"""Pinned Meshy MCP client used by the autonomous job runner.

The client starts only the external app-owned launcher materialized by the
repository bootstrap. Project wrappers and direct REST/API fallbacks are not
credential routes.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from lib.mcp_stdio import MCPRouteError, call_stdio
from lib.paths import (
    append_history,
    file_record,
    job_path,
    redact,
    sha256_file,
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


def task_id_from(result: Dict[str, Any]) -> str:
    value = _first_key(result, ("task_id", "taskid", "id"))
    if not value:
        raise MCPRouteError("Meshy response did not contain a task id.")
    return str(value)


def status_from(result: Dict[str, Any]) -> str:
    value = _first_key(result, ("status", "state"))
    return str(value or "UNKNOWN").upper()


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
            "server_version": os.environ.get("MESHY_MCP_VERSION", "0.4.0"),
            "server_compatibility": "meshy-7-live-schema",
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
            credits_value = _first_key(result, ("credits_used", "credit_cost", "cost"))
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
        result = call_stdio(
            self._command(),
            tool=tool,
            arguments=arguments,
            timeout_seconds=timeout_seconds,
            cwd=self.repo_root,
        )
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
        ai_model: str,
        model_type: str,
        pose_mode: Optional[str],
        target_polycount: int,
        estimate_credits: int,
    ) -> Dict[str, Any]:
        if self.job_root is None:
            raise RuntimeError("Image-to-3D calls require a job root.")
        if ai_model.lower() != "meshy-7":
            raise ValueError("Image-to-3D generation requires explicit ai_model='meshy-7'.")
        image_path = image_path.resolve()
        job_path(self.job_root, image_path.relative_to(self.job_root).as_posix(), must_exist=True)
        arguments = {
            "file_path": str(image_path),
            "ai_model": ai_model,
            "model_type": model_type,
            "enable_pbr": True,
            "topology": "triangle",
            "target_polycount": target_polycount,
            "should_remesh": False,
            "should_texture": True,
            "image_enhancement": True,
            "target_formats": ["glb", "fbx"],
            "multi_view_thumbnails": False,
            "response_format": "json",
        }
        if pose_mode:
            arguments["pose_mode"] = pose_mode
        return self.call(
            "meshy_image_to_3d",
            arguments,
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
        if bool(input_task_id) == bool(model_url):
            raise ValueError("Meshy rigging requires exactly one of input_task_id or model_url.")
        arguments: Dict[str, Any] = {
            "height_meters": height_meters,
            "response_format": "json",
        }
        if input_task_id:
            arguments["input_task_id"] = input_task_id
        if model_url:
            arguments["model_url"] = model_url
        return self.call(
            "meshy_rig",
            arguments,
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
            {
                "input_task_id": input_task_id,
                "target_formats": ["glb", "fbx"],
                "topology": "triangle",
                "target_polycount": target_polycount,
                "response_format": "json",
            },
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

    def animate(self, *, rig_task_id: str, action_id: int, estimate_credits: int) -> Dict[str, Any]:
        return self.call(
            "meshy_animate",
            {
                "rig_task_id": rig_task_id,
                "action_id": action_id,
                "response_format": "json",
            },
            paid=True,
            estimate_credits=estimate_credits,
            timeout_seconds=1800,
        )
