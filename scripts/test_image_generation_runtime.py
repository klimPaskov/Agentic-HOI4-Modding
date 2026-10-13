from __future__ import annotations

import json
import base64
import struct
import sys
import tempfile
import unittest
import zlib
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".tools" / "image_generation" / "runtime"))
import server


def png(color_type: int = 6, alpha: int = 0, width: int = 1, height: int = 1) -> bytes:
    signature = b"\x89PNG\r\n\x1a\n"
    header = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    pixel = {0: b"\x80", 2: b"\x10\x20\x30", 3: b"\x00", 4: bytes((128, alpha)), 6: bytes((16, 32, 48, alpha))}[color_type]

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    rows = b"".join(b"\x00" + pixel * width for _ in range(height))
    return signature + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


def grayscale_trns_png(bit_depth: int, pixels: list[int], transparent_sample: int) -> bytes:
    if bit_depth not in {1, 2, 4} or any(pixel < 0 or pixel >= 1 << bit_depth for pixel in pixels):
        raise ValueError("invalid packed grayscale fixture")
    signature = b"\x89PNG\r\n\x1a\n"
    header = struct.pack(">IIBBBBB", len(pixels), 1, bit_depth, 0, 0, 0, 0)

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    packed = bytearray((len(pixels) * bit_depth + 7) // 8)
    for index, sample in enumerate(pixels):
        shift = 8 - bit_depth * ((index % (8 // bit_depth)) + 1)
        packed[index // (8 // bit_depth)] |= sample << shift
    row = b"\x00" + bytes(packed)
    return (
        signature
        + chunk(b"IHDR", header)
        + chunk(b"tRNS", transparent_sample.to_bytes(2, "big"))
        + chunk(b"IDAT", zlib.compress(row))
        + chunk(b"IEND", b"")
    )


def jpeg() -> bytes:
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"


class RemoteResponse:
    def __init__(self, body: bytes, headers: dict[str, str] | None = None):
        self.body = body
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit: int = -1) -> bytes:
        return self.body


class ImageGenerationRuntimeTests(unittest.TestCase):
    def write_provider(self, provider_id: str, *, credential_references: dict | None = None, settings: dict | None = None) -> dict:
        trusted = server.canonical_provider(provider_id)
        provider = {
            "id": provider_id,
            "display_name": trusted["display_name"],
            "route": deepcopy(trusted["route"]),
            "capabilities": deepcopy(trusted["capabilities"]),
            "credential_references": credential_references or {},
            "settings": settings or {},
        }
        document = {"schema_version": "1.0.0", "project_id": "test_mod", "providers": {provider_id: provider}}
        (self.root / server.CONFIG_PATH).write_text(json.dumps(document), encoding="utf-8")
        return provider

    def setUp(self) -> None:
        credential_reader = patch.object(server, "read_credential", return_value=None)
        credential_reader.start()
        self.addCleanup(credential_reader.stop)
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / ".hoi4-setup").mkdir()
        self.provider = self.write_provider("automatic1111_local", settings={"server_url": "http://127.0.0.1:7860"})
        self.runtime = server.Server("automatic1111_local", self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_initialize_and_tool_list_are_provider_bound(self) -> None:
        initialized = self.runtime.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": server.MCP_VERSION}})
        self.assertEqual(initialized["result"]["serverInfo"]["name"], self.runtime.route["server_id"])
        tools = self.runtime.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})["result"]["tools"]
        self.assertEqual({tool["name"] for tool in tools}, {"generate_image", "edit_image", "image_auth_status"})
        self.assertNotIn("remove_background", {tool["name"] for tool in tools})

    def test_tool_schema_hides_unsupported_reference_and_alpha_controls(self) -> None:
        self.write_provider("huggingface_inference")
        runtime = server.Server("huggingface_inference", self.root)
        tools = runtime.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})["result"]["tools"]
        generate = next(tool for tool in tools if tool["name"] == "generate_image")
        properties = generate["inputSchema"]["properties"]
        self.assertNotIn("reference_images", properties)
        self.assertNotIn("transparent_background", properties)
        self.assertIn("width", properties)

    def test_model_choice_is_saved_in_setup_settings_and_never_accepted_as_prompt_input(self) -> None:
        self.write_provider("openai_api", settings={"model": "gpt-image-2.5-flare"})
        runtime = server.Server("openai_api", self.root)
        self.assertEqual(runtime.selected_model(), "gpt-image-2.5-flare")
        tool = next(
            item for item in runtime.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/list", "params": {}})["result"]["tools"]
            if item["name"] == "generate_image"
        )
        self.assertNotIn("model", tool["inputSchema"]["properties"])
        with self.assertRaisesRegex(server.ImageRouteError, "listed in the setup provider details"):
            self.write_provider("openai_api", settings={"model": "unreviewed/model"})
            server.Server("openai_api", self.root)

    def test_reference_count_limit_is_enforced_before_provider_calls(self) -> None:
        self.write_provider("automatic1111_local", settings={"server_url": "http://127.0.0.1:7860"})
        runtime = server.Server("automatic1111_local", self.root)
        (self.root / "one.png").write_bytes(png())
        (self.root / "two.png").write_bytes(png())
        with self.assertRaisesRegex(server.ImageRouteError, "up to 1 reference images"):
            runtime.generate_image({"prompt": "combine", "reference_images": ["one.png", "two.png"], "out": "gfx/combined.png"})

    def test_flux_dimensions_obey_the_documented_total_pixel_cap(self) -> None:
        self.write_provider("black_forest_labs")
        runtime = server.Server("black_forest_labs", self.root)
        runtime._validate_size({"width": 2048, "height": 2048})
        with self.assertRaisesRegex(server.ImageRouteError, "total pixel limit"):
            runtime._validate_size({"width": 4096, "height": 4096})

    def test_only_verified_https_and_local_loopback_routes_are_allowed(self) -> None:
        self.assertEqual(server._safe_url("automatic1111_local", "http://127.0.0.1:7860", allow_loopback=True), "http://127.0.0.1:7860")
        self.assertEqual(server._safe_url("vertex_imagen", "https://us-central1-aiplatform.googleapis.com/v1"), "https://us-central1-aiplatform.googleapis.com/v1")
        with self.assertRaisesRegex(server.ImageRouteError, "HTTPS"):
            server._safe_url("openai_api", "http://api.openai.com/v1")
        with self.assertRaisesRegex(server.ImageRouteError, "host list"):
            server._safe_url("openai_api", "https://attacker.example/v1")
        with self.assertRaisesRegex(server.ImageRouteError, "host list"):
            server._safe_url("automatic1111_local", "https://attacker.example")

    def test_provider_api_requests_disable_redirects(self) -> None:
        captured = {}

        class FakeOpener:
            def open(self, request, timeout):
                captured["request"] = request
                captured["timeout"] = timeout
                raise server.urllib.error.HTTPError(request.full_url, 302, "redirect", {}, None)

        def fake_build_opener(*handlers):
            captured["handlers"] = handlers
            return FakeOpener()

        with patch.object(server.urllib.request, "build_opener", side_effect=fake_build_opener):
            with self.assertRaisesRegex(server.ImageRouteError, "provider request failed"):
                self.runtime._request_bytes(
                    "http://127.0.0.1:7860/api", "POST", {"Authorization": "Bearer test-secret"}, b"{}", loopback=True
                )
        self.assertTrue(any(isinstance(handler, server._NoRedirect) for handler in captured["handlers"]))
        self.assertEqual(captured["request"].get_header("Authorization"), "Bearer test-secret")

    def test_save_checks_alpha_and_never_overwrites(self) -> None:
        data = png(color_type=6)
        result = self.runtime.save_output("gfx/generated/one.png", data)
        self.assertTrue(result["alpha"])
        self.assertTrue(result["transparent_pixels"])
        self.assertEqual((self.root / "gfx/generated/one.png").read_bytes(), data)
        with self.assertRaisesRegex(server.ImageRouteError, "already exists"):
            self.runtime.save_output("gfx/generated/one.png", data)
        self.assertFalse(server.png_has_alpha(png(color_type=2)))
        self.assertFalse(server.png_has_transparent_pixels(png(color_type=6, alpha=255)))
        with self.assertRaisesRegex(server.ImageRouteError, "transparent pixels"):
            self.runtime.save_transparent_output("gfx/generated/opaque.png", png(color_type=6, alpha=255))

    def test_packed_grayscale_trns_verifies_decoded_pixel_values(self) -> None:
        for bit_depth in (1, 2, 4):
            with self.subTest(bit_depth=bit_depth):
                for transparent_value, opaque_value in ((0, 1), ((1 << bit_depth) - 1, 0)):
                    with self.subTest(transparent_value=transparent_value):
                        opaque_pixels = [opaque_value] * (8 // bit_depth + 1)
                        transparent_pixels = [opaque_value, transparent_value, opaque_value]
                        self.assertFalse(server.png_has_transparent_pixels(grayscale_trns_png(bit_depth, opaque_pixels, transparent_value)))
                        self.assertTrue(server.png_has_transparent_pixels(grayscale_trns_png(bit_depth, transparent_pixels, transparent_value)))

    def test_reference_and_output_paths_stay_inside_the_project(self) -> None:
        reference_image = png(width=64, height=64)
        (self.root / "reference.png").write_bytes(reference_image)
        name, data = self.runtime.read_reference("reference.png")
        self.assertEqual(name, "reference.png")
        self.assertTrue(data.startswith(b"\x89PNG"))
        for candidate in ("../outside.png", str(self.root / "reference.png")):
            with self.subTest(path=candidate), self.assertRaises(server.ImageRouteError):
                self.runtime.read_reference(candidate)
        with self.assertRaisesRegex(server.ImageRouteError, "inside the current mod"):
            self.runtime.save_output("../outside.png", png())

    def test_remote_proxy_forwards_credentials_only_in_headers(self) -> None:
        self.write_provider("adobe_firefly", credential_references={
            "ims_token": "credential://image_generation_api_key/adobe_firefly_ims_token",
            "service_key": "credential://image_generation_api_key/adobe_firefly_service_key",
        })
        runtime = server.Server("adobe_firefly", self.root)
        runtime.secrets.update({"ims_token": "synthetic-token", "service_key": "synthetic-service-key"})
        request_message = {"jsonrpc": "2.0", "id": 9, "method": "tools/list", "params": {}}
        response_body = json.dumps({"jsonrpc": "2.0", "id": 9, "result": {"tools": []}}).encode()

        def fake_open(request, timeout):
            self.assertEqual(request.get_header("Authorization"), "Bearer synthetic-token")
            self.assertEqual(request.get_header("X-api-key"), "synthetic-service-key")
            self.assertNotIn(b"synthetic-token", request.data)
            self.assertNotIn(b"synthetic-service-key", request.data)
            return RemoteResponse(response_body, {"Content-Type": "application/json", "Mcp-Session-Id": "session-test"})

        class FakeOpener:
            def open(self, request, timeout):
                return fake_open(request, timeout)

        with patch.object(server.urllib.request, "build_opener", lambda *_args: FakeOpener()):
            response = runtime.handle(request_message)
        self.assertEqual(response["id"], 9)
        self.assertEqual(runtime.remote_session_id, "session-test")

    def test_openai_generation_uses_one_image_and_never_puts_the_key_in_the_request_body(self) -> None:
        provider = self.write_provider(
            "openai_api",
            credential_references={"api_key": "credential://image_generation_api_key/openai_api_api_key"},
            settings={"model": "gpt-image-2.5-flare"},
        )
        runtime = server.Server("openai_api", self.root)
        runtime.secrets["api_key"] = "openai-test-secret"
        captured = {}

        def fake_request(url, method, headers, body=None, **kwargs):
            captured.update({"url": url, "method": method, "headers": headers, "body": body})
            return json.dumps({"data": [{"b64_json": base64.b64encode(png()).decode("ascii")}]}).encode()

        runtime._request_bytes = fake_request
        result = runtime.generate_image({"prompt": "a test image", "out": "gfx/generated/openai.png", "transparent_background": True})
        self.assertEqual(result["path"], "gfx/generated/openai.png")
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["headers"]["Authorization"], "Bearer openai-test-secret")
        self.assertNotIn(b"openai-test-secret", captured["body"])
        body = json.loads(captured["body"])
        self.assertEqual(body["model"], "gpt-image-2.5-flare")
        self.assertEqual(body["n"], 1)
        self.assertEqual(body["background"], "transparent")
        self.assertEqual(body["output_format"], "png")
        self.assertNotIn("response_format", body)

    def test_modified_project_route_cannot_redirect_a_saved_api_key(self) -> None:
        provider = self.write_provider("openai_api", credential_references={"api_key": "credential://image_generation_api_key/openai_api_api_key"})
        provider["route"]["api_base_url"] = "https://attacker.example/v1"
        document = {"providers": {"openai_api": provider}}
        (self.root / server.CONFIG_PATH).write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(server.ImageRouteError, "do not match"):
            server.Server("openai_api", self.root)

    def test_image_download_hosts_and_reference_signatures_are_checked(self) -> None:
        self.assertEqual(server._safe_image_download_url("ideogram", "https://ideogram.ai/api/images/image.png"), "https://ideogram.ai/api/images/image.png")
        self.assertEqual(server._safe_image_download_url("fal_ai", "https://storage.googleapis.com/falserverless/out.png"), "https://storage.googleapis.com/falserverless/out.png")
        self.assertEqual(server._safe_image_download_url("xai_grok", "https://imgen.x.ai/result.jpg"), "https://imgen.x.ai/result.jpg")
        for url in ("https://127.0.0.1/secret", "https://attacker.example/image.png", "https://ideogram.ai:8443/image.png"):
            with self.subTest(url=url), self.assertRaises(server.ImageRouteError):
                server._safe_image_download_url("ideogram", url)
        with self.assertRaisesRegex(server.ImageRouteError, "verified image host"):
            server._safe_image_download_url("fal_ai", "https://storage.googleapis.com/other-bucket/out.png")
        with self.assertRaisesRegex(server.ImageRouteError, "valid PNG"):
            server.validate_reference_image("secret.png", b"not really a png")

    def test_openrouter_uses_image_api_with_one_result_and_reference_data(self) -> None:
        self.write_provider("openrouter", credential_references={"api_key": "credential://image_generation_api_key/openrouter_api_key"})
        runtime = server.Server("openrouter", self.root)
        runtime.secrets["api_key"] = "openrouter-secret"
        (self.root / "reference.png").write_bytes(png())
        captured = []

        def fake_json(url, method, headers, payload=None, **_kwargs):
            captured.append({"url": url, "method": method, "headers": headers, "payload": payload})
            return {"data": [{"b64_json": base64.b64encode(png()).decode("ascii"), "media_type": "image/png"}]}

        runtime._request_json = fake_json
        result = runtime.generate_image({"prompt": "a test", "reference_images": ["reference.png"], "out": "gfx/openrouter.png"})
        transparent = runtime.generate_image({"prompt": "a transparent cutout", "transparent_background": True, "out": "gfx/openrouter-alpha.png"})
        self.assertEqual(result["path"], "gfx/openrouter.png")
        self.assertTrue(transparent["transparent_pixels"])
        self.assertTrue(captured[0]["url"].endswith("/api/v1/images"))
        self.assertEqual(captured[0]["headers"]["Authorization"], "Bearer openrouter-secret")
        self.assertNotIn("openrouter-secret", json.dumps(captured[0]["payload"]))
        self.assertEqual(len(captured[0]["payload"]["input_references"]), 1)
        self.assertTrue(captured[0]["payload"]["input_references"][0]["image_url"]["url"].startswith("data:image/png;base64,"))
        self.assertEqual(captured[1]["payload"]["background"], "transparent")
        ratio_result = runtime.generate_image({
            "prompt": "a landscape asset", "aspect_ratio": "16:9", "out": "gfx/openrouter-wide.png",
        })
        self.assertEqual(ratio_result["path"], "gfx/openrouter-wide.png")
        self.assertEqual(captured[2]["payload"]["aspect_ratio"], "16:9")
        with self.assertRaisesRegex(server.ImageRouteError, "aspect ratio"):
            runtime.generate_image({"prompt": "bad ratio", "aspect_ratio": "5:1", "out": "gfx/openrouter-invalid.png"})
        generate_tool = next(
            tool for tool in runtime.handle({"jsonrpc": "2.0", "id": 10, "method": "tools/list", "params": {}})["result"]["tools"]
            if tool["name"] == "generate_image"
        )
        properties = generate_tool["inputSchema"]["properties"]
        self.assertNotIn("width", properties)
        self.assertNotIn("height", properties)
        self.assertEqual(properties["aspect_ratio"]["enum"], list(server.OPENROUTER_ASPECT_RATIOS))
        with self.assertRaisesRegex(server.ImageRouteError, "chooses its own output dimensions"):
            runtime.generate_image({"prompt": "unavailable size", "width": 1024, "height": 1024, "out": "gfx/openrouter-size.png"})

    def test_together_returns_png_base64_and_declines_undocumented_project_reference_uploads(self) -> None:
        self.write_provider("together_ai", credential_references={"api_key": "credential://image_generation_api_key/together_ai_api_key"})
        runtime = server.Server("together_ai", self.root)
        runtime.secrets["api_key"] = "together-secret"
        captured = {}

        def fake_json(url, method, headers, payload=None, **_kwargs):
            captured.update({"url": url, "method": method, "headers": headers, "payload": payload})
            return {"data": [{"b64_json": base64.b64encode(png()).decode("ascii")} ]}

        runtime._request_json = fake_json
        result = runtime.generate_image({"prompt": "a test", "out": "gfx/together.png"})
        self.assertEqual(result["path"], "gfx/together.png")
        self.assertTrue(captured["url"].endswith("/v1/images/generations"))
        self.assertEqual(captured["payload"]["n"], 1)
        self.assertEqual(captured["payload"]["response_format"], "base64")
        self.assertEqual(captured["payload"]["output_format"], "png")
        self.assertEqual(captured["headers"]["Authorization"], "Bearer together-secret")
        (self.root / "reference.png").write_bytes(png())
        with self.assertRaisesRegex(server.ImageRouteError, "does not accept reference images"):
            runtime.generate_image({"prompt": "a test", "reference_images": ["reference.png"], "out": "gfx/together-ref.png"})

    def test_huggingface_text_to_image_uses_provider_router(self) -> None:
        self.write_provider("huggingface_inference", credential_references={"api_key": "credential://image_generation_api_key/huggingface_inference_api_key"})
        runtime = server.Server("huggingface_inference", self.root)
        runtime.secrets["api_key"] = "hf-secret"
        captured = {}

        def fake_bytes(url, method, headers, body=None, **_kwargs):
            captured.update({"url": url, "method": method, "headers": headers, "body": body})
            return png()

        runtime._request_bytes = fake_bytes
        runtime.generate_image({"prompt": "a test", "out": "gfx/hf.png"})
        self.assertTrue(captured["url"].endswith("/hf-inference/models/black-forest-labs/FLUX.1-Krea-dev"))
        self.assertEqual(captured["headers"]["Authorization"], "Bearer hf-secret")
        self.assertEqual(json.loads(captured["body"])["inputs"], "a test")

    def test_ideogram_transparency_and_remix_use_documented_multipart_routes(self) -> None:
        self.write_provider("ideogram", credential_references={"api_key": "credential://image_generation_api_key/ideogram_api_key"})
        runtime = server.Server("ideogram", self.root)
        runtime.secrets["api_key"] = "ideogram-secret"
        (self.root / "reference.png").write_bytes(png())
        calls = []

        def fake_json(url, method, headers, payload=None, **_kwargs):
            calls.append({"url": url, "headers": headers, "body": payload})
            return {"data": [{"b64_json": base64.b64encode(png()).decode("ascii")}]}

        runtime._request_json = fake_json
        transparent = runtime.generate_image({"prompt": "a transparent emblem", "transparent_background": True, "out": "gfx/ideo-alpha.png"})
        edit = runtime.generate_image({"prompt": "redraw this", "reference_images": ["reference.png"], "out": "gfx/ideo-remix.png"})
        self.assertTrue(transparent["alpha"])
        self.assertEqual(edit["path"], "gfx/ideo-remix.png")
        self.assertTrue(calls[0]["url"].endswith("/ideogram-v4/generate-transparent"))
        self.assertTrue(calls[1]["url"].endswith("/ideogram-v4/remix"))
        self.assertEqual(calls[0]["headers"]["Api-Key"], "ideogram-secret")
        self.assertIn(b"text_prompt", calls[1]["body"])
        self.assertIn(b"reference.png", calls[1]["body"])

    def test_recraft_image_edit_and_background_removal_are_saved_as_png(self) -> None:
        self.write_provider("recraft", credential_references={"api_key": "credential://image_generation_api_key/recraft_api_key"})
        runtime = server.Server("recraft", self.root)
        runtime.secrets["api_key"] = "recraft-secret"
        (self.root / "reference.png").write_bytes(png())
        calls = []

        def fake_json(url, method, headers, payload=None, **_kwargs):
            calls.append({"url": url, "payload": payload, "headers": headers})
            if url.endswith("removeBackground"):
                return {"image": {"b64_json": base64.b64encode(png()).decode("ascii")}}
            return {"data": [{"b64_json": base64.b64encode(png()).decode("ascii")}]}

        runtime._request_json = fake_json
        result = runtime.call_tool("edit_image", {"prompt": "make this an ink drawing", "image": "reference.png", "out": "gfx/recraft-edit.png"})
        removal = runtime.remove_background({"image": "reference.png", "out": "gfx/recraft-cutout.png"})
        self.assertEqual(result["path"], "gfx/recraft-edit.png")
        self.assertTrue(removal["alpha"])
        self.assertTrue(calls[0]["url"].endswith("/images/imageToImage"))
        self.assertTrue(calls[0]["payload"]["image_url"].startswith("data:image/png;base64,"))
        self.assertEqual(calls[0]["payload"]["n"], 1)
        self.assertTrue(calls[1]["url"].endswith("/images/removeBackground"))
        self.assertEqual(calls[1]["payload"]["image_format"], "png")

    def test_stability_image_to_image_uses_the_reference_filename(self) -> None:
        self.write_provider("stability_ai", credential_references={"api_key": "credential://image_generation_api_key/stability_ai_api_key"})
        runtime = server.Server("stability_ai", self.root)
        runtime.secrets["api_key"] = "stability-secret"
        (self.root / "reference.png").write_bytes(png())
        captured = {}

        def fake_bytes(url, method, headers, body=None, **_kwargs):
            captured.update({"url": url, "method": method, "headers": headers, "body": body})
            return png()

        runtime._request_bytes = fake_bytes
        result = runtime.generate_image({"prompt": "redraw the reference", "reference_images": ["reference.png"], "out": "gfx/stability-edit.png"})
        self.assertEqual(result["path"], "gfx/stability-edit.png")
        self.assertTrue(captured["url"].endswith("/stable-image/edit/image-to-image"))
        self.assertIn(b'filename="reference.png"', captured["body"])
        self.assertEqual(captured["headers"]["Authorization"], "Bearer stability-secret")
        self.assertNotIn(b"stability-secret", captured["body"])

    def test_aws_bedrock_uses_stability_payloads_for_generation_edits_and_cutouts(self) -> None:
        self.write_provider(
            "aws_bedrock",
            credential_references={
                "access_key": "credential://image_generation_api_key/aws_bedrock_access_key",
                "secret_key": "credential://image_generation_api_key/aws_bedrock_secret_key",
            },
            settings={"region": "us-west-2"},
        )
        runtime = server.Server("aws_bedrock", self.root)
        runtime.secrets.update({"access_key": "aws-access", "secret_key": "aws-secret"})
        reference_image = png(width=64, height=64)
        (self.root / "reference.png").write_bytes(reference_image)
        calls = []

        def fake_json(url, method, headers, payload=None, **_kwargs):
            calls.append({"url": url, "method": method, "headers": headers, "payload": payload})
            return {"images": [base64.b64encode(png()).decode("ascii")]}

        runtime._request_json = fake_json
        generated = runtime.generate_image({"prompt": "an archival image", "out": "gfx/aws-generated.png"})
        edited = runtime.call_tool("edit_image", {"prompt": "redraw with a different uniform", "image": "reference.png", "out": "gfx/aws-edit.png"})
        removed = runtime.remove_background({"image": "reference.png", "out": "gfx/aws-cutout.png"})
        self.assertEqual(generated["path"], "gfx/aws-generated.png")
        self.assertEqual(edited["path"], "gfx/aws-edit.png")
        self.assertTrue(removed["transparent_pixels"])
        self.assertEqual(calls[0]["payload"], {"prompt": "an archival image", "output_format": "png"})
        self.assertIn("bedrock-runtime.us-west-2.amazonaws.com", calls[0]["url"])
        self.assertTrue(calls[0]["headers"]["Authorization"].startswith("AWS4-HMAC-SHA256"))
        self.assertEqual(calls[1]["payload"]["strength"], 0.35)
        self.assertEqual(calls[1]["payload"]["image"], base64.b64encode(reference_image).decode("ascii"))
        self.assertTrue(calls[2]["url"].endswith("stability.stable-image-remove-background-v1:0/invoke"))
        self.assertEqual(calls[2]["payload"], {"image": base64.b64encode(reference_image).decode("ascii")})
        (self.root / "too-small.png").write_bytes(png(width=32, height=64))
        with self.assertRaisesRegex(server.ImageRouteError, "at least 64 pixels"):
            runtime.remove_background({"image": "too-small.png", "out": "gfx/aws-small-cutout.png"})

    def test_bedrock_core_hides_and_rejects_reference_edits_but_ultra_exposes_them(self) -> None:
        credentials = {
            "access_key": "credential://image_generation_api_key/aws_bedrock_access_key",
            "secret_key": "credential://image_generation_api_key/aws_bedrock_secret_key",
        }
        self.write_provider(
            "aws_bedrock",
            credential_references=credentials,
            settings={"region": "us-west-2", "model": "stability.stable-image-core-v1:1"},
        )
        core = server.Server("aws_bedrock", self.root)
        core_tools = core.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})["result"]["tools"]
        self.assertNotIn("edit_image", {tool["name"] for tool in core_tools})
        core_generate = next(tool for tool in core_tools if tool["name"] == "generate_image")
        self.assertNotIn("reference_images", core_generate["inputSchema"]["properties"])
        with self.assertRaisesRegex(server.ImageRouteError, "does not support image edits"):
            core.call_tool("edit_image", {"prompt": "edit", "image": "reference.png", "out": "gfx/core-edit.png"})
        with self.assertRaisesRegex(server.ImageRouteError, "does not accept reference images"):
            core.generate_image({"prompt": "edit", "reference_images": ["reference.png"], "out": "gfx/core-reference.png"})

        self.write_provider(
            "aws_bedrock",
            credential_references=credentials,
            settings={"region": "us-west-2", "model": "stability.stable-image-ultra-v1:1"},
        )
        ultra = server.Server("aws_bedrock", self.root)
        ultra_tools = ultra.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})["result"]["tools"]
        self.assertIn("edit_image", {tool["name"] for tool in ultra_tools})
        ultra_generate = next(tool for tool in ultra_tools if tool["name"] == "generate_image")
        self.assertIn("reference_images", ultra_generate["inputSchema"]["properties"])

    def test_leonardo_polls_generation_and_saves_the_result(self) -> None:
        self.write_provider("leonardo", credential_references={"api_key": "credential://image_generation_api_key/leonardo_api_key"})
        runtime = server.Server("leonardo", self.root)
        runtime.secrets["api_key"] = "leonardo-secret"
        calls = []

        def fake_json(url, method, headers, payload=None, **_kwargs):
            calls.append({"url": url, "method": method, "headers": headers, "payload": payload})
            if method == "POST":
                return {"sdGenerationJob": {"generationId": "00000000-0000-4000-8000-000000000000"}}
            return {"generations_by_pk": {"generated_images": [{"b64_json": base64.b64encode(png()).decode("ascii")}]}}

        runtime._request_json = fake_json
        result = runtime.generate_image({"prompt": "a test", "out": "gfx/leonardo.png"})
        self.assertEqual(result["path"], "gfx/leonardo.png")
        self.assertTrue(calls[0]["url"].endswith("/generations"))
        self.assertTrue(calls[1]["url"].endswith("/generations/00000000-0000-4000-8000-000000000000"))
        self.assertEqual(calls[0]["payload"]["modelId"], "7b592283-e8a7-4c5a-9ba6-d18c31f258b9")

    def test_fal_waits_for_queue_result_before_saving_one_image(self) -> None:
        self.write_provider("fal_ai", credential_references={"api_key": "credential://image_generation_api_key/fal_ai_api_key"})
        runtime = server.Server("fal_ai", self.root)
        runtime.secrets["api_key"] = "fal-secret"
        calls = []

        def fake_json(url, method, headers, payload=None, **_kwargs):
            calls.append({"url": url, "method": method, "headers": headers, "payload": payload})
            if method == "POST":
                return {
                    "request_id": "request-1",
                    "status_url": "https://queue.fal.run/fal-ai/flux-2-pro/requests/request-1/status",
                    "response_url": "https://queue.fal.run/fal-ai/flux-2-pro/requests/request-1",
                }
            if url.endswith("/status"):
                return {"status": "COMPLETED"}
            return {"images": [{"url": "https://storage.googleapis.com/falserverless/out.png"}]}

        runtime._request_json = fake_json
        runtime._image_from_response = lambda _response: png()
        with patch.object(server.time, "sleep", lambda _seconds: None):
            result = runtime.generate_image({"prompt": "a test", "out": "gfx/fal.png"})
        self.assertEqual(result["path"], "gfx/fal.png")
        self.assertEqual([call["method"] for call in calls], ["POST", "GET", "GET"])
        self.assertTrue(calls[0]["url"].endswith("/fal-ai/flux-2-pro"))
        self.assertNotIn("num_images", calls[0]["payload"])
        self.assertEqual(calls[0]["headers"]["Authorization"], "Key fal-secret")

    def test_every_fal_model_uses_its_documented_generation_payload(self) -> None:
        cases = {
            "fal-ai/flux-2-pro": {"image_size": "square_hd", "output_format": "png"},
            "fal-ai/flux-2-flex": {"image_size": "square_hd", "output_format": "png"},
            "fal-ai/flux/dev": {"image_size": "square_hd", "num_images": 1, "output_format": "png"},
            "fal-ai/flux/schnell": {"image_size": "square_hd", "num_images": 1, "output_format": "png"},
            "fal-ai/bytedance/seedream/v4.5/text-to-image": {"image_size": "auto_2K", "num_images": 1, "max_images": 1},
            "fal-ai/nano-banana-2": {"num_images": 1, "output_format": "png", "limit_generations": True, "resolution": "1K"},
            "fal-ai/nano-banana-pro": {"num_images": 1, "output_format": "png", "limit_generations": True, "resolution": "1K"},
            "fal-ai/recraft/v4/text-to-image": {"image_size": "square_hd"},
            "fal-ai/ideogram/v3": {"image_size": "square_hd", "num_images": 1},
            "fal-ai/ideogram/v3/generate-transparent": {"num_images": 1},
        }
        self.assertEqual(set(cases), set(server.canonical_provider("fal_ai")["route"]["supported_models"]))
        for index, (model, expected) in enumerate(cases.items()):
            with self.subTest(model=model):
                self.write_provider("fal_ai", settings={"model": model})
                runtime = server.Server("fal_ai", self.root)
                runtime.secrets["api_key"] = "test-only-key"
                webp = b"RIFF" + (8).to_bytes(4, "little") + b"WEBPVP8 "
                output = webp if "recraft" in model else png()
                suffix = "webp" if "recraft" in model else "png"
                with patch.object(runtime, "_request_json", return_value={"images": [{"b64_json": base64.b64encode(output).decode("ascii")}]}) as request:
                    result = runtime.generate_image({"prompt": "one asset", "out": f"gfx/fal-{index}.{suffix}"})
                self.assertEqual(request.call_args.args[0], "https://queue.fal.run/" + model)
                self.assertEqual(request.call_args.args[3], {"prompt": "one asset", **expected})
                self.assertEqual(result["format"], suffix)
                self.assertNotIn("test-only-key", json.dumps(result))

    def test_fal_edit_routes_are_explicit_and_send_a_contained_data_uri(self) -> None:
        (self.root / "source.png").write_bytes(png())
        cases = {
            "fal-ai/flux-2-pro": "fal-ai/flux-2-pro/edit",
            "fal-ai/flux-2-flex": "fal-ai/flux-2-flex/edit",
            "fal-ai/bytedance/seedream/v4.5/text-to-image": "fal-ai/bytedance/seedream/v4.5/edit",
            "fal-ai/nano-banana-2": "fal-ai/nano-banana-2/edit",
            "fal-ai/nano-banana-pro": "fal-ai/nano-banana-pro/edit",
        }
        for index, (model, endpoint) in enumerate(cases.items()):
            with self.subTest(model=model):
                self.write_provider("fal_ai", settings={"model": model})
                runtime = server.Server("fal_ai", self.root)
                runtime.secrets["api_key"] = "test-only-key"
                with patch.object(runtime, "_request_json", return_value={"images": [{"b64_json": base64.b64encode(png()).decode("ascii")}]}) as request:
                    runtime.call_tool("edit_image", {"prompt": "new style", "image": "source.png", "out": f"gfx/edit-{index}.png"})
                self.assertEqual(request.call_args.args[0], "https://queue.fal.run/" + endpoint)
                self.assertEqual(request.call_args.args[3]["image_urls"], [runtime._data_url(png(), "image/png")])
                with patch.object(runtime, "_request_json") as request:
                    with self.assertRaisesRegex(server.ImageRouteError, "one source image"):
                        runtime.call_tool("edit_image", {"prompt": "new style", "image": "source.png", "reference_images": ["source.png", "extra.png"], "out": "gfx/extra.png"})
                request.assert_not_called()

    def test_fal_model_schema_and_invalid_combinations_fail_before_network(self) -> None:
        cases = [
            ("fal-ai/flux/dev", {"reference_images": ["source.png"]}),
            ("fal-ai/flux/schnell", {"_hoi4_edit_request": True, "image": "source.png"}),
            ("fal-ai/recraft/v4/text-to-image", {"_hoi4_edit_request": True, "image": "source.png", "out": "out.webp"}),
            ("fal-ai/recraft/v4/text-to-image", {"out": "out.png"}),
            ("fal-ai/ideogram/v3", {"reference_images": ["source.png"]}),
            ("fal-ai/ideogram/v3/generate-transparent", {"reference_images": ["source.png"]}),
            ("fal-ai/flux-2-flex", {"transparent_background": True}),
            ("fal-ai/flux-2-pro", {"width": 2560, "height": 2560}),
            ("fal-ai/flux-2-pro", {"width": 1025, "height": 1024}),
            ("fal-ai/flux-2-pro", {"width": 1024}),
            ("fal-ai/bytedance/seedream/v4.5/text-to-image", {"width": 1024, "height": 1024}),
            ("fal-ai/bytedance/seedream/v4.5/text-to-image", {"width": 4097, "height": 2048}),
            ("fal-ai/nano-banana-2", {"width": 1024, "height": 1024}),
            ("fal-ai/nano-banana-2", {"resolution": "8K"}),
            ("fal-ai/nano-banana-pro", {"resolution": "0.5K"}),
            ("fal-ai/nano-banana-pro", {"aspect_ratio": "8:1"}),
            ("fal-ai/flux-2-pro", {"aspect_ratio": "1:1"}),
            ("fal-ai/nano-banana-2", {"reference_images": ["../outside.png"]}),
            ("fal-ai/nano-banana-2", {"reference_images": ["source.png", "source.png"]}),
        ]
        for model, options in cases:
            with self.subTest(model=model, options=options):
                self.write_provider("fal_ai", settings={"model": model})
                runtime = server.Server("fal_ai", self.root)
                with patch.object(runtime, "_request_json") as request:
                    with self.assertRaises(server.ImageRouteError):
                        runtime.generate_image({"prompt": "one asset", "out": "out.png", **options})
                request.assert_not_called()
        for model in server.canonical_provider("fal_ai")["route"]["supported_models"]:
            self.write_provider("fal_ai", settings={"model": model})
            runtime = server.Server("fal_ai", self.root)
            tools = server._local_tools(runtime.provider)
            props = next(tool["inputSchema"]["properties"] for tool in tools if tool["name"] == "generate_image")
            supports_edit = model in {"fal-ai/flux-2-pro", "fal-ai/flux-2-flex", "fal-ai/bytedance/seedream/v4.5/text-to-image", "fal-ai/nano-banana-2", "fal-ai/nano-banana-pro"}
            self.assertEqual("reference_images" in props, supports_edit)
            self.assertEqual(any(tool["name"] == "edit_image" for tool in tools), supports_edit)
            self.assertEqual("transparent_background" in props, model.endswith("generate-transparent"))
            self.assertEqual("resolution" in props, "nano-banana" in model)
            self.assertEqual("width" in props, "/flux" in model or "seedream" in model)

    def test_fal_tiers_dimensions_and_transparency_are_model_bound(self) -> None:
        cases = [
            ("fal-ai/nano-banana-2", {"resolution": "0.5K", "aspect_ratio": "8:1"}, {"resolution": "0.5K", "aspect_ratio": "8:1"}),
            ("fal-ai/nano-banana-pro", {"resolution": "4K", "aspect_ratio": "3:2"}, {"resolution": "4K", "aspect_ratio": "3:2"}),
            ("fal-ai/bytedance/seedream/v4.5/text-to-image", {"width": 2048, "height": 2048}, {"image_size": {"width": 2048, "height": 2048}}),
        ]
        for index, (model, options, expected) in enumerate(cases):
            self.write_provider("fal_ai", settings={"model": model})
            runtime = server.Server("fal_ai", self.root)
            runtime.secrets["api_key"] = "test-only-key"
            with patch.object(runtime, "_request_json", return_value={"images": [{"b64_json": base64.b64encode(png()).decode("ascii")}]}) as request:
                runtime.generate_image({"prompt": "one asset", "out": f"gfx/tier-{index}.png", **options})
            for key, value in expected.items():
                self.assertEqual(request.call_args.args[3][key], value)
        self.write_provider("fal_ai", settings={"model": "fal-ai/ideogram/v3/generate-transparent"})
        runtime = server.Server("fal_ai", self.root)
        runtime.secrets["api_key"] = "test-only-key"
        with patch.object(runtime, "_request_json", return_value={"images": [{"b64_json": base64.b64encode(png(alpha=255)).decode("ascii")}]}):
            with self.assertRaisesRegex(server.ImageRouteError, "transparent pixels"):
                runtime.generate_image({"prompt": "one asset", "out": "gfx/opaque.png"})
        self.assertFalse((self.root / "gfx/opaque.png").exists())

    def test_fal_queue_rejects_untrusted_urls_failed_jobs_and_multiple_outputs(self) -> None:
        self.write_provider("fal_ai", settings={"model": "fal-ai/nano-banana-2"})
        runtime = server.Server("fal_ai", self.root)
        runtime.secrets["api_key"] = "test-only-key"
        responses = [
            {"request_id": "id", "status_url": "https://untrusted.example/status", "response_url": "https://queue.fal.run/result"},
            {"images": [{"url": "https://untrusted.example/image.png"}]},
            {"images": [{"url": runtime._data_url(png())}, {"url": runtime._data_url(png())}]},
            {"images": []},
        ]
        for response in responses:
            with self.subTest(response=response), patch.object(runtime, "_request_json", return_value=response):
                with self.assertRaises(server.ImageRouteError):
                    runtime.generate_image({"prompt": "one asset", "out": "gfx/rejected.png"})
        queued = {"request_id": "id", "status_url": "https://queue.fal.run/status", "response_url": "https://queue.fal.run/result"}
        with patch.object(runtime, "_request_json", side_effect=[queued, {"status": "FAILED"}]) as request:
            with self.assertRaisesRegex(server.ImageRouteError, "could not complete"):
                runtime.generate_image({"prompt": "one asset", "out": "gfx/rejected.png"})
        self.assertEqual(request.call_count, 2)
        with patch.object(runtime, "_request_json", side_effect=[queued] + [{"status": "IN_QUEUE"}] * 120) as request, patch.object(server.time, "sleep"):
            with self.assertRaisesRegex(server.ImageRouteError, "still preparing"):
                runtime.generate_image({"prompt": "one asset", "out": "gfx/rejected.png"})
        self.assertEqual(request.call_count, 121)
        self.assertFalse((self.root / "gfx/rejected.png").exists())

    def test_model_profiles_cannot_be_overridden_by_project_settings(self) -> None:
        self.write_provider("fal_ai", settings={"model": "fal-ai/flux/schnell"})
        path = self.root / server.CONFIG_PATH
        document = json.loads(path.read_text(encoding="utf-8"))
        document["providers"]["fal_ai"]["_model_profiles"] = {"fal-ai/flux/schnell": {"edit_endpoint": "untrusted/edit"}}
        path.write_text(json.dumps(document), encoding="utf-8")
        runtime = server.Server("fal_ai", self.root)
        self.assertIsNone(server._model_profile(runtime.provider)["edit_endpoint"])
        with patch.object(runtime, "_request_json") as request:
            with self.assertRaisesRegex(server.ImageRouteError, "does not support image edits"):
                runtime.call_tool("edit_image", {"prompt": "one asset", "image": "source.png", "out": "gfx/rejected.png"})
        request.assert_not_called()

    def test_replicate_and_together_models_use_reviewed_count_and_model_fields(self) -> None:
        for provider_id in ("replicate", "together_ai"):
            models = server.canonical_provider(provider_id)["route"]["supported_models"]
            for index, model in enumerate(models):
                with self.subTest(provider=provider_id, model=model):
                    self.write_provider(provider_id, settings={"model": model})
                    runtime = server.Server(provider_id, self.root)
                    runtime.secrets["api_key"] = "test-only-key"
                    image = base64.b64encode(png()).decode("ascii")
                    response = {"status": "succeeded", "output": [image]} if provider_id == "replicate" else {"data": [{"b64_json": image}]}
                    with patch.object(runtime, "_request_json", return_value=response) as request:
                        runtime.generate_image({"prompt": "one asset", "out": f"gfx/{provider_id}-{index}.png"})
                    payload = request.call_args.args[3]
                    if provider_id == "replicate":
                        self.assertEqual(request.call_args.args[0], f"https://api.replicate.com/v1/models/{model}/predictions")
                        expected = {"prompt": "one asset", "output_format": "png"}
                        if model != "black-forest-labs/flux-1.1-pro":
                            expected["num_outputs"] = 1
                        self.assertEqual(payload["input"], expected)
                    else:
                        self.assertEqual(payload["model"], model)
                        self.assertEqual(payload["n"], 1)
                        self.assertEqual(payload["response_format"], "base64")
                        self.assertEqual(payload["output_format"], "png")
                        self.assertEqual("steps" in payload, model.endswith("FLUX.2-dev"))
                    with patch.object(runtime, "_request_json") as request:
                        for invalid in ({"reference_images": ["source.png"]}, {"transparent_background": True}):
                            with self.assertRaises(server.ImageRouteError):
                                runtime.generate_image({"prompt": "one asset", "out": "out.png", **invalid})
                    request.assert_not_called()

    def test_gemini_key_is_sent_in_header_not_url(self) -> None:
        self.write_provider("gemini_api", credential_references={"api_key": "credential://image_generation_api_key/gemini_api_api_key"})
        runtime = server.Server("gemini_api", self.root)
        runtime.secrets["api_key"] = "gemini-secret"
        captured = {}

        def fake_json(url, method, headers, payload=None, **_kwargs):
            captured.update({"url": url, "headers": headers, "payload": payload})
            image = base64.b64encode(png()).decode("ascii")
            return {"candidates": [{"content": {"parts": [{"inlineData": {"data": image}}]}}]}

        runtime._request_json = fake_json
        runtime.generate_image({"prompt": "a test", "out": "gfx/gemini.png"})
        self.assertNotIn("gemini-secret", captured["url"])
        self.assertEqual(captured["headers"]["x-goog-api-key"], "gemini-secret")
        self.assertIn("/models/gemini-nano-banana-2.1:generateContent", captured["url"])
        self.assertEqual(captured["payload"]["generationConfig"]["responseModalities"], ["IMAGE"])

    def test_xai_edits_use_json_data_urls_and_preserve_jpeg_format(self) -> None:
        self.write_provider("xai_grok", credential_references={"api_key": "credential://image_generation_api_key/xai_grok_api_key"})
        runtime = server.Server("xai_grok", self.root)
        runtime.secrets["api_key"] = "xai-secret"
        (self.root / "reference.png").write_bytes(png())
        captured = {}

        def fake_json(url, method, headers, payload=None, **_kwargs):
            captured.update({"url": url, "headers": headers, "payload": payload})
            return {"data": [{"url": "https://imgen.x.ai/test.jpeg", "mime_type": "image/jpeg"}]}

        runtime._request_json = fake_json
        runtime._image_from_response = lambda _response: jpeg()
        result = runtime.call_tool("edit_image", {"prompt": "edit this", "image": "reference.png", "out": "gfx/xai.jpg"})
        self.assertEqual(result["format"], "jpeg")
        self.assertFalse(result["alpha"])
        self.assertTrue(captured["url"].endswith("/images/edits"))
        self.assertNotIn("n", captured["payload"])
        self.assertEqual(captured["payload"]["image"]["type"], "image_url")
        self.assertTrue(captured["payload"]["image"]["url"].startswith("data:image/png;base64,"))
        self.assertNotIn("xai-secret", json.dumps(captured["payload"]))

    def test_non_png_outputs_must_use_matching_file_extensions(self) -> None:
        result = self.runtime.save_output("gfx/generated/one.jpg", jpeg())
        self.assertEqual(result["format"], "jpeg")
        with self.assertRaisesRegex(server.ImageRouteError, "matching output file extension"):
            self.runtime.save_output("gfx/generated/mismatch.png", jpeg())

    def test_microsoft_foundry_uses_the_saved_endpoint_and_model_deployment(self) -> None:
        self.write_provider(
            "microsoft_foundry",
            credential_references={
                "resource_url": "credential://image_generation_api_key/microsoft_foundry_resource_url",
                "api_key": "credential://image_generation_api_key/microsoft_foundry_api_key",
            },
            settings={"deployment_name": "my-image-deployment"},
        )
        runtime = server.Server("microsoft_foundry", self.root)
        runtime.secrets.update({"resource_url": "https://myresource.services.ai.azure.com", "api_key": "foundry-secret"})
        captured = {}

        def fake_bytes(url, method, headers, body=None, **_kwargs):
            captured.update({"url": url, "method": method, "headers": headers, "body": body})
            return json.dumps({"data": [{"b64_json": base64.b64encode(png()).decode("ascii")}]}).encode()

        runtime._request_bytes = fake_bytes
        runtime.generate_image({"prompt": "a test", "out": "gfx/foundry.png"})
        payload = json.loads(captured["body"])
        self.assertTrue(captured["url"].endswith("/mai/v1/images/generations"))
        self.assertEqual(captured["headers"]["api-key"], "foundry-secret")
        self.assertEqual(payload["model"], "my-image-deployment")

    def test_sse_parser_reads_mcp_messages(self) -> None:
        messages = server._sse_json(b"event: message\ndata: {\"jsonrpc\":\"2.0\",\"id\":4,\"result\":{}}\n\n")
        self.assertEqual(messages[0]["id"], 4)

    def test_sse_parser_reads_multiple_crlf_delimited_messages(self) -> None:
        body = (
            b"event: message\r\ndata: {\"jsonrpc\":\"2.0\",\"id\":4,\"result\":{}}\r\n\r\n"
            b"event: message\r\ndata: {\"jsonrpc\":\"2.0\",\"id\":5,\"result\":{}}\r\n\r\n"
        )
        messages = server._sse_json(body)
        self.assertEqual([message["id"] for message in messages], [4, 5])

    def test_windows_vault_reference_matches_the_setup_app_keyring_target(self) -> None:
        reference = "credential://image_generation_api_key/project_openai_api_key"
        self.assertEqual(server.keyring_target_name(reference), f"{reference}.{server.KEYRING_SERVICE}")


if __name__ == "__main__":
    unittest.main()
