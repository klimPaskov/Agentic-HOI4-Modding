"""Canonical image-provider catalog inserted into the published manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coding_environment_data import MCP_ROUTE_CLIENTS  # noqa: E402

ALL_CLIENTS = list(MCP_ROUTE_CLIENTS)
TEXT_SOURCE_SUFFIXES = {".js", ".json", ".md", ".py", ".txt"}


def _route(provider_id: str, auth: str, *, kind: str = "stdio_adapter", component: str | None = None,
           source_repository: str | None = None, source_revision: str | None = None,
           package_name: str | None = None, package_version: str | None = None,
           package_tree_sha256: str | None = None, runtime_entry: str | None = None,
           tools: dict[str, str] | None = None, tool_arguments: dict | None = None,
           supported_models: list[str] | None = None,
           result_format: str | None = None, primary_environment: str | None = None) -> dict:
    return {
        "kind": kind,
        "auth_method": auth,
        "server_id": f"hoi4_image_{provider_id}" if kind not in {"native", "manual"} else None,
        "url": None,
        "component_id": component if component is not None else ("imagegen.runtime" if kind == "stdio_adapter" else None),
        "source_repository": source_repository,
        "source_revision": source_revision,
        "package_name": package_name,
        "package_version": package_version,
        "package_tree_sha256": package_tree_sha256,
        "source_tree_sha256": None,
        "package_lock_sha256": None,
        "runtime_entry": runtime_entry or (".tools/image_generation/runtime/server.py" if kind == "stdio_adapter" else None),
        "tool_names": tools if tools is not None else {
            "generate": "generate_image",
            "edit": "edit_image",
            "background_removal": "remove_background",
            "auth_status": "image_auth_status",
        },
        "supported_models": supported_models or [],
        "tool_arguments": tool_arguments if tool_arguments is not None else {
            "prompt": "prompt",
            "output_path": "out",
            "reference_images": "reference_images",
            "reference_image": "image",
            "width": "width",
            "height": "height",
            "transparent_background": "transparent_background",
        },
        "required_environment_names": [],
        "auth_headers": [],
        "api_protocol": None,
        "api_base_url": None,
        "default_model": None,
        "result_format": result_format or ("manual" if kind == "manual" else "png"),
        "credential_fields": [],
        "requires_primary_coding_environment": primary_environment,
    }


def _capabilities(*, references: bool, edits: bool, alpha: bool,
                  width: int | None = None, height: int | None = None,
                  maximum_pixels: int | None = None, reference_limit: int | None = None,
                  accepts_dimensions: bool = False, size_notes: str = "", reference_notes: str = "",
                  alpha_notes: str = "", edit_fallback: str = "",
                  background_removal: bool = False) -> dict:
    return {
        "reference_images": {
            "supported": references,
            "max_count": reference_limit,
            "notes": reference_notes or "Limits depend on the selected model.",
        },
        "image_edits": edits,
        "background_removal": background_removal,
        "transparent_background": {
            "native": alpha,
            "request_parameter": "transparent_background" if alpha else None,
            "notes": alpha_notes or ("Request a transparent PNG when supported and verify its alpha." if alpha else "Native alpha is not documented for this route."),
        },
        "size_limits": {
            "accepts_dimensions": accepts_dimensions,
            "maximum_width_px": width,
            "maximum_height_px": height,
            "maximum_pixels": maximum_pixels,
            "notes": size_notes or (
                "Use dimensions supported by the selected model."
                if accepts_dimensions else "This route uses the model's default image size; limits can vary by model."
            ),
        },
        "one_image_per_call": True,
        "alpha_verification": "Open the saved PNG and check its alpha channel before treating it as transparent.",
        "fallback_if_no_alpha": "Use a selected background-removal route and verify alpha; if none is configured, ask the maintainer for another route.",
        "fallback_if_no_edits": edit_fallback or "Make a new image from the reference if that fits, or choose another configured provider for an edit.",
    }


def _reference(name: str, url: str, maintenance: str, authentication: str,
               tools: list[str] | None = None, notes: str = "", version: str | None = None) -> dict:
    value = {
        "name": name,
        "url": url,
        "maintenance": maintenance,
        "authentication": authentication,
        "notes": notes,
        "tool_names": tools or [],
    }
    if version:
        value["version"] = version
    return value


def build_image_model_profiles() -> dict:
    """Reviewed request contracts; published beside the runtime, never accepted from project settings."""
    def profile(label: str, payload: dict, *, edit_endpoint: str | None = None,
                dimensions: bool = False, maximum: int = 2048, pixels: int = 4_194_304,
                minimum: int = 256, multiple: int = 32, alpha: bool = False,
                result_format: str = "png", aspect_ratios: list[str] | None = None,
                resolutions: list[str] | None = None) -> dict:
        return {
            "display_name": label,
            "payload": payload,
            "edit_endpoint": edit_endpoint,
            "result_format": result_format,
            "aspect_ratios": aspect_ratios or [],
            "resolutions": resolutions or [],
            "minimum_dimension": minimum,
            "dimension_multiple": multiple,
            "capabilities": _capabilities(
                references=bool(edit_endpoint), edits=bool(edit_endpoint), alpha=alpha,
                accepts_dimensions=dimensions, width=maximum, height=maximum,
                maximum_pixels=pixels, reference_limit=1 if edit_endpoint else 0,
                reference_notes="This adapter accepts one local reference." if edit_endpoint else "This adapter exposes text-to-image only.",
                size_notes=(f"Adapter bounds: {minimum}-{maximum} pixels per edge in multiples of {multiple}, at most {pixels} total pixels."
                            if dimensions else "Use the model's default size or its listed aspect-ratio and resolution controls.")),
        }

    nano_ratios = ["auto", "21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16"]
    fal = {
        "fal-ai/flux-2-pro": profile("FLUX.2 Pro", {"image_size": "square_hd", "output_format": "png"},
            edit_endpoint="fal-ai/flux-2-pro/edit", dimensions=True, maximum=2560),
        "fal-ai/flux-2-flex": profile("FLUX.2 Flex", {"image_size": "square_hd", "output_format": "png"},
            edit_endpoint="fal-ai/flux-2-flex/edit", dimensions=True, maximum=2560),
        "fal-ai/flux/dev": profile("FLUX.1 Dev", {"image_size": "square_hd", "num_images": 1, "output_format": "png"}, dimensions=True),
        "fal-ai/flux/schnell": profile("FLUX.1 Schnell", {"image_size": "square_hd", "num_images": 1, "output_format": "png"}, dimensions=True),
        "fal-ai/bytedance/seedream/v4.5/text-to-image": profile("Seedream 4.5", {"image_size": "auto_2K", "num_images": 1, "max_images": 1},
            edit_endpoint="fal-ai/bytedance/seedream/v4.5/edit", dimensions=True, minimum=1920, maximum=4096, pixels=16_777_216, multiple=1),
        "fal-ai/nano-banana-2": profile("Nano Banana 2", {"num_images": 1, "output_format": "png", "limit_generations": True, "resolution": "1K"},
            edit_endpoint="fal-ai/nano-banana-2/edit", maximum=4096, pixels=16_777_216,
            aspect_ratios=nano_ratios + ["4:1", "1:4", "8:1", "1:8"], resolutions=["0.5K", "1K", "2K", "4K"]),
        "fal-ai/nano-banana-pro": profile("Nano Banana Pro", {"num_images": 1, "output_format": "png", "limit_generations": True, "resolution": "1K"},
            edit_endpoint="fal-ai/nano-banana-pro/edit", maximum=4096, pixels=16_777_216,
            aspect_ratios=nano_ratios, resolutions=["1K", "2K", "4K"]),
        "fal-ai/recraft/v4/text-to-image": profile("Recraft V4", {"image_size": "square_hd"}, result_format="webp"),
        "fal-ai/ideogram/v3": profile("Ideogram V3", {"image_size": "square_hd", "num_images": 1}),
        "fal-ai/ideogram/v3/generate-transparent": profile("Ideogram V3 Transparent", {"num_images": 1}, alpha=True,
            aspect_ratios=["1:3", "3:1", "1:2", "2:1", "9:16", "16:9", "10:16", "16:10", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "1:1"]),
    }
    for model, entry in fal.items():
        entry["documentation_urls"] = [f"https://fal.ai/models/{model}/api"]
        if entry["edit_endpoint"]:
            entry["documentation_urls"].append(f"https://fal.ai/models/{entry['edit_endpoint']}/api")
    replicate = {
        "black-forest-labs/flux-schnell": profile("FLUX Schnell", {"num_outputs": 1, "output_format": "png"}),
        "black-forest-labs/flux-dev": profile("FLUX Dev", {"num_outputs": 1, "output_format": "png"}),
        "black-forest-labs/flux-1.1-pro": profile("FLUX 1.1 Pro", {"output_format": "png"}),
    }
    for model, entry in replicate.items():
        entry["documentation_urls"] = [f"https://replicate.com/{model}/api/schema"]
        entry["capabilities"]["background_removal"] = True
    together = {
        "black-forest-labs/FLUX.2-pro": profile("FLUX.2 Pro", {}, dimensions=True),
        "black-forest-labs/FLUX.2-dev": profile("FLUX.2 Dev", {"steps": 20}, dimensions=True),
        "black-forest-labs/FLUX.2-flex": profile("FLUX.2 Flex", {}, dimensions=True),
        "black-forest-labs/FLUX.1.1-pro": profile("FLUX 1.1 Pro", {}, dimensions=True, maximum=1440, pixels=2_073_600),
    }
    for entry in together.values():
        entry["documentation_urls"] = ["https://docs.together.ai/docs/inference/images/overview", "https://docs.together.ai/docs/inference/images/parameters"]
        entry["capabilities"]["reference_images"]["notes"] = "The adapter does not publish local references to the public URLs required by Together."
    return {"fal_ai": fal, "replicate": replicate, "together_ai": together}


def _provider(provider_id: str, display_name: str, description: str, requirements: list[str],
              good_for: list[str], cost: str, models: list[str], auth: str,
              capabilities: dict, *, availability: str = "supported",
              clients: list[str] | None = None, route: dict | None = None,
              reference_mcp: dict | None = None) -> dict:
    value = {
        "id": provider_id,
        "display_name": display_name,
        "description": description,
        "availability": availability,
        "requirements": requirements,
        "good_for": good_for,
        "cost_summary": cost,
        "documentation_url": None,
        "models": models,
        "supported_coding_environments": clients or ALL_CLIENTS,
        "route": route or _route(provider_id, auth),
        "capabilities": capabilities,
    }
    if reference_mcp:
        value["reference_mcp"] = reference_mcp
    return value


def _tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        (
            item
            for item in root.rglob("*")
            if item.is_file() and not {"node_modules", "__pycache__"}.intersection(item.parts)
        ),
        key=lambda item: item.relative_to(root).as_posix(),
    ):
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        if path.name == "LICENSE" or path.suffix.lower() in TEXT_SOURCE_SUFFIXES:
            data = data.replace(b"\r\n", b"\n")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(data)
    return digest.hexdigest()


def build_image_generation_table(source_root: Path | None = None) -> dict:
    """Return the single provider catalog used by app setup and asset guidance."""
    providers = [
        _provider(
            "gptimage", "ChatGPT subscription (GPTImage)",
            "Use the gptimage MCP server with a ChatGPT subscription.",
            ["A ChatGPT plan and browser sign-in to gptimage.", "This community server calls an undocumented ChatGPT service, not the public Images API."],
            ["Concept art", "Images guided by reference files"],
            "No separate image API bill; plan usage limits apply.",
            ["ChatGPT image generation through the server's configured route"], "chatgpt_subscription",
            _capabilities(references=True, edits=False, alpha=False, width=3840, height=3840,
                reference_notes="Use list_references to discover project references, then pass relevant image paths and describe each one's role. Reference count is not documented; output sizes have a maximum edge and aspect-ratio rule.",
                alpha_notes="PNG output does not guarantee a transparent background.",
                edit_fallback="Use reference_images to make a new version; choose another configured provider for precise image edits."),
            route=_route("gptimage", "chatgpt_subscription", kind="local_package", component="imagegen.gptimage",
                source_repository="https://github.com/Connected-Mate/gptimage",
                source_revision="dfb4948b6877b5b7febf73e1342fcfacd862a1ed",
                package_name="gptimage", package_version="0.1.0",
                runtime_entry=".tools/image_generation/providers/gptimage/src/server.js",
                tools={"generate": "generate_image", "auth_status": "image_auth_status", "list_references": "list_references"},
                tool_arguments={"prompt": "prompt", "output_path": "out", "reference_images": "reference_images", "quality": "quality", "size": "size"}),
            reference_mcp=_reference("GPTImage MCP", "https://github.com/Connected-Mate/gptimage", "community", "ChatGPT subscription sign-in", ["generate_image", "image_auth_status", "list_references"], "Pinned source; account data stays in the server's local auth store. The configured route does not establish the underlying image model.")),
        _provider("openai_api", "OpenAI Images API", "Use OpenAI image models with a key saved on this computer.",
            ["An OpenAI API key saved in the operating-system credential store."], ["General image work", "Reference edits", "Transparent PNG output"],
            "Pay per image; price changes with model and quality.", ["GPT Image 2.5 Sunburst", "GPT Image 2.5 Flare", "GPT Image 2"], "api_key_vault",
            _capabilities(references=True, edits=True, alpha=True, accepts_dimensions=True, width=3840, height=3840, maximum_pixels=8_294_400, reference_limit=16,
                reference_notes="Reference count depends on model and endpoint. Use local image paths with the edit tool.",
                alpha_notes="Supported GPT Image models can request transparent output. Verify the saved alpha.")),
        _provider("gemini_api", "Google Gemini images (Nano Banana)", "Use Google image models through the Gemini API.",
            ["A Google AI Studio API key saved in the operating-system credential store."], ["Reference-guided generations", "Image edits", "Several visual styles"],
            "Pay per image; cost depends on model and resolution.", ["Nano Banana 2.1", "Nano Banana 2 (Gemini 3.1 Flash Image)", "Nano Banana Pro (Gemini 3 Pro Image)"], "api_key_vault",
            _capabilities(references=True, edits=True, alpha=False, width=4096, height=4096, reference_limit=14,
                reference_notes="Reference-image limits vary by model.", alpha_notes="The API does not promise native transparent output."),
            reference_mcp=_reference("gemini-mcp", "https://github.com/chrischall/gemini-mcp", "community", "Google API key", ["generate_image", "edit_image"], "The setup app uses its own pinned adapter for vault-backed keys.")),
        _provider("fal_ai", "fal.ai", "Choose image models from fal's hosted catalog.",
            ["A fal API key saved in the operating-system credential store."], ["FLUX", "Recraft", "Ideogram", "Seedream", "Nano Banana and more"],
            "Pay per selected model run; price and limits vary by endpoint.", [], "api_key_vault",
            _capabilities(references=True, edits=True, alpha=True, accepts_dimensions=True, width=4096, height=4096, maximum_pixels=16_777_216, reference_limit=1,
                reference_notes="One local reference is supported by FLUX.2, Seedream, and Nano Banana. Other included models are text-to-image only.",
                size_notes="Dimensions depend on model. Nano Banana uses resolution tiers; Recraft and Ideogram use default sizes. Inspect the selected tool's schema.",
                alpha_notes="Only the Ideogram V3 Transparent selection offers native alpha; every saved result is verified."),
            reference_mcp=_reference("fal MCP", "https://mcp.fal.ai/mcp", "official", "fal API key", ["run_model", "get_model_schema", "upload_file"], "Hosted MCP sends the key in an authorization header; the app-managed route keeps it in the OS vault.")),
        _provider("replicate", "Replicate", "Use hosted models from many image providers through one account.",
            ["A Replicate API token saved in the operating-system credential store."], ["Trying different model families", "Fast drafts", "Model variety"],
            "Pay per selected model run; FLUX Schnell is the default.", [], "api_key_vault",
            _capabilities(references=False, edits=False, alpha=False,
                reference_notes="The included FLUX Schnell, Dev, and 1.1 Pro routes expose text-to-image only.", alpha_notes="Use a selected background-removal route when the model does not return alpha.", background_removal=True),
            reference_mcp=_reference("Replicate MCP", "https://replicate.com/docs/reference/mcp", "official", "Replicate token", [], "The server exposes Replicate's model and prediction API.")),
        _provider("black_forest_labs", "Black Forest Labs (FLUX)", "Use FLUX through the Black Forest Labs API.",
            ["A BFL API key saved in the operating-system credential store."], ["Detailed scenes", "Reference composition", "Image-to-image edits"],
            "Pay per image; price depends on model and quality.", ["FLUX.2 Pro", "FLUX.2 Max", "FLUX.2 Flex"], "api_key_vault",
            _capabilities(references=True, edits=True, alpha=False, accepts_dimensions=True, width=4096, height=4096, maximum_pixels=4_194_304, reference_limit=1,
                reference_notes="The app adapter sends one reference image to the selected FLUX endpoint.", alpha_notes="Native alpha output is not documented."),
            reference_mcp=_reference("Official FLUX MCP", "https://mcp.bfl.ai", "official", "BFL account sign-in", ["generate_image", "generate_variations"], "The setup app uses the API adapter so the key stays in the OS vault.", "1.2.0")),
        _provider("stability_ai", "Stability AI", "Use Stable Image and Stable Diffusion models through the Stability API.",
            ["A Stability API key saved in the operating-system credential store."], ["Image generation", "Image-to-image work", "Background removal"],
            "Pay per image; some image operations cost extra.", ["Stable Image Core", "Stable Image Ultra"], "api_key_vault",
            _capabilities(references=True, edits=True, alpha=False, width=2048, height=2048, reference_limit=1,
                reference_notes="Image-to-image and control features depend on the endpoint.", alpha_notes="Use the API background-removal operation, then verify alpha.", background_removal=True),
            reference_mcp=_reference("Stability image MCP", "https://github.com/alesurli/mcp-stability-ai", "community", "Stability API key", ["generate_image", "edit_image", "remove_background"], "No first-party image MCP was found; the setup app uses its own reviewed API adapter.")),
        _provider("ideogram", "Ideogram", "Use Ideogram's image models through its API.",
            ["An Ideogram API key saved in the operating-system credential store."], ["Readable lettering", "Design images", "Reference edits"],
            "API use is billed through Ideogram credits.", ["Ideogram 4"], "api_key_vault",
            _capabilities(references=True, edits=True, alpha=True, width=8192, height=8192, reference_limit=1,
                reference_notes="The app adapter supports one reference image for edits. The transparent route uses a size tier.", alpha_notes="Request the transparent generation route and verify alpha."),
            reference_mcp=_reference("Ideogram MCP", "https://mcp.ideogram.ai/mcp", "official", "Ideogram account sign-in", ["generate_image", "describe_image", "remix_image"], "The setup app uses the API route so the key stays in the OS vault.")),
        _provider("recraft", "Recraft", "Use Recraft raster models through its API.",
            ["A Recraft API key saved in the operating-system credential store, plus API units."], ["Graphic design", "Vector images", "Style-guided edits"],
            "Pay per image or operation; raster generation starts at a few cents.", ["Recraft V4.1", "Recraft V4"], "api_key_vault",
            _capabilities(references=True, edits=True, alpha=False, width=2048, height=2048, reference_limit=10,
                reference_notes="Image references and sizes depend on model.", alpha_notes="Use the background-removal operation for alpha and verify the result.", background_removal=True),
            reference_mcp=_reference("Recraft MCP", "https://mcp.recraft.ai/mcp", "official", "Recraft API key", [], "The setup app uses the API route so keys stay in the OS vault.")),
        _provider("leonardo", "Leonardo.Ai", "Use Leonardo image models through its API.",
            ["A Leonardo API key saved in the operating-system credential store."], ["Realistic scenes", "Style references", "Image-to-image editing"],
            "Pay per model use; check the current API estimate.", ["Lucid Origin"], "api_key_vault",
            _capabilities(references=False, edits=False, alpha=False, accepts_dimensions=True, width=3840, height=3616,
                reference_notes="This app adapter supports text-to-image only; choose a model-specific client for edits.", alpha_notes="Native alpha output is not exposed by the default route."),
            reference_mcp=_reference("Leonardo MCP", "https://mcp.leonardo.ai/v1/mcp", "official", "Leonardo API key", [], "The app-managed route keeps the key in the OS vault.")),
        _provider("adobe_firefly", "Adobe Firefly", "Use Adobe Firefly through an organization-provided API.",
            ["An Adobe organization, service API key, and IMS access token stored in the operating-system credential store."], ["Style references", "Structure references", "Creative workflows"],
            "API pricing depends on organization access and credits.", ["Firefly Image 5"], "enterprise_credentials",
            _capabilities(references=True, edits=True, alpha=False,
                reference_notes="Reference options depend on the Firefly workflow.", alpha_notes="This connected workflow does not expose background removal; use a selected remover route and verify alpha."),
            availability="conditional",
            reference_mcp=_reference("Adobe Run-Workflow MCP", "https://run-workflow.adobe.io/mcp", "official", "Organization IMS token and service API key", [], "The organization configures its workflow tools. Ask the MCP for tools/list and use only the exact names it returns.")),
        _provider("xai_grok", "xAI Grok Imagine", "Use Grok Imagine for prompt-based images and reference edits.",
            ["An xAI API key saved in the operating-system credential store."], ["Photoreal images", "Reference-guided edits"],
            "Pay per image; resolution and quality change the price.", ["grok-imagine-image-2.0"], "api_key_vault",
            _capabilities(references=True, edits=True, alpha=False, width=2048, height=2048, reference_limit=5,
                reference_notes="The API accepts reference images for edits.", alpha_notes="Native transparent output is not documented."),
            reference_mcp=_reference("grok-mcp", "https://github.com/libraz/grok-mcp", "community", "xAI API key", ["generate_image", "edit_image"], "No official image-generation MCP was found; the app uses its reviewed API adapter.")),
        _provider("together_ai", "Together AI", "Use open image models through Together's hosted API.",
            ["A Together API key saved in the operating-system credential store."], ["FLUX models", "Open model families", "Fast hosted generation"],
            "Pay per model; the connected route uses FLUX.2 Pro.", ["FLUX.2 Pro"], "api_key_vault",
            _capabilities(references=False, edits=False, alpha=False, accepts_dimensions=True, width=1920, height=1920,
                reference_notes="FLUX.2 accepts URL references, but the setup route does not publish project files to a public URL.", alpha_notes="Native alpha is not documented."),
            reference_mcp=_reference("Together Images API", "https://www.together.ai/models/flux-2-pro", "official", "Together API key", ["generate_image", "edit_image"])),
        _provider("openrouter", "OpenRouter", "Use one account to try image models from many providers.",
            ["An OpenRouter API key saved in the operating-system credential store."], ["Comparing image models", "Choosing among providers", "Reference edits where supported"],
            "Pay per model; the connected route uses GPT Image 2.5 Sunburst.", ["GPT Image 2.5 Sunburst"], "api_key_vault",
            _capabilities(references=True, edits=True, alpha=True, reference_limit=16,
                size_notes="Choose one of the selected model's supported aspect ratios; the model chooses output pixel dimensions.",
                reference_notes="The connected model accepts reference images for editing.", alpha_notes="Request a transparent PNG and check that its pixels include transparency."),
            route=_route("openrouter", "api_key_vault", tool_arguments={
                "prompt": "prompt", "output_path": "out", "reference_image": "image", "reference_images": "reference_images",
                "aspect_ratio": "aspect_ratio", "transparent_background": "transparent_background",
            }),
            reference_mcp=_reference("OpenRouter MCP", "https://mcp.openrouter.ai/mcp", "official", "OpenRouter browser authorization", ["generate-image"], "The hosted MCP has short-lived authorization and a default spending cap. The setup app uses its Images API adapter for references.")),
        _provider("comfyui_local", "Local ComfyUI", "Use a ComfyUI server and checkpoint installed on this computer.",
            ["A local ComfyUI server, a compatible checkpoint, and available GPU memory."], ["Local models", "Prompt-based image creation", "One reference-guided edit"],
            "No per-image service bill; local hardware and model downloads are required.", ["Checkpoint selected in local ComfyUI"], "local",
            _capabilities(references=True, edits=True, alpha=False, accepts_dimensions=True, reference_limit=1,
                reference_notes="The included basic workflow supports one reference image; custom workflows can add more.", alpha_notes="The basic local workflow does not make transparent output."),
            availability="conditional",
            reference_mcp=_reference("Comfy-Org comfy-mcp", "https://github.com/Comfy-Org/comfy-mcp", "official", "Local ComfyUI server", [], "The setup app uses a local adapter and does not alter the separate HOI4 portrait workflow.", "0.10.0")),
        _provider("automatic1111_local", "AUTOMATIC1111", "Use a local AUTOMATIC1111 WebUI API server.",
            ["A local install started with API access enabled and a downloaded model."], ["Local image generation", "Image-to-image", "Inpainting"],
            "No per-image service bill; local hardware and models are required.", ["Models installed in AUTOMATIC1111"], "local",
            _capabilities(references=True, edits=True, alpha=False, accepts_dimensions=True, reference_limit=1,
                reference_notes="The local API and model determine accepted image sizes.", alpha_notes="Use a selected background-removal route and verify alpha."),
            availability="conditional",
            reference_mcp=_reference("image-generation-mcp", "https://github.com/pvliesdonk/image-generation-mcp", "community", "Local server URL", ["generate_image", "generate_image_from_image"], "The setup app uses its own pinned local API adapter.")),
        _provider("forge_local", "Stable Diffusion Forge", "Use a local Forge API server and installed model.",
            ["A local Forge install started with API access enabled and a downloaded model."], ["Local image generation", "Image-to-image", "Inpainting"],
            "No per-image service bill; local hardware and models are required.", ["Models installed in Forge"], "local",
            _capabilities(references=True, edits=True, alpha=False, accepts_dimensions=True, reference_limit=1,
                reference_notes="The local API and model determine accepted image sizes.", alpha_notes="Use a selected background-removal route and verify alpha."),
            availability="conditional",
            reference_mcp=_reference("image-generation-mcp", "https://github.com/pvliesdonk/image-generation-mcp", "community", "Local server URL", ["generate_image", "generate_image_from_image"], "The setup app uses its own pinned local API adapter.")),
        _provider("codex_native", "Codex image generation", "Use the image tool built into Codex with a ChatGPT plan.",
            ["Codex must be the primary coding client and signed in to a ChatGPT plan."], ["Image generation", "Reference-guided edits", "Transparent output"],
            "Uses the plan's Codex limits; there is no separate image API bill.", ["Codex image_gen"], "chatgpt_subscription",
            _capabilities(references=True, edits=True, alpha=True,
                reference_notes="Pass the reference files to the native Codex image tool.", alpha_notes="Request transparency and verify the saved PNG alpha."),
            route=_route("codex_native", "chatgpt_subscription", kind="native", tools={"generate": "image_gen"},
                tool_arguments={"prompt": "prompt", "output_path": None, "reference_images": "referenced_image_paths", "quality": None, "size": None, "transparent_background": "transparent_background"}, primary_environment="codex"),
            clients=["codex"]),
        _provider("vertex_imagen", "Google Vertex AI Imagen", "Use Google Cloud Imagen models.",
            ["A Google Cloud project and credentials stored in the operating-system credential store."], ["Fast concept images", "High-quality final images"],
            "Pay per image; price depends on the Imagen tier.", ["Imagen 4 Fast", "Imagen 4 Standard", "Imagen 4 Ultra"], "cloud_credentials",
            _capabilities(references=False, edits=False, alpha=False, width=2048, height=2048,
                reference_notes="Imagen 4 generation is text-only; use Gemini for image edits.", alpha_notes="Native transparent output is not documented."),
            availability="conditional"),
        _provider("microsoft_foundry", "Microsoft Foundry MAI Image", "Use Microsoft Foundry image models in a configured Azure resource.",
            ["A deployed MAI image model, its resource endpoint, deployment name, and API key saved on this computer."], ["Text-to-image", "Reference-guided edits"],
            "Pay per image; preview model prices may change.", ["MAI-Image-2.6", "MAI-Image-2.6-Flash"], "enterprise_credentials",
            _capabilities(references=True, edits=True, alpha=False, accepts_dimensions=True, width=1536, height=1536, maximum_pixels=2_359_296, reference_limit=5,
                reference_notes="Reference limit and resolution depend on model; the newest models are in preview.", alpha_notes="Native transparent output is not documented."),
            availability="conditional"),
        _provider("aws_bedrock", "AWS Bedrock image models", "Use supported image models and edit tools through AWS Bedrock.",
            ["An AWS account, supported region, model access, and AWS credentials."], ["Image edits", "Background removal", "Hosted model access"],
            "Pay per model or image operation; AWS pricing varies by region.", ["Stable Image Core", "Stable Image Ultra"], "cloud_credentials",
            _capabilities(references=True, edits=True, alpha=False, width=1536, height=1536, maximum_pixels=2_359_296, reference_limit=1,
                reference_notes="Stable Image Ultra accepts one reference image for edits. Stable Image Core is text-to-image only.", alpha_notes="Use a Bedrock background-removal operation and verify alpha.", background_removal=True),
            availability="conditional",
            reference_mcp=_reference("AWS Bedrock image MCP", "https://github.com/awslabs/bedrock-image-mcp-server", "official", "AWS credentials and model access", [], "Uses the Stability image models; retired Nova Canvas and Titan Image Generator routes are excluded.")),
        _provider("huggingface_inference", "Hugging Face Inference Providers", "Use image models available through Hugging Face providers.",
            ["A Hugging Face token saved in the operating-system credential store."], ["Trying different hosted models", "Open model families"],
            "Pay as you go; cost depends on model and provider.", ["FLUX.1 Krea Dev"], "api_key_vault",
            _capabilities(references=False, edits=False, alpha=False, accepts_dimensions=True,
                reference_notes="The included route covers text-to-image models. Use a model-specific client for image edits.", alpha_notes="Use a selected background-removal route and verify alpha."),
            reference_mcp=_reference("Hugging Face Inference Providers", "https://huggingface.co/docs/inference-providers/index", "official", "Hugging Face token", ["generate_image", "edit_image"])),
        _provider("midjourney_manual", "Midjourney (manual only)", "Use Midjourney manually, then add files to your mod. It has no public API and does not permit automated generation.",
            ["A Midjourney subscription and manual use of its web or Discord app."], ["Stylized concept art", "Manual image editing"],
            "Subscription plans; no connected API route.", ["Midjourney V8.2", "Edit model"], "manual",
            _capabilities(references=True, edits=True, alpha=False, reference_limit=4,
                reference_notes="Use references manually in the web editor.", alpha_notes="The public API does not document alpha output."),
            route=_route("midjourney_manual", "manual", kind="manual", tools={}, tool_arguments={}), availability="manual_only"),
        _provider("none", "None \u2014 I will make art myself", "Do not connect an image-generation provider.",
            ["No service account or local install is needed."], ["Using your own art", "Sourced images"], "No provider charge.", [], "none",
            _capabilities(references=False, edits=False, alpha=False,
                reference_notes="Add your own files to the project.", alpha_notes="No image route is selected.", edit_fallback="Create or edit the image yourself and add it to the project."),
            route=_route("none", "none", kind="manual", tools={}, tool_arguments={})),
    ]
    api_routes = {
        "openai_api": ("openai_images", "https://api.openai.com/v1", "gpt-image-2.5-sunburst", [("api_key", "OpenAI API key", "OPENAI_API_KEY")]),
        "gemini_api": ("gemini_generate_content", "https://generativelanguage.googleapis.com/v1", "gemini-nano-banana-2.1", [("api_key", "Google AI Studio API key", "GEMINI_API_KEY")]),
        "fal_ai": ("fal_queue", "https://queue.fal.run", "fal-ai/flux-2-pro", [("api_key", "fal API key", "FAL_KEY")]),
        "replicate": ("replicate_predictions", "https://api.replicate.com/v1", "black-forest-labs/flux-schnell", [("api_key", "Replicate API token", "REPLICATE_API_TOKEN")]),
        "black_forest_labs": ("bfl", "https://api.bfl.ai/v1", "flux-2-pro", [("api_key", "BFL API key", "BFL_API_KEY")]),
        "stability_ai": ("stability", "https://api.stability.ai/v2beta", "stable-image-ultra", [("api_key", "Stability API key", "STABILITY_API_KEY")]),
        "ideogram": ("ideogram", "https://api.ideogram.ai/v1", "ideogram-v4", [("api_key", "Ideogram API key", "IDEOGRAM_API_KEY")]),
        "recraft": ("recraft", "https://external.api.recraft.ai/v1", "recraftv4_1", [("api_key", "Recraft API key", "RECRAFT_API_KEY")]),
        "leonardo": ("leonardo", "https://cloud.leonardo.ai/api/rest/v1", "7b592283-e8a7-4c5a-9ba6-d18c31f258b9", [("api_key", "Leonardo API key", "LEONARDO_API_KEY")]),
        "adobe_firefly": ("adobe_firefly", "https://firefly-api.adobe.io/v3", "firefly_image", [("ims_token", "Adobe IMS access token", "ADOBE_IMS_TOKEN"), ("service_key", "Adobe service API key", "ADOBE_SERVICE_API_KEY")]),
        "xai_grok": ("xai_imagine", "https://api.x.ai/v1", "grok-imagine-image-2.0", [("api_key", "xAI API key", "XAI_API_KEY")]),
        "together_ai": ("together_images", "https://api.together.ai/v1", "black-forest-labs/FLUX.2-pro", [("api_key", "Together API key", "TOGETHER_API_KEY")]),
        "openrouter": ("openrouter_images", "https://openrouter.ai/api/v1", "openai/gpt-image-2.5-sunburst", [("api_key", "OpenRouter API key", "OPENROUTER_API_KEY")]),
        "comfyui_local": ("comfyui", None, None, []),
        "automatic1111_local": ("automatic1111", "http://127.0.0.1:7860", None, []),
        "forge_local": ("automatic1111", "http://127.0.0.1:7860", None, []),
        "vertex_imagen": ("vertex_ai", "https://us-central1-aiplatform.googleapis.com/v1", "imagen-4.0-generate-001", [("service_account", "Google Cloud service-account key", "GOOGLE_APPLICATION_CREDENTIALS")]),
        "microsoft_foundry": ("microsoft_foundry", None, None, [("resource_url", "Microsoft Foundry resource endpoint", "AZURE_ENDPOINT"), ("api_key", "Microsoft Foundry API key", "AZURE_API_KEY")]),
        "aws_bedrock": ("aws_bedrock", None, "stability.stable-image-ultra-v1:1", [("access_key", "AWS access key ID", "AWS_ACCESS_KEY_ID"), ("secret_key", "AWS secret access key", "AWS_SECRET_ACCESS_KEY")]),
        "huggingface_inference": ("huggingface_inference", "https://router.huggingface.co/hf-inference/models", "black-forest-labs/FLUX.1-Krea-dev", [("api_key", "Hugging Face token", "HF_TOKEN")]),
    }
    adapter_models = {
        "openai_api": ["gpt-image-2.5-sunburst", "gpt-image-2.5-flare", "gpt-image-2"],
        "gemini_api": ["gemini-nano-banana-2.1", "gemini-3.1-flash-image", "gemini-3-pro-image"],
        "black_forest_labs": ["flux-2-pro", "flux-2-max", "flux-2-flex"],
        "stability_ai": ["stable-image-core", "stable-image-ultra"],
        "ideogram": ["ideogram-v4"],
        "recraft": ["recraftv4_1", "recraftv4"],
        "leonardo": ["7b592283-e8a7-4c5a-9ba6-d18c31f258b9"],
        "xai_grok": ["grok-imagine-image-2.0"],
        "openrouter": ["openai/gpt-image-2.5-sunburst"],
        "vertex_imagen": ["imagen-4.0-fast-generate-001", "imagen-4.0-generate-001", "imagen-4.0-ultra-generate-001"],
        "aws_bedrock": ["stability.stable-image-core-v1:1", "stability.stable-image-ultra-v1:1"],
        "huggingface_inference": ["black-forest-labs/FLUX.1-Krea-dev"],
    }
    model_profiles = build_image_model_profiles()
    for provider in providers:
        provider["route"]["supported_models"] = adapter_models.get(provider["id"], [])
        if provider["id"] in model_profiles:
            profiles = model_profiles[provider["id"]]
            provider["route"]["supported_models"] = list(profiles)
            provider["models"] = [profile["display_name"] for profile in profiles.values()]
    next(item for item in providers if item["id"] == "fal_ai")["route"]["result_format"] = "model_defined"
    proxy_routes = {
        "adobe_firefly": ("https://run-workflow.adobe.io/mcp", [("ims_token", "Adobe IMS access token", "ADOBE_IMS_TOKEN", "authorization", "Bearer "), ("service_key", "Adobe service API key", "ADOBE_SERVICE_API_KEY", "x-api-key", "")], {}),
    }
    oauth_routes = {}
    for item in providers:
        route = item["route"]
        values = api_routes.get(item["id"])
        if values:
            route["api_protocol"], route["api_base_url"], route["default_model"], credentials = values
            route["credential_fields"] = [
                {"id": field_id, "display_name": display_name, "environment_name": environment_name}
                for field_id, display_name, environment_name in credentials
            ]
        if item["id"] == "xai_grok":
            route["result_format"] = "jpeg"
        if item["id"] == "leonardo":
            route["result_format"] = "model_defined"
        if item["id"] in proxy_routes:
            url, credentials, tools = proxy_routes[item["id"]]
            route["api_protocol"] = "mcp_proxy"
            route["api_base_url"] = url
            route["default_model"] = None
            route["result_format"] = "model_defined"
            route["credential_fields"] = [
                {"id": field_id, "display_name": display_name, "environment_name": environment_name,
                 "header": header, "prefix": prefix}
                for field_id, display_name, environment_name, header, prefix in credentials
            ]
            route["tool_names"] = tools
            route["tool_arguments"] = {}
            route["auth_headers"] = sorted({field["header"] for field in route["credential_fields"]})
        if item["id"] in oauth_routes:
            url, tool_names = oauth_routes[item["id"]]
            route["kind"] = "remote_http"
            route["auth_method"] = "oauth"
            route["url"] = url
            route["server_id"] = item["id"]
            route["component_id"] = None
            route["runtime_entry"] = None
            route["api_protocol"] = None
            route["api_base_url"] = None
            route["default_model"] = None
            route["credential_fields"] = []
            route["tool_names"] = tool_names
    root = source_root or Path(__file__).resolve().parents[1]
    package = root / ".tools" / "image_generation" / "providers" / "gptimage"
    gptimage = next(item for item in providers if item["id"] == "gptimage")
    gptimage["route"]["source_tree_sha256"] = _tree_sha256(package)
    lock_bytes = (package / "package-lock.json").read_bytes().replace(b"\r\n", b"\n")
    gptimage["route"]["package_lock_sha256"] = hashlib.sha256(lock_bytes).hexdigest()
    documentation = {
        "openai_api": "https://developers.openai.com/api/docs/guides/image-generation/",
        "gemini_api": "https://ai.google.dev/gemini-api/docs/image-generation",
        "fal_ai": "https://fal.ai/pricing",
        "replicate": "https://replicate.com/docs",
        "black_forest_labs": "https://bfl.ai/models/flux-3-image",
        "stability_ai": "https://platform.stability.ai/docs/getting-started/stable-image",
        "ideogram": "https://developer.ideogram.ai/",
        "recraft": "https://www.recraft.ai/docs",
        "leonardo": "https://docs.leonardo.ai/docs/connect-to-leonardoai-mcp",
        "adobe_firefly": "https://developer.adobe.com/firefly-services/docs/firefly-api/",
        "xai_grok": "https://docs.x.ai/developers/model-capabilities/imagine",
        "together_ai": "https://www.together.ai/models/flux-2-pro",
        "openrouter": "https://openrouter.ai/docs/guides/features/images",
        "comfyui_local": "https://docs.comfy.org/",
        "automatic1111_local": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API",
        "forge_local": "https://github.com/lllyasviel/stable-diffusion-webui-forge",
        "codex_native": "https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/imagegen/SKILL.md",
        "vertex_imagen": "https://cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate-001",
        "microsoft_foundry": "https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-mai-image",
        "aws_bedrock": "https://docs.aws.amazon.com/bedrock/latest/userguide/stable-image-services.html",
        "huggingface_inference": "https://huggingface.co/docs/inference-providers/index",
        "midjourney_manual": "https://github.com/midjourney/docs/blob/main/data/faq.txt",
    }
    api_only = {"openai_api", "together_ai", "vertex_imagen", "microsoft_foundry", "huggingface_inference"}
    for item in providers:
        item["documentation_url"] = documentation.get(item["id"])
        if item["id"] in api_only:
            item.pop("reference_mcp", None)
        if item["id"] == "aws_bedrock" and item.get("reference_mcp"):
            item["reference_mcp"]["url"] = "https://github.com/awslabs/bedrock-image-mcp-server"
    return {"default_provider": "gptimage", "providers": providers}


def write_runtime_provider_catalog(source_root: Path | None = None) -> Path:
    """Write the route allowlist shipped beside the project-local adapter."""
    root = source_root or Path(__file__).resolve().parents[1]
    table = build_image_generation_table(root)
    catalog = {
        "default_provider": table["default_provider"],
        "model_profiles": build_image_model_profiles(),
        "providers": [
            {
                "id": provider["id"],
                "display_name": provider["display_name"],
                "availability": provider["availability"],
                "route": provider["route"],
                "capabilities": provider["capabilities"],
            }
            for provider in table["providers"]
        ],
    }
    output = root / ".tools" / "image_generation" / "runtime" / "provider_catalog.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def build_image_generation_components(source_root: Path | None = None) -> list[dict]:
    """Return provider runtime components that the app installs on selection."""
    root = source_root or Path(__file__).resolve().parents[1]
    table = build_image_generation_table(root)
    gptimage = next(item for item in table["providers"] if item["id"] == "gptimage")["route"]
    gptimage_component = {
        "id": "imagegen.gptimage",
        "display_name": "GPTImage MCP source",
        "description": "Project-local GPTImage server source for the ChatGPT subscription route.",
        "category": "mcp",
        "optional": True,
        "platforms": ["windows", "macos", "linux"],
        "source": {
            "kind": "tree",
            "path": ".tools/image_generation/providers/gptimage",
            "include": ["**"],
            "exclude": ["**/node_modules/**"],
        },
        "destination": {
            "path": ".tools/image_generation/providers/gptimage/",
            "ownership": "managed",
            "outside_project": False,
        },
        "dependencies": [],
        "required_tools": [
            {"id": "node", "required": True, "version_policy": "any", "version": ">=20", "commands": ["node"], "health_checks": ["node --version"]},
            {"id": "npm", "required": True, "version_policy": "any", "version": "Node LTS", "commands": ["npm"], "health_checks": ["npm --version"]},
        ],
        "environment": [],
        "expected_files": [],
        "conflicts": [],
        "conflict_policy": "replace_if_unmodified",
        "validation": [{
            "id": "imagegen.gptimage.bootstrap",
            "severity": "block",
            "kind": "command",
            "target": "python",
            "parameters": {
                "script_path": ".tools/image_generation/providers/gptimage/bootstrap.py",
                "package_root": ".tools/image_generation/providers/gptimage",
                "arguments": [
                    "--package-root", "<project_root>/.tools/image_generation/providers/gptimage",
                    "--expected-tree-sha256", gptimage["source_tree_sha256"],
                    "--expected-lock-sha256", gptimage["package_lock_sha256"],
                ],
                "package_name": gptimage["package_name"],
                "package_version": gptimage["package_version"],
                "source_revision": gptimage["source_revision"],
                "source_tree_sha256": gptimage["source_tree_sha256"],
                "package_lock_sha256": gptimage["package_lock_sha256"],
                "required_tools": ["generate_image", "image_auth_status"],
                "network_access": "Downloads only the exact dependencies in the checked-in npm lockfile from the npm registry during install or repair. The installer disables lifecycle scripts, uses a temporary cache, and removes that cache when complete.",
                "expected_writes": [
                    ".tools/image_generation/providers/gptimage/node_modules/**",
                    "the current user's temporary npm cache directory (removed when bootstrap finishes)",
                ],
                "privilege": "current_user",
                "rollback_boundary": "Managed project files roll back transactionally. Setup repair removes the managed node_modules tree; the temporary npm cache is removed by bootstrap and other user files are not changed.",
            },
        }],
        "update": {
            "strategy": "replace_if_unmodified",
            "remove_obsolete": True,
            "preserve_local_additions": True,
        },
        "capabilities": ["image generation", "reference images", "ChatGPT subscription"],
        "notes": ["Source revision is pinned to Connected-Mate/gptimage; dependency versions and integrity are in the included npm lockfile."],
    }
    runtime_component = {
        "id": "imagegen.runtime",
        "display_name": "Image provider MCP adapter",
        "description": "Project-local, provider-neutral MCP adapter for selected image APIs and local image servers.",
        "category": "mcp",
        "optional": True,
        "platforms": ["windows", "macos", "linux"],
        "source": {
            "kind": "tree",
            "path": ".tools/image_generation/runtime",
            "include": ["**"],
        },
        "destination": {
            "path": ".tools/image_generation/runtime/",
            "ownership": "managed",
            "outside_project": False,
        },
        "dependencies": [],
        "required_tools": [{
            "id": "python",
            "required": True,
            "version_policy": "any",
            "version": ">=3.10",
            "commands": ["python", "python3", "py"],
            "health_checks": ["python --version"],
        }],
        "environment": [],
        "expected_files": [],
        "conflicts": [],
        "conflict_policy": "replace_if_unmodified",
        "validation": [],
        "update": {
            "strategy": "replace_if_unmodified",
            "remove_obsolete": True,
            "preserve_local_additions": True,
        },
        "capabilities": ["image generation", "image editing", "OS credential access", "local image servers"],
        "notes": ["API keys are read from the operating-system credential store at tool-call time and are never written to project files."],
    }
    return [runtime_component, gptimage_component]
