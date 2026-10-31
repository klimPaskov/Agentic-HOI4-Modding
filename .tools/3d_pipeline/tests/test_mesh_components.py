"""Loose-component counting and the worker's topology metrics that feed the candidate gate.

The worker functions are AST-loaded against bmesh-shaped doubles, so this proves
the counting and aggregation logic, not Blender's own mesh behavior.
"""

from __future__ import annotations

import ast
import importlib.util
import math
import types
import unittest
from pathlib import Path


PIPELINE_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_ROOT = PIPELINE_ROOT / "adapter"
WORKER = ADAPTER_ROOT / "blender_worker.py"
_SPEC = importlib.util.spec_from_file_location("mesh_components", ADAPTER_ROOT / "mesh_components.py")
mesh_components = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mesh_components)
count_connected_components = mesh_components.count_connected_components
TREE = ast.parse(WORKER.read_text(encoding="utf-8"))


def load_worker_functions(names: set[str], namespace: dict) -> dict:
    nodes = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
    nodes += [node for node in TREE.body if isinstance(node, ast.FunctionDef) and node.name in names]
    module = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    namespace = {"Any": object, "Dict": dict, "List": list, "Optional": object, "math": math, **namespace}
    exec(compile(module, str(WORKER), "exec"), namespace)
    return namespace


class CountConnectedComponentsTests(unittest.TestCase):
    def test_counts_pieces_of_a_graph(self) -> None:
        cases = {
            "empty": (0, [], 0),
            "isolated vertices": (4, [], 4),
            "one chain": (4, [(0, 1), (1, 2), (2, 3)], 1),
            "two triangles": (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)], 2),
            "ring plus a stray vertex": (5, [(0, 1), (1, 2), (2, 3), (3, 0)], 2),
            "repeated edges change nothing": (3, [(0, 1), (1, 0), (0, 1)], 2),
            "a bridge merges two shells": (6, [(0, 1), (1, 2), (3, 4), (4, 5), (2, 3)], 1),
        }
        for name, (vertices, edges, expected) in cases.items():
            with self.subTest(name=name):
                self.assertEqual(count_connected_components(vertices, edges), expected)

    def test_bad_input_is_an_error_not_a_miscount(self) -> None:
        with self.assertRaises(ValueError):
            count_connected_components(-1, [])
        for edge in ((0, 3), (-1, 0), (5, 5)):
            with self.subTest(edge=edge), self.assertRaises(ValueError):
                count_connected_components(3, [edge])


class FakeVertex:
    def __init__(self, index: int) -> None:
        self.index = index


class FakeEdge:
    def __init__(self, first: FakeVertex, second: FakeVertex, faces: int) -> None:
        self.verts = (first, second)
        self.link_faces = [object()] * faces

    def calc_length(self) -> float:
        return 1.0


class FakeFace:
    def __init__(self, vertices: list[FakeVertex]) -> None:
        self.verts = vertices

    def calc_area(self) -> float:
        return 0.5

    normal = types.SimpleNamespace(length=1.0)


class FakeVerts(list):
    def index_update(self) -> None:
        for position, vertex in enumerate(self):
            vertex.index = position


def triangles_bmesh(pieces: int, stray_vertices: int = 0) -> types.SimpleNamespace:
    verts = FakeVerts()
    edges, faces = [], []
    for _ in range(pieces):
        corner = [FakeVertex(len(verts) + step) for step in range(3)]
        verts.extend(corner)
        edges += [FakeEdge(corner[step], corner[(step + 1) % 3], 1) for step in range(3)]
        faces.append(FakeFace(corner))
    verts.extend(FakeVertex(len(verts) + step) for step in range(stray_vertices))
    return types.SimpleNamespace(verts=verts, edges=edges, faces=faces)


class TopologyMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.namespace = load_worker_functions(
            {"topology_metrics_from_bmesh"}, {"count_connected_components": count_connected_components}
        )

    def test_topology_metrics_report_the_number_of_loose_components(self) -> None:
        metrics = self.namespace["topology_metrics_from_bmesh"](triangles_bmesh(pieces=1))
        self.assertEqual(metrics["loose_component_count"], 1)
        two = self.namespace["topology_metrics_from_bmesh"](triangles_bmesh(pieces=2))
        self.assertEqual(two["loose_component_count"], 2)
        self.assertEqual(two["triangles"], 2)
        self.assertEqual(two["loose_boundary_edges"], 6)

    def test_a_vertex_with_no_edges_is_its_own_component(self) -> None:
        metrics = self.namespace["topology_metrics_from_bmesh"](triangles_bmesh(pieces=1, stray_vertices=2))
        self.assertEqual(metrics["loose_component_count"], 3)

    def test_stale_vertex_indices_do_not_change_the_count(self) -> None:
        bm = triangles_bmesh(pieces=2)
        for vertex in bm.verts:
            vertex.index = 0
        self.assertEqual(self.namespace["topology_metrics_from_bmesh"](bm)["loose_component_count"], 2)


class GeometryMetricsAggregationTests(unittest.TestCase):
    def test_object_loose_components_are_summed_into_the_candidate_metrics(self) -> None:
        def make_object(name: str) -> types.SimpleNamespace:
            return types.SimpleNamespace(
                name=name,
                scale=(1.0, 1.0, 1.0),
                data=types.SimpleNamespace(
                    vertices=[0, 1, 2],
                    polygons=[types.SimpleNamespace(vertices=[0, 1, 2])],
                    uv_layers=[],
                ),
                get=lambda key, default=None: True,
            )

        objects = [make_object("Body"), make_object("Cape")]
        per_object = {
            "Body": {"loose_component_count": 2},
            "Cape": {"loose_component_count": 1},
        }
        base = {
            "loose_boundary_edges": 0,
            "non_manifold_edges": 0,
            "degenerate_faces": 0,
            "zero_length_normals": 0,
            "boundary_component_count": 0,
            "closed_boundary_component_count": 0,
            "branched_boundary_component_count": 0,
            "max_boundary_component_edges": 0,
        }

        class Point(tuple):
            def __sub__(self, other: "Point") -> "Point":
                return Point(a - b for a, b in zip(self, other))

        namespace = load_worker_functions(
            {"geometry_metrics"},
            {
                "mesh_objects": lambda working_only=True: objects,
                "geometry_metrics_for_object": lambda obj: {**base, **per_object[obj.name]},
                "world_bounds": lambda meshes: (Point((0, 0, 0)), Point((1, 2, 3))),
                "bpy": types.SimpleNamespace(context=types.SimpleNamespace(scene=types.SimpleNamespace(objects=objects))),
            },
        )
        metrics = namespace["geometry_metrics"]()
        self.assertEqual(metrics["loose_component_count"], 3)
        self.assertEqual(metrics["objects"], 2)
        self.assertEqual(metrics["triangles"], 2)
        self.assertEqual(metrics["dimensions"], [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
