"""Pinned Meshy MCP client used by the autonomous job runner.

The client starts only the external app-owned launcher materialized by the
repository bootstrap. Project wrappers and direct REST/API fallbacks are not
credential routes.
"""

from __future__ import annotations

import json
import math
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from lib.credits import request_fingerprint
from lib.generation import (
    load_contract,
    locked_server_version,
    operation_credits,
    validate_generation,
)
from lib.mcp_stdio import MCPRouteError, call_stdio
from lib.paths import (
    append_history,
    file_record,
    job_path,
    redact,
    utc_now,
    write_json,
)


REQUIRED_KEY_MESSAGE = (
    "MESHY_API_KEY is missing or blank. Stop. Run this PowerShell command, "
    "then restart the shell or Codex:\n\n"
    '[Environment]::SetEnvironmentVariable(\n'
    '    "MESHY_API_KEY",\n'
    '    "msy_your_actual_key_here",\n'
    '    "User"\n'
    ")\n"
)


# Optional Text-to-Motion tools as 0.6.7 registers them, with the arguments the client sends.
MOTION_TOOL_ARGUMENTS: Dict[str, set] = {
    "meshy_text_to_motion": {"prompt", "mode", "duration"},
    "meshy_list_animations": set(),
    "meshy_get_task_status": {"task_id", "task_type"},
    "meshy_list_tasks": {"task_type", "limit", "offset"},
    "meshy_download_model": {"task_id", "task_type", "save_to"},
}


class MeshyTaskFailed(MCPRouteError):
    """Carry the provider's final task payload into immutable failure evidence."""

    def __init__(self, task_id: str, status: str, final: Dict[str, Any]):
        super().__init__(f"Meshy task {task_id} ended in {status}.")
        self.task_id = task_id
        self.status = status
        self.final = final


def require_meshy_key() -> None:
    """Hard gate before any provider or downstream work."""

    if not os.environ.get("MESHY_API_KEY", "").strip():
        raise RuntimeError(REQUIRED_KEY_MESSAGE)


def _walk(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _payload(result: Dict[str, Any]) -> Dict[str, Any]:
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        return structured
    for item in result.get("content", []):
        if isinstance(item, dict) and item.get("type") == "text":
            text = item.get("text", "")
            try:
                decoded = json.loads(text)
            except (TypeError, json.JSONDecodeError):
                continue
            if isinstance(decoded, dict):
                return decoded
    return result


def _first_key(value: Any, names: Tuple[str, ...]) -> Optional[Any]:
    for key, item in _walk(value):
        if key.lower() in names:
            return item
    return None


def provider_error_text(result: Dict[str, Any]) -> str:
    """The text of an MCP error result, such as Meshy's 402 refusal on the free plan."""
    parts = [item.get("text", "") for item in result.get("content") or [] if isinstance(item, dict)]
    return " ".join(part.strip() for part in parts if part.strip()) or "no error text"


def task_id_from(result: Dict[str, Any]) -> str:
    if result.get("isError"):
        raise MCPRouteError(f"Meshy refused the request: {provider_error_text(result)}")
    value = _first_key(result, ("task_id", "taskid", "id"))
    if not value:
        payload = _payload(result)
        if isinstance(payload.get("result"), str):
            value = payload["result"]
    if not value:
        raise MCPRouteError("Meshy response did not contain a task id.")
    return str(value)


def status_from(result: Dict[str, Any]) -> str:
    value = _first_key(result, ("status", "state"))
    return str(value or "UNKNOWN").upper()


def server_version() -> str:
    """The Meshy MCP version in use: the launcher's report, else the reviewed schema lock."""

    return os.environ.get("MESHY_MCP_VERSION") or locked_server_version()


def image_to_3d_arguments(
    image_path: Path,
    generation: Dict[str, Any],
    pose_mode: Optional[str],
) -> Dict[str, Any]:
    """The meshy_image_to_3d request for one profile's validated generation settings."""

    smart = generation["model_type"] == "smart-topology"
    arguments: Dict[str, Any] = {
        "file_path": str(image_path),
        "ai_model": generation["ai_model"],
        "model_type": generation["model_type"],
        "enable_pbr": generation["enable_pbr"],
        "topology": "triangle",
    }
    if generation["target_polycount"] is not None:
        arguments["target_polycount"] = generation["target_polycount"]
    if not smart:
        arguments["should_remesh"] = generation["should_remesh"]
    arguments["should_texture"] = True
    arguments["texture_resolution"] = generation["texture_resolution"]
    # Meshy answers 400 to image_enhancement on Smart Topology and on the lite model.
    if not smart and generation["ai_model"] != "meshy-6-lite":
        arguments["image_enhancement"] = True
    arguments.update(
        {
            "target_formats": ["glb", "fbx"],
            "multi_view_thumbnails": False,
            "response_format": "json",
        }
    )
    if pose_mode:
        arguments["pose_mode"] = pose_mode
    return arguments


def rig_arguments(
    input_task_id: Optional[str],
    model_url: Optional[str],
    height_meters: float,
) -> Dict[str, Any]:
    """The meshy_rig request. The deprecated texture_image_url is never sent: it drops the PBR maps."""

    if bool(input_task_id) == bool(model_url):
        raise ValueError("Meshy rigging requires exactly one of input_task_id or model_url.")
    arguments: Dict[str, Any] = {"height_meters": height_meters, "response_format": "json"}
    if input_task_id:
        arguments["input_task_id"] = input_task_id
    if model_url:
        arguments["model_url"] = model_url
    return arguments


def remesh_arguments(input_task_id: str, target_polycount: int) -> Dict[str, Any]:
    return {
        "input_task_id": input_task_id,
        "target_formats": ["glb", "fbx"],
        "topology": "triangle",
        "target_polycount": target_polycount,
        "response_format": "json",
    }


def animate_arguments(
    rig_task_id: str,
    action_id: Optional[int],
    motion_task_id: Optional[str],
) -> Dict[str, Any]:
    if (action_id is None) == (motion_task_id is None):
        raise ValueError("Animation requires exactly one of action_id or motion_task_id.")
    arguments: Dict[str, Any] = {"rig_task_id": rig_task_id, "response_format": "json"}
    arguments.update({"action_id": action_id} if action_id is not None else {"motion_task_id": motion_task_id})
    return arguments


def refuse_forbidden_arguments(tool: str, arguments: Dict[str, Any]) -> None:
    """Stop a call that carries an argument the tool contract forbids (absent or false is fine)."""

    forbidden = load_contract()["required_tools"].get(tool, {}).get("forbidden_arguments", [])
    present = [name for name in forbidden if arguments.get(name)]
    if present:
        raise ValueError(f"{tool} must not be called with {present}: the Meshy tool contract forbids it.")


class MeshyClient:
    """Evidence-recording client for the verified Meshy MCP server."""

    def __init__(self, repo_root: Path, job_root: Optional[Path] = None):
        require_meshy_key()
        self.repo_root = repo_root.resolve()
        self.job_root = job_root.resolve() if job_root else None
        config_path = self.repo_root / ".codex" / "config.toml"
        if not config_path.is_file():
            raise FileNotFoundError(
                f"Reviewed MCP config is missing: {config_path}. Run bootstrap_3d_workflow.py."
            )
        route: Dict[str, Any] = {}
        in_meshy_section = False
        for line in config_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("["):
                in_meshy_section = stripped == "[mcp_servers.meshy]"
                continue
            if not in_meshy_section or not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, raw_value = (part.strip() for part in stripped.split("=", 1))
            try:
                route[key] = json.loads(raw_value)
            except json.JSONDecodeError as exc:
                raise MCPRouteError(f"Unsupported reviewed Meshy route value for {key}.") from exc
        launcher_value = route.get("command")
        route_args = route.get("args")
        if not isinstance(launcher_value, str) or not isinstance(route_args, list):
            raise MCPRouteError("The reviewed Meshy MCP route is incomplete.")
        self.launcher = Path(launcher_value).resolve()
        if (
            not self.launcher.is_absolute()
            or not self.launcher.is_file()
            or self.repo_root == self.launcher
            or self.repo_root in self.launcher.parents
            or route_args != ["--run-verified-meshy-mcp"]
        ):
            raise MCPRouteError(
                "Meshy must use the external app-owned launcher with only "
                "--run-verified-meshy-mcp."
            )
        if self.job_root is not None:
            self.sequence = len(list((self.job_root / "provider" / "requests").glob("*.json")))
        else:
            self.sequence = 0

    def _command(self) -> list[str]:
        return [str(self.launcher), "--run-verified-meshy-mcp"]

    def _record(
        self,
        tool: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any],
        *,
        paid: bool,
        estimate_credits: Optional[int] = None,
    ) -> Dict[str, Any]:
        self.sequence += 1
        stamp = f"{self.sequence:03d}_{tool}"
        redacted_arguments = redact(arguments)
        redacted_result = redact(result)
        record = {
            "timestamp": utc_now(),
            "provider": "meshy",
            "server_package": "@meshy-ai/meshy-mcp-server",
            "server_version": server_version(),
            "tool": tool,
            "paid": paid,
            "request": redacted_arguments,
            "response": redacted_result,
        }
        if self.job_root is not None:
            write_json(self.job_root / "provider" / "requests" / f"{stamp}.json", {
                "timestamp": record["timestamp"],
                "provider": record["provider"],
                "server_package": record["server_package"],
                "server_version": record["server_version"],
                "tool": tool,
                "paid": paid,
                "arguments": redacted_arguments,
            })
            write_json(self.job_root / "provider" / "responses" / f"{stamp}.json", redacted_result)
            credits_value = _first_key(result, ("consumed_credits", "credits_used", "credit_cost", "cost"))
            credit_record = {
                "timestamp": record["timestamp"],
                "tool": tool,
                "paid": paid,
                "estimate_credits": estimate_credits,
                "consumed_credits": credits_value,
            }
            write_json(self.job_root / "provider" / "credits" / f"{stamp}.json", credit_record)
            append_history(
                self.job_root,
                state="provider_call_recorded",
                event=tool,
                actor="meshy_mcp",
                details={
                    "sequence": self.sequence,
                    "paid": paid,
                    "task_id": _first_key(result, ("task_id", "taskid")),
                    "estimate_credits": estimate_credits,
                    "consumed_credits": credits_value,
                },
            )
        return result

    def call(
        self,
        tool: str,
        arguments: Dict[str, Any],
        *,
        paid: bool = False,
        estimate_credits: Optional[int] = None,
        timeout_seconds: int = 1800,
    ) -> Dict[str, Any]:
        require_meshy_key()
        refuse_forbidden_arguments(tool, arguments)
        journal = None
        if paid:
            if self.job_root is None:
                raise RuntimeError("Paid submissions require a job-local upfront journal.")
            journal = self.job_root / "provider/submissions" / f"{uuid.uuid4().hex}.json"
            entry = {"timestamp": utc_now(), "tool": tool, "arguments": redact(arguments),
                     "fingerprint": request_fingerprint(tool, arguments),
                     "estimate_credits": estimate_credits, "state": "submission_started",
                     "automatic_retry": False}
            write_json(journal, entry)
        lifecycle = {}
        try:
            result = call_stdio(self._command(), tool=tool, arguments=arguments,
                                timeout_seconds=timeout_seconds, cwd=self.repo_root,
                                lifecycle_receipt=lifecycle)
            if journal:
                entry.update(state="uncertain" if result.get("isError") else "response_received",
                             response=redact(result), lifecycle=lifecycle)
                write_json(journal, entry)
        except Exception:
            if journal:
                entry.update(state="uncertain", lifecycle=lifecycle,
                             recovery="Inspect task inventory before any further paid submission; do not retry blindly.")
                write_json(journal, entry)
            raise
        return self._record(
            tool,
            arguments,
            result,
            paid=paid,
            estimate_credits=estimate_credits,
        )

    def check_balance(self) -> Dict[str, Any]:
        # The pinned stdio server can take longer than two minutes to resolve
        # and complete a cold authenticated probe even when the route is
        # healthy. Keep this read-only hard gate below the paid-call timeout,
        # but do not misclassify verified startup latency as a provider failure.
        return self.call("meshy_check_balance", {}, paid=False, timeout_seconds=300)

    def image_to_3d(
        self,
        *,
        image_path: Path,
        generation: Dict[str, Any],
        pose_mode: Optional[str],
        estimate_credits: int,
    ) -> Dict[str, Any]:
        if self.job_root is None:
            raise RuntimeError("Image-to-3D calls require a job root.")
        # The profile's model is explicit and never changes silently; refuse before any request.
        generation = validate_generation(generation)
        image_path = image_path.resolve()
        job_path(self.job_root, image_path.relative_to(self.job_root).as_posix(), must_exist=True)
        return self.call(
            "meshy_image_to_3d",
            image_to_3d_arguments(image_path, generation, pose_mode),
            paid=True,
            estimate_credits=estimate_credits,
            timeout_seconds=1800,
        )

    def wait_for_task(
        self,
        task_id: str,
        *,
        task_type: str,
        timeout_seconds: int = 1800,
    ) -> Dict[str, Any]:
        deadline = time.monotonic() + timeout_seconds
        last: Dict[str, Any] = {}
        while time.monotonic() < deadline:
            last = self.call(
                "meshy_get_task_status",
                {
                    "task_id": task_id,
                    "task_type": task_type,
                    "wait": True,
                    "timeout_seconds": 300,
                    "response_format": "json",
                },
                paid=False,
                timeout_seconds=360,
            )
            status = status_from(last)
            if status in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}:
                return last
            if status in {"FAILED", "ERROR", "CANCELED", "CANCELLED"}:
                raise MeshyTaskFailed(task_id, status, last)
        raise MCPRouteError(f"Meshy task {task_id} did not finish within {timeout_seconds}s.")

    def download(
        self,
        *,
        task_id: str,
        task_type: str,
        format_name: str,
        destination: Path,
        include_textures: bool = True,
        allow_url_only: bool = False,
    ) -> Dict[str, Any]:
        if self.job_root is None:
            raise RuntimeError("Downloads require a job root.")
        destination = destination.resolve()
        job_path(self.job_root, destination.relative_to(self.job_root).as_posix())
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite provider output: {destination}")
        result = self.call(
            "meshy_download_model",
            {
                "task_id": task_id,
                "task_type": task_type,
                "format": format_name,
                "include_textures": include_textures,
                "save_to": str(destination),
            },
            paid=False,
            timeout_seconds=1800,
        )
        if not destination.exists():
            local_path = _first_key(result, ("local_path", "path", "file_path"))
            if local_path and Path(str(local_path)).exists():
                actual = Path(str(local_path)).resolve()
                job_path(self.job_root, actual.relative_to(self.job_root).as_posix())
                destination = actual
        if not destination.exists():
            if allow_url_only:
                download_url = _first_key(result, ("download_url", "url"))
                if download_url:
                    record = {
                        "timestamp": utc_now(),
                        "task_id": task_id,
                        "task_type": task_type,
                        "format": format_name,
                        "include_textures": include_textures,
                        "url": str(download_url),
                        "url_only": True,
                    }
                    write_json(
                        self.job_root / "provider" / "downloads" / f"{destination.name}.url.json",
                        record,
                    )
                    append_history(
                        self.job_root,
                        state="provider_url_obtained",
                        event="meshy_download_model",
                        actor="meshy_mcp",
                        details={
                            "task_id": task_id,
                            "task_type": task_type,
                            "format": format_name,
                            "url_only": True,
                        },
                    )
                    return {"provider_response": result, "url": str(download_url), "url_only": True}
            raise MCPRouteError(f"Meshy download did not create the requested file: {destination}")
        record = file_record(destination, relative_to=self.job_root)
        write_json(
            self.job_root / "provider" / "downloads" / f"{destination.name}.manifest.json",
            {
                "timestamp": utc_now(),
                "task_id": task_id,
                "task_type": task_type,
                "format": format_name,
                "include_textures": include_textures,
                "file": record,
            },
        )
        append_history(
            self.job_root,
            state="provider_downloaded",
            event="meshy_download_model",
            actor="meshy_mcp",
            details={"task_id": task_id, "file": record},
        )
        return {"provider_response": result, "file": record}

    def fetch_provider_artifact(
        self,
        *,
        task_id: str,
        task_type: str,
        format_name: str,
        url: str,
        destination: Path,
        include_textures: bool = False,
    ) -> Dict[str, Any]:
        """Persist a signed Meshy artifact URL emitted by the verified MCP tool.

        The Meshy MCP package exposes rigging and animation outputs as signed
        artifact URLs instead of local files.  This transport deliberately
        accepts only the Meshy asset host, keeps the destination job-local, and
        records the URL-only MCP evidence next to the downloaded checksum.
        It is not an API or REST fallback.
        """

        if self.job_root is None:
            raise RuntimeError("Provider artifact fetches require a job root.")
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "assets.meshy.ai":
            raise MCPRouteError("Refusing provider artifact URL outside https://assets.meshy.ai/.")
        destination = destination.resolve()
        job_path(self.job_root, destination.relative_to(self.job_root).as_posix())
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite provider artifact: {destination}")
        partial = destination.with_name(destination.name + ".part")
        if partial.exists():
            raise FileExistsError(f"Refusing to overwrite incomplete provider artifact: {partial}")
        try:
            request = Request(url, headers={"User-Agent": "hoi4-3d-model-pipeline/1.0"})
            with urlopen(request, timeout=1800) as response, partial.open("wb") as stream:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    stream.write(chunk)
            if partial.stat().st_size <= 0:
                raise MCPRouteError("Meshy provider artifact response was empty.")
            partial.replace(destination)
        except Exception:
            if partial.exists():
                partial.unlink()
            raise
        record = file_record(destination, relative_to=self.job_root)
        write_json(
            self.job_root / "provider" / "downloads" / f"{destination.name}.manifest.json",
            {
                "timestamp": utc_now(),
                "task_id": task_id,
                "task_type": task_type,
                "format": format_name,
                "include_textures": include_textures,
                "transport": "mcp_provider_signed_asset_fetch",
                "source_url_host": parsed.hostname,
                "file": record,
            },
        )
        append_history(
            self.job_root,
            state="provider_downloaded",
            event="meshy_signed_asset_fetch",
            actor="meshy_mcp",
            details={"task_id": task_id, "task_type": task_type, "file": record},
        )
        return {"task_id": task_id, "task_type": task_type, "format": format_name, "file": record}

    def rig(
        self,
        *,
        input_task_id: Optional[str] = None,
        model_url: Optional[str] = None,
        height_meters: float,
        estimate_credits: int,
    ) -> Dict[str, Any]:
        return self.call(
            "meshy_rig",
            rig_arguments(input_task_id, model_url, height_meters),
            paid=True,
            estimate_credits=estimate_credits,
            timeout_seconds=1800,
        )

    def remesh(
        self,
        *,
        input_task_id: str,
        target_polycount: int,
        estimate_credits: int,
    ) -> Dict[str, Any]:
        return self.call(
            "meshy_remesh",
            remesh_arguments(input_task_id, target_polycount),
            paid=True,
            estimate_credits=estimate_credits,
            timeout_seconds=1800,
        )

    def convert(
        self,
        *,
        input_task_id: Optional[str] = None,
        model_url: Optional[str] = None,
        target_formats: list[str],
        estimate_credits: int,
    ) -> Dict[str, Any]:
        """Convert a completed Meshy task through the official MCP route."""

        if bool(input_task_id) == bool(model_url):
            raise ValueError("Meshy conversion requires exactly one of input_task_id or model_url.")
        arguments: Dict[str, Any] = {
            "target_formats": target_formats,
            "response_format": "json",
        }
        if input_task_id:
            arguments["input_task_id"] = input_task_id
        if model_url:
            arguments["model_url"] = model_url
        return self.call(
            "meshy_convert",
            arguments,
            paid=True,
            estimate_credits=estimate_credits,
            timeout_seconds=1800,
        )

    def _require_motion_tools(self, *, generated_retarget: bool = False) -> None:
        """Verify optional live exposure through the app launcher; never patch its runtime."""
        require_meshy_key()
        listed = call_stdio(self._command(), list_tools=True, timeout_seconds=300, cwd=self.repo_root)
        live = {item.get("name"): item for item in listed.get("tools", []) if isinstance(item, dict)}
        expected = dict(MOTION_TOOL_ARGUMENTS)
        if generated_retarget:
            expected["meshy_animate"] = {"rig_task_id", "motion_task_id"}
        missing = []
        for name, arguments in expected.items():
            properties = live.get(name, {}).get("inputSchema", {}).get("properties", {})
            if name not in live or not arguments.issubset(properties):
                missing.append(name)
        if missing:
            raise MCPRouteError(f"Required installation/verification: app-owned Meshy launcher lacks optional motion tools/schema: {sorted(missing)}. Do not use a project wrapper or direct REST; use the authorized Blender recovery route where applicable.")

    def list_animations(self, **filters: Any) -> Dict[str, Any]:
        """Free lookup of preset action ids (search, category, sub_category, action_ids)."""
        unknown = sorted(set(filters) - {"search", "category", "sub_category", "action_ids"})
        if unknown:
            raise ValueError(f"meshy_list_animations does not take {unknown}.")
        self._require_motion_tools()
        return self.call("meshy_list_animations", {**filters, "response_format": "json"}, timeout_seconds=300)

    def text_to_motion(self, *, prompt: str, mode: str, duration: float) -> Dict[str, Any]:
        if not isinstance(prompt, str) or not prompt.strip() or not 1 <= len(prompt) <= 400 or mode not in {"prime", "swift"}:
            raise ValueError("Motion requires prompt 1–400 characters and prime/swift mode.")
        if type(duration) not in (int, float) or not math.isfinite(duration) or not 2 <= duration <= 10 or duration * 2 != int(duration * 2):
            raise ValueError("Motion duration must be 2–10 seconds in half-second steps.")
        self._require_motion_tools()
        return self.call("meshy_text_to_motion", {"prompt": prompt, "mode": mode, "duration": duration},
                         paid=True, estimate_credits=operation_credits("text_to_motion", mode=mode),
                         timeout_seconds=300)

    def motion_status(self, task_id: str) -> Dict[str, Any]:
        self._require_motion_tools()
        return self.call("meshy_get_task_status", {"task_id": task_id, "task_type": "text-to-motion",
                         "wait": False, "response_format": "json"}, timeout_seconds=300)

    def list_motion_tasks(self, *, page_num: int = 1, page_size: int = 20) -> Dict[str, Any]:
        if type(page_num) is not int or page_num < 1 or type(page_size) is not int or not 1 <= page_size <= 100:
            raise ValueError("Motion pagination requires positive integer page and size 1..100.")
        self._require_motion_tools()
        return self.call("meshy_list_tasks", {"task_type": "text-to-motion", "limit": page_size,
                         "offset": (page_num - 1) * page_size, "response_format": "json"}, timeout_seconds=300)

    def download_motion(self, *, task_id: str, format_name: str, destination: Path) -> Dict[str, Any]:
        if self.job_root is None:
            raise RuntimeError("Motion download requires job root.")
        if not isinstance(task_id, str) or not task_id.strip() or format_name not in {"fbx", "bvh"}:
            raise ValueError("Motion download requires exact task id and fbx/bvh format.")
        destination = destination.resolve()
        job_path(self.job_root, destination.relative_to(self.job_root).as_posix())
        if destination.exists():
            raise FileExistsError(destination)
        self._require_motion_tools()
        # meshy_download_model saves a clip as its own file and ignores `format`, so the
        # receipt (task, format, checksum) is built here from the saved bytes.
        result = self.call("meshy_download_model", {"task_id": task_id, "task_type": "text-to-motion",
                           "save_to": str(destination)}, timeout_seconds=300)
        if result.get("isError") or not destination.is_file() or destination.stat().st_size <= 0:
            raise MCPRouteError("Motion download did not save a non-empty file.")
        receipt = {"timestamp": utc_now(), "task_id": task_id, "task_type": "text-to-motion",
                   "format": format_name, "file": file_record(destination, relative_to=self.job_root)}
        write_json(self.job_root / "provider/downloads" / f"{destination.name}.manifest.json", receipt)
        return receipt

    def animate(self, *, rig_task_id: str, estimate_credits: int, action_id: Optional[int] = None,
                motion_task_id: Optional[str] = None) -> Dict[str, Any]:
        arguments = animate_arguments(rig_task_id, action_id, motion_task_id)
        if motion_task_id is not None:
            if not isinstance(motion_task_id, str) or not motion_task_id.strip():
                raise ValueError("Generated-motion retarget requires a nonblank task id.")
            self._require_motion_tools(generated_retarget=True)
        return self.call(
            "meshy_animate",
            arguments,
            paid=True,
            estimate_credits=estimate_credits,
            timeout_seconds=1800,
        )
