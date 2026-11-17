"""Delighting for Tripo colour textures of static models: lift cast shadows that were painted into the texture.

Tripo's texture model sometimes paints a shadow into the colour map, for example a hard dark band across a roof where a
chimney "casts" one. The shadow points one way for ever, and the game's light will contradict it. The route lifts it
(`delight`) and its check (`shadow_findings`) fails a model whose texture still has one.

The rule works per facet group: a run of triangles that share edges and face the same way (a roof plane, a wall), drawn
into texture space with the model's UVs. Inside a group a cast shadow is a region that is

- much darker than the group's median (`DARK_RATIO`), after smoothing away mortar lines and grain,
- large: it keeps its shape under an opening by `OPEN_SHARE` of the group's side and covers `AREA_SHARE` of the
  group (windows, doors, vents and weathering streaks are small against a wall or a roof),
- long: it runs across its surface (`SPAN_SHARE`), where a stain or corner darkening is a blob,
- sharp-edged (`SHARP_SHARE`), because weathering and ambient occlusion fade, and
- the same colour family as the group around it (a shadow darkens a surface, it does not turn it grey: a door in
  a brick wall has another chromaticity and is left alone).

Every limit is a share of the group or a ratio of its median, so none depends on one model. The lift divides the
shadow's low-frequency brightness out per channel and puts the surrounding low-frequency brightness in, so the
detail inside the shadow (bricks, slates) stays.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

DARK_RATIO = 0.65  # a shadow's smoothed luminance is below this share of its group's median (a hard shadow takes a third or more)
LOOSE_RATIO = 0.85  # the region grows out to this share (the penumbra), seeded by the dark core
SHARP_SHARE = 0.035  # a cast shadow's edge goes from lit to dark within this share of the group's side (weathering fades slowly)
OPEN_SHARE = 0.02  # the core survives an opening by this share of the group's side (grain and mortar do not)
AREA_SHARE = 0.04  # a cast shadow covers at least this share of its group
FAIL_SHARE = 0.05  # the check fails a texture with a region this large (looser than the lift, so the margin is real)
SPAN_SHARE = 0.4  # a cast shadow runs across its surface: its longest extent is this share of the group's (corner darkening and stains are blobs)
CHROMA_TOLERANCE = 0.035  # the shadow's red, green and blue shares differ from the group's by at most this
MIN_GROUP_SHARE = 0.015  # groups smaller than this share of the texture are detail (a door, a sill), not surfaces
NORMAL_DEGREES = 10.0  # a facet group's triangles lean at most this from the group's first triangle
ANALYSIS_SIZE = 1024  # the largest side the rule works at; the final textures are smaller

LUMA = np.array([0.299, 0.587, 0.114])


def facet_labels(positions: np.ndarray, triangles: np.ndarray, degrees: float = NORMAL_DEGREES) -> np.ndarray:
    """One label per triangle: grown from the largest unlabelled triangle over shared edges, each member within
    `degrees` of the seed's normal. A vertex index shared by two triangles is an edge or a corner of one UV island."""

    p = np.asarray(positions, dtype=float)
    t = np.asarray(triangles, dtype=np.int64)
    cross = np.cross(p[t[:, 1]] - p[t[:, 0]], p[t[:, 2]] - p[t[:, 0]])
    area = np.linalg.norm(cross, axis=1)
    normal = cross / np.maximum(area[:, None], 1e-18)
    edges: Dict[Tuple[int, int], List[int]] = {}
    for index, tri in enumerate(t):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            key = (int(min(tri[a], tri[b])), int(max(tri[a], tri[b])))
            edges.setdefault(key, []).append(index)
    neighbours: List[List[int]] = [[] for _ in range(len(t))]
    for pair in edges.values():
        for i in pair:
            neighbours[i].extend(j for j in pair if j != i)
    limit = np.cos(np.radians(degrees))
    labels = np.full(len(t), -1, dtype=np.int64)
    count = 0
    for seed in np.argsort(-area):
        if labels[seed] >= 0 or area[seed] <= 1e-18:
            continue
        labels[seed] = count
        queue = deque([seed])
        while queue:
            current = queue.popleft()
            for other in neighbours[current]:
                if labels[other] < 0 and float(normal[seed] @ normal[other]) >= limit:
                    labels[other] = count
                    queue.append(other)
        count += 1
    labels[labels < 0] = count  # degenerate triangles carry no surface
    return labels


def group_map(uv: np.ndarray, triangles: np.ndarray, labels: np.ndarray, size: int) -> np.ndarray:
    """(size, size) int map of the facet group under each texel (row = v * size, as glTF and PDX store v), -1 outside."""

    canvas = Image.new("I", (size, size), -1)
    draw = ImageDraw.Draw(canvas)
    uv = np.asarray(uv, dtype=float)
    for tri, label in zip(np.asarray(triangles), labels):
        pts = [(float(uv[i][0]) * size, float(uv[i][1]) * size) for i in tri]
        draw.polygon(pts, fill=int(label))
    return np.asarray(canvas, dtype=np.int64)


def _blur_normalised(values: np.ndarray, weight: np.ndarray, sigma: float) -> Tuple[np.ndarray, np.ndarray]:
    """Gaussian average of `values` over `weight` (normalised convolution) and the blurred weight."""

    sigma = max(float(sigma), 0.8)
    w = ndimage.gaussian_filter(weight.astype(float), sigma)
    if values.ndim == 3:
        v = np.stack([ndimage.gaussian_filter(values[..., c] * weight, sigma) for c in range(values.shape[2])], axis=-1)
        return v / np.maximum(w, 1e-6)[..., None], w
    return ndimage.gaussian_filter(values * weight, sigma) / np.maximum(w, 1e-6), w


def _disk(radius: int) -> np.ndarray:
    y, x = np.ogrid[-radius : radius + 1, -radius : radius + 1]
    return (x * x + y * y) <= radius * radius


def shadow_regions(rgb: np.ndarray, groups: np.ndarray, area_share: float = AREA_SHARE) -> List[dict]:
    """The cast-shadow regions of a texture: {group, share (of the group), median_ratio, mask, loose} each.

    `rgb` is a float array (h, w, 3) in 0..255, `groups` the group_map at the same size."""

    height, width = groups.shape
    luma = rgb @ LUMA
    total = float(height * width)
    found: List[dict] = []
    for label in np.unique(groups):
        if label < 0:
            continue
        member = groups == label
        count = int(member.sum())
        if count < MIN_GROUP_SHARE * total:
            continue
        side = float(np.sqrt(count))
        smooth_sigma = max(1.0, 0.008 * side)
        smooth, _ = _blur_normalised(luma, member, smooth_sigma)
        reference = float(np.median(smooth[member]))
        if reference < 8.0:
            continue
        dark = member & (smooth < DARK_RATIO * reference)
        radius = max(1, int(round(OPEN_SHARE * side)))
        core = ndimage.binary_opening(dark, structure=_disk(radius))
        if not core.any():
            continue
        loose = member & (smooth < LOOSE_RATIO * reference)
        regions, n = ndimage.label(loose)
        seeds = np.unique(regions[core])
        for seed in seeds[seeds > 0]:
            region = regions == seed
            share = float(region.sum()) / count
            if share < area_share:
                continue
            ys, xs = np.nonzero(region)
            gy, gx = np.nonzero(member)
            reach = max(np.ptp(xs), np.ptp(ys)) + 1
            if reach < SPAN_SHARE * (max(np.ptp(gx), np.ptp(gy)) + 1):
                continue
            around = member & ~ndimage.binary_dilation(region, structure=_disk(max(2, radius)))
            if int(around.sum()) < 0.05 * count:
                continue  # nothing left to compare it with: the whole group is the dark thing
            chroma_in = rgb[region].mean(axis=0)
            chroma_out = rgb[around].mean(axis=0)
            c_in = chroma_in / max(float(chroma_in.sum()), 1e-6)
            c_out = chroma_out / max(float(chroma_out.sum()), 1e-6)
            if float(np.abs(c_in - c_out).max()) > CHROMA_TOLERANCE:
                continue
            edge = region & ~ndimage.binary_erosion(region)
            gradient = np.hypot(ndimage.sobel(smooth, axis=0), ndimage.sobel(smooth, axis=1)) / 8.0
            step = float(np.median(smooth[around])) - float(np.median(smooth[region]))
            width = step / max(float(np.median(gradient[edge])), 1e-6)
            if width > SHARP_SHARE * side:
                continue  # a soft fade is weathering or ambient occlusion, not a cast shadow
            found.append({"group": int(label), "share": share, "median_ratio": float(np.median(smooth[region])) / reference, "width_share": width / side,
                          "mask": region, "around": around})
    return found


def _lift(rgb: np.ndarray, groups: np.ndarray, regions: List[dict]) -> np.ndarray:
    """The texture with each region's low-frequency brightness replaced by its surroundings', detail kept."""

    out = rgb.copy()
    for region in regions:
        member = groups == region["group"]
        side = float(np.sqrt(member.sum()))
        mask = region["mask"]
        inside, _ = _blur_normalised(rgb, mask, max(2.0, 0.05 * side))
        outside, _ = _blur_normalised(rgb, region["around"], max(3.0, 0.1 * side))
        gain = np.clip(outside / np.maximum(inside, 4.0), 1.0, 6.0)
        grown = ndimage.binary_dilation(mask, structure=_disk(max(2, int(round(0.03 * side)))))
        feather = np.clip(ndimage.gaussian_filter(grown.astype(float), max(1.0, 0.015 * side)) * 1.6, 0.0, 1.0)
        feather *= ndimage.binary_dilation(member, iterations=1)
        out = out * (1.0 + (gain - 1.0) * feather[..., None])
    return np.clip(out, 0, 255)


def delight(image: Image.Image, groups: np.ndarray) -> Tuple[Image.Image, dict]:
    """(the lifted texture, a report). `groups` is the group_map at any size: it is resampled to the working size."""

    work = min(ANALYSIS_SIZE, image.width)
    base = image.convert("RGB").resize((work, work), Image.Resampling.LANCZOS) if image.width != work else image.convert("RGB")
    if groups.shape[0] != work:
        groups = np.asarray(Image.fromarray(groups.astype(np.int32), "I").resize((work, work), Image.Resampling.NEAREST), dtype=np.int64)
    rgb = np.asarray(base, dtype=float)
    regions = shadow_regions(rgb, groups)
    report = {"size": work, "regions": [{"group": r["group"], "share": round(r["share"], 4), "median_ratio": round(r["median_ratio"], 3)} for r in regions]}
    if not regions:
        return base, report
    lifted = _lift(rgb, groups, regions)
    after = shadow_regions(lifted, groups)
    report["left"] = [{"group": r["group"], "share": round(r["share"], 4)} for r in after]
    return Image.fromarray(np.uint8(np.round(lifted)), "RGB"), report


HOLE_PERCENTILE = 5.0  # a hole's colour: the darkest twentieth of the texels the model uses
HOLE_SIZE = 256  # the side the dark patch is looked for at (the final textures' small mip levels)


def hole_uv(image: Image.Image, groups: np.ndarray) -> dict:
    """Where in the atlas a hole's dark interior is: the texel deepest inside the largest patch of the darkest texels
    (`HOLE_PERCENTILE`) that the model's faces cover, so the colour holds when the texture is mipmapped. A face given
    this UV at every corner is one flat dark colour, as the inside of a turret ring blown open.

    `groups` is the group_map (any size, -1 off the model). Returns {"uv": [u, v] (glTF, v down), "luma", "ratio" (of
    the covered texels' median), "depth" (texels at HOLE_SIZE)}."""

    rgb = np.asarray(image.convert("RGB").resize((HOLE_SIZE, HOLE_SIZE), Image.Resampling.BOX), dtype=float)
    covered = np.asarray(Image.fromarray(groups.astype(np.int32), "I").resize((HOLE_SIZE, HOLE_SIZE), Image.Resampling.NEAREST), dtype=np.int64) >= 0
    luma = rgb @ LUMA
    if not covered.any():
        covered = np.ones_like(covered)
    dark = covered & (luma <= np.percentile(luma[covered], HOLE_PERCENTILE))
    depth = ndimage.distance_transform_edt(dark)
    y, x = np.unravel_index(int(np.argmax(depth)), depth.shape)
    return {"uv": [float((x + 0.5) / HOLE_SIZE), float((y + 0.5) / HOLE_SIZE)], "luma": round(float(luma[y, x]), 1),
            "ratio": round(float(luma[y, x]) / max(float(np.median(luma[covered])), 1e-6), 3), "depth": round(float(depth[y, x]), 1)}


# glTF and PDX readers ---------------------------------------------------------------------------------------------

def glb_uv_geometry(path: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(positions, uv, triangles) of every mesh of a GLB, placed by its nodes. UV is glTF's (v down)."""

    from lib import static_kinds as sk
    from lib.texture_lineage import _read_glb

    document, binary = _read_glb(Path(path))
    positions, uvs, triangles = [], [], []
    offset = 0

    def visit(index: int, parent: np.ndarray) -> None:
        nonlocal offset
        node = document["nodes"][index]
        world = parent @ sk._node_matrix(node)
        if "mesh" in node:
            for primitive in document["meshes"][node["mesh"]]["primitives"]:
                if primitive.get("mode", 4) != 4 or "TEXCOORD_0" not in primitive["attributes"]:
                    continue
                p = sk._accessor(document, binary, primitive["attributes"]["POSITION"]).astype(float)
                positions.append(p @ world[:3, :3].T + world[:3, 3])
                uvs.append(sk._accessor(document, binary, primitive["attributes"]["TEXCOORD_0"]).astype(float))
                t = sk._accessor(document, binary, primitive["indices"]).reshape(-1, 3).astype(np.int64) if "indices" in primitive else np.arange(len(p)).reshape(-1, 3)
                triangles.append(t + offset)
                offset += len(p)
        for child in node.get("children", []):
            visit(child, world)

    scene = document.get("scenes", [{}])[document.get("scene", 0)]
    for root in scene.get("nodes", range(len(document.get("nodes", [])))):
        visit(root, np.eye(4))
    return np.concatenate(positions), np.concatenate(uvs), np.concatenate(triangles)


def glb_groups(path: Path, size: int) -> np.ndarray:
    positions, uv, triangles = glb_uv_geometry(path)
    return group_map(uv, triangles, facet_labels(positions, triangles), size)


def mesh_uv_geometry(mesh_path: Path, diffuse: Optional[str] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(positions, uv, triangles) of the rendered streams of a PDX mesh (collision shapes left out). With `diffuse` (a
    file name), only the streams whose material names that colour texture, or names none: a tank's track runs are a
    second stream on their own tread texture, and their UVs mean nothing on the atlas."""

    from lib import pdx_binary

    objects = pdx_binary.read(mesh_path).child("object")
    positions, uvs, triangles, offset = [], [], [], 0
    for shape in objects.children:
        for stream in (n for n in shape.children if n.name == "mesh"):
            material = stream.child("material")
            shader = (material.properties.get("shader") or [""])[0] if material is not None else ""
            if str(shader).lower() == "collision":
                continue
            named = (material.properties.get("diff") or [None])[0] if material is not None else None
            if diffuse is not None and named is not None and str(named).lower() != diffuse.lower():
                continue
            p = np.asarray(stream.properties.get("p", []), dtype=float).reshape(-1, 3)
            u = np.asarray(stream.properties.get("u0", []), dtype=float).reshape(-1, 2)
            if len(u) != len(p) or not len(p):
                continue
            positions.append(p)
            uvs.append(u)
            triangles.append(np.asarray(stream.properties.get("tri", []), dtype=np.int64).reshape(-1, 3) + offset)
            offset += len(p)
    if not positions:
        return np.zeros((0, 3)), np.zeros((0, 2)), np.zeros((0, 3), dtype=np.int64)
    return np.concatenate(positions), np.concatenate(uvs), np.concatenate(triangles)


def shadow_findings(mesh_path: Path, diffuse_path: Path) -> List[Tuple[str, str, str]]:
    """STATIC-SHADOW: the exported model's colour texture still has a cast-shadow region over `FAIL_SHARE` of a facet
    group. (rule, severity, message) for each."""

    if not Path(diffuse_path).is_file():
        return []
    positions, uv, triangles = mesh_uv_geometry(mesh_path, Path(diffuse_path).name)
    if not len(triangles):
        return []
    with Image.open(diffuse_path) as opened:
        image = opened.convert("RGB")
    work = min(ANALYSIS_SIZE, image.width)
    if image.width != work:
        image = image.resize((work, work), Image.Resampling.LANCZOS)
    groups = group_map(uv, triangles, facet_labels(positions, triangles), work)
    regions = shadow_regions(np.asarray(image, dtype=float), groups, FAIL_SHARE)
    return [("STATIC-SHADOW", "error",
             f"the colour texture has a cast shadow: a region {100 * r['share']:.0f} % of one facet group's area, at {r['median_ratio']:.2f} of the group's median brightness "
             f"(the game's light will contradict a painted shadow; lift it with the route's delighting or make the texture from a picture lit without cast shadows)")
            for r in regions]


# The ring seam: the band round a tank's turret ring ------------------------------------------------------------------

SEAM_INNER = 0.85  # the seam band runs from this share of the ring's radius ...
SEAM_OUTER = 1.5  # ... to this share, measured sideways from the turret's axis
SEAM_BELOW = 0.3  # of the turret's height below its cut, the band's lowest part (the hull roof and the slope round the sunk ring)
SEAM_ABOVE = 0.1  # of the turret's height above its cut, the band's highest part (the turret wall's foot)
SEAM_REFERENCE = 2.6  # the roof the band is matched to lies out to this share of the ring's radius
SEAM_LUMA = 0.12  # a band texel is off the roof's colour when it is this share brighter or darker than the roof's median ...
SEAM_CHROMA = 0.025  # ... or its colour shares (red, green, blue over their sum) differ from the roof's by more than this


def _triangle_mask(uv: np.ndarray, triangles: np.ndarray, size: int) -> np.ndarray:
    canvas = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(canvas)
    for tri in np.asarray(triangles):
        draw.polygon([(float(uv[i][0]) * size, float(uv[i][1]) * size) for i in tri], fill=255)
    return np.asarray(canvas) > 0


def _texel_points(uv: np.ndarray, positions: np.ndarray, triangles: np.ndarray, size: int) -> Tuple[np.ndarray, np.ndarray]:
    """(a `size` x `size` grid of the model's 3D point under each texel centre, which texels a triangle covers). A big
    roof triangle's few texels span a long stretch of the model, so the point under a texel, not the triangle's centre,
    says where on the model a texel is."""

    points = np.zeros((size, size, 3))
    covered = np.zeros((size, size), dtype=bool)
    uv = np.asarray(uv, dtype=float)
    positions = np.asarray(positions, dtype=float)
    for tri in np.asarray(triangles):
        a, b, c = (uv[i] * size for i in tri)
        low = np.maximum(np.floor(np.minimum(np.minimum(a, b), c) - 0.5).astype(int), 0)
        high = np.minimum(np.ceil(np.maximum(np.maximum(a, b), c) + 0.5).astype(int), size - 1)
        det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(det) < 1e-12 or high[0] < low[0] or high[1] < low[1]:
            continue
        xs, ys = np.meshgrid(np.arange(low[0], high[0] + 1) + 0.5, np.arange(low[1], high[1] + 1) + 0.5)
        w0 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / det
        w1 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / det
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
        if not inside.any():
            continue
        a3, b3, c3 = positions[tri[0]], positions[tri[1]], positions[tri[2]]
        xi, yi = xs[inside].astype(int), ys[inside].astype(int)
        points[yi, xi] = w0[inside, None] * a3 + w1[inside, None] * b3 + w2[inside, None] * c3
        covered[yi, xi] = True
    return points, covered


def _off_roof(rgb: np.ndarray, median: np.ndarray) -> np.ndarray:
    """Which texels (rows of `rgb`) are off the roof's colour: brighter or darker than `SEAM_LUMA` or another colour family."""

    luma = rgb @ LUMA / max(float(median @ LUMA), 1e-6)
    share = rgb / np.maximum(rgb.sum(axis=1, keepdims=True), 1.0)
    chroma = np.abs(share - median / max(float(median.sum()), 1.0)).max(axis=1)
    return (np.abs(luma - 1.0) > SEAM_LUMA) | (chroma > SEAM_CHROMA)


def ring_seam(image: Image.Image, uv: np.ndarray, positions: np.ndarray, triangles: np.ndarray, cut_z: float, top_z: float,
              centre: np.ndarray, radius: float) -> Tuple[Image.Image, dict]:
    """(the texture with the ring's seam band matched to the roof, a report). Tripo paints the sunk ring's band, which a
    turret hides, in whatever colour it likes: a bright yellow-green halo round the turret on the hull roof. The band is
    every triangle whose centre lies between `SEAM_INNER` and `SEAM_OUTER` of the ring's radius from the turret's axis and
    between `SEAM_BELOW` under the cut and `SEAM_ABOVE` over it (shares of the turret's height). The roof is the same
    heights farther out (to `SEAM_REFERENCE`). A band texel off the roof's median colour (`_off_roof`) takes the median,
    brightened or darkened by its own deviation within the same tolerance, so grain and rivets stay. The report holds the
    share of band texels off the roof's colour before and after."""

    work = min(ANALYSIS_SIZE, image.width)
    base = image.convert("RGB").resize((work, work), Image.Resampling.LANCZOS) if image.width != work else image.convert("RGB")
    rgb = np.asarray(base, dtype=float)
    height = max(top_z - cut_z, 1e-9)
    corners = np.asarray(positions)[np.asarray(triangles)]
    middle = corners.mean(axis=1)
    sideways = np.linalg.norm(middle[:, :2] - np.asarray(centre)[:2], axis=1) / max(radius, 1e-9)
    high = (middle[:, 2] <= cut_z + SEAM_ABOVE * height) & (middle[:, 2] >= cut_z - SEAM_BELOW * height)
    band = high & (sideways >= SEAM_INNER) & (sideways <= SEAM_OUTER)
    roof = high & (sideways > SEAM_OUTER) & (sideways <= SEAM_REFERENCE)
    report = {"band_triangles": int(band.sum()), "roof_triangles": int(roof.sum())}
    if band.sum() < 3 or roof.sum() < 3:
        report["skipped"] = "too few triangles in the seam band or the roof round it"
        return base, report
    band_mask = _triangle_mask(uv, np.asarray(triangles)[band], work)
    roof_mask = _triangle_mask(uv, np.asarray(triangles)[roof], work) & ~band_mask
    # A triangle is judged by its centre above, but a big roof triangle (a few texels over a long stretch of roof) can have
    # its edge along the ring while its centre lies far out: the texels whose own point on the model lies in the band
    # belong to the band, wherever their triangle's centre is (the bright arc outside a tank's turret base).
    points, covered = _texel_points(uv, positions, triangles, work)
    texel_side = np.linalg.norm(points[..., :2] - np.asarray(centre)[:2], axis=2) / max(radius, 1e-9)
    texel_high = (points[..., 2] <= cut_z + SEAM_ABOVE * height) & (points[..., 2] >= cut_z - SEAM_BELOW * height)
    texel_band = covered & texel_high & (texel_side >= SEAM_INNER) & (texel_side <= SEAM_OUTER)
    texel_roof = covered & texel_high & (texel_side > SEAM_OUTER) & (texel_side <= SEAM_REFERENCE)
    report["band_texels_from_points"] = int((texel_band & ~band_mask).sum())
    band_mask = band_mask | texel_band
    roof_mask = (roof_mask | texel_roof) & ~band_mask
    if band_mask.sum() < 4 or roof_mask.sum() < 4:
        report["skipped"] = "the seam band or the roof round it has no texels"
        return base, report
    median = np.median(rgb[roof_mask], axis=0)
    off = _off_roof(rgb[band_mask], median)
    report.update({"texels": int(band_mask.sum()), "roof_median": [round(float(v), 1) for v in median], "off_before": round(float(off.mean()), 4)})
    # the roof's own scatter sets what the roof counts as normal: a band no wilder than the roof round it is left alone
    roof_off = float(_off_roof(rgb[roof_mask], median).mean())
    report["off_roof"] = round(roof_off, 4)
    if float(off.mean()) <= roof_off + 0.02:
        report["off_after"] = report["off_before"]
        return base, report
    texels = rgb[band_mask]
    luma = np.clip(texels @ LUMA / max(float(median @ LUMA), 1e-6), 1.0 - 0.75 * SEAM_LUMA, 1.0 + 0.5 * SEAM_LUMA)
    matched = median[None, :] * luma[:, None]
    mix = off.astype(float)[:, None]
    fixed = rgb.copy()
    fixed[band_mask] = texels * (1.0 - mix) + matched * mix
    report["off_after"] = round(float(_off_roof(fixed[band_mask], median).mean()), 4)
    return Image.fromarray(np.uint8(np.round(np.clip(fixed, 0, 255))), "RGB"), report


# Contrast: a flat Tripo texture against vanilla's ---------------------------------------------------------------------

CONTRAST_MAX_GAIN = 1.5  # the lift never stretches the brightness spread by more than this (a moderate lift, not a repaint)
CONTRAST_HEIGHT = 0.15  # of its brightness, the most a texel is darkened at the model's foot or lightened at its top
CONTRAST_SIZE = 256  # the side the texture's spread is measured at


def luma_spread(rgb: np.ndarray, covered: np.ndarray) -> float:
    """The brightness spread of the texels the model uses: their standard deviation over their mean (`rgb` is the
    texture, `covered` the texels some face uses)."""

    luma = (np.asarray(rgb, dtype=float) @ LUMA)[covered]
    return float(luma.std() / max(float(luma.mean()), 1e-6)) if luma.size else 0.0


def covered_texels(uv: np.ndarray, triangles: np.ndarray, size: int) -> np.ndarray:
    return group_map(uv, triangles, np.zeros(len(triangles), dtype=np.int64), size) >= 0


def texture_spread(image: Image.Image, uv: np.ndarray, triangles: np.ndarray) -> float:
    """`luma_spread` of a colour texture at `CONTRAST_SIZE`, over the texels the faces' UVs cover."""

    rgb = np.asarray(image.convert("RGB").resize((CONTRAST_SIZE, CONTRAST_SIZE), Image.Resampling.BOX), dtype=float)
    return luma_spread(rgb, covered_texels(uv, triangles, CONTRAST_SIZE))


def _height_map(uv: np.ndarray, heights: np.ndarray, triangles: np.ndarray, size: int) -> np.ndarray:
    """(size, size) height of the surface under each texel (NaN where no face is), interpolated across each triangle."""

    out = np.full((size, size), np.nan)
    pixels = np.asarray(uv, dtype=float) * size
    for tri in np.asarray(triangles):
        a, b, c = pixels[tri]
        x0, x1 = int(max(np.floor(min(a[0], b[0], c[0])), 0)), int(min(np.ceil(max(a[0], b[0], c[0])), size - 1))
        y0, y1 = int(max(np.floor(min(a[1], b[1], c[1])), 0)), int(min(np.ceil(max(a[1], b[1], c[1])), size - 1))
        if x1 < x0 or y1 < y0:
            continue
        det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(det) < 1e-9:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        w0 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / det
        w1 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / det
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)
        value = w0 * heights[tri[0]] + w1 * heights[tri[1]] + w2 * heights[tri[2]]
        block = out[y0:y1 + 1, x0:x1 + 1]
        block[inside] = value[inside]
    return out


def contrast_lift(image: Image.Image, uv: np.ndarray, heights: np.ndarray, triangles: np.ndarray, target: float) -> Tuple[Image.Image, dict]:
    """(the texture with its brightness spread lifted to `target`, a report). Tripo's colour maps are flatter than vanilla's
    (a light tank's texture spreads its brightness by 0.43 to 0.64 of the mean, a Smart Mesh tank's by under 0.2), so at map
    size the model is a flat slab. The lift stretches the brightness about its median by `target` over the measured spread
    (at most `CONTRAST_MAX_GAIN`, colour kept), then darkens the foot of the model and lightens its top by up to
    `CONTRAST_HEIGHT`, the way vanilla's light falls on a tank. `heights` is one value per vertex. A texture at or over the
    target is left as it is."""

    work = min(ANALYSIS_SIZE, image.width)
    base = image.convert("RGB").resize((work, work), Image.Resampling.LANCZOS) if image.width != work else image.convert("RGB")
    rgb = np.asarray(base, dtype=float)
    covered = covered_texels(uv, triangles, work)
    before = luma_spread(rgb, covered)
    report = {"spread_before": round(before, 3), "target": round(float(target), 3)}
    if before >= target or not covered.any():
        report["spread_after"] = report["spread_before"]
        return base, report
    luma = rgb @ LUMA
    median = float(np.median(luma[covered]))
    gain = float(min(CONTRAST_MAX_GAIN, target / max(before, 1e-6)))
    stretched = median + (luma - median) * gain
    span = max(float(np.ptp(heights)), 1e-9)
    height = _height_map(uv, (heights - float(heights.min())) / span, triangles, work)
    ramp = 1.0 + CONTRAST_HEIGHT * (2.0 * np.nan_to_num(height, nan=0.5) - 1.0)
    wanted = np.clip(stretched, 4.0, 250.0) * ramp
    scale = np.where(covered, np.clip(wanted / np.maximum(luma, 4.0), 0.4, 2.5), 1.0)
    fixed = np.clip(rgb * scale[..., None], 0, 255)
    report.update({"gain": round(gain, 3), "spread_after": round(luma_spread(fixed, covered), 3)})
    return Image.fromarray(np.uint8(np.round(fixed)), "RGB"), report
