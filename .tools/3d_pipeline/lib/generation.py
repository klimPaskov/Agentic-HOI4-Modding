"""Generation settings a profile may ask Meshy for, and what every paid operation costs.

Standard library only, so the bootstrap can load this file by path. Prices come from
config/meshy_pricing.json. The accepted models come from the reviewed schema lock, and the
retired models, unpinned aliases and Smart Topology caps come from the tool contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

CONFIG_ROOT = Path(__file__).resolve().parents[1] / "config"
PRICING_PATH = CONFIG_ROOT / "meshy_pricing.json"
CONTRACT_PATH = CONFIG_ROOT / "meshy_tool_contract.json"
SCHEMA_LOCK_PATH = CONFIG_ROOT / "meshy_tool_schema.lock.json"
GENERATION_KEYS = (
    "ai_model",
    "model_type",
    "target_polycount",
    "should_remesh",
    "texture_resolution",
    "enable_pbr",
)
TEXTURE_RESOLUTIONS = ("2k", "4k", "8k")
STANDARD_POLYCOUNT_RANGE = (100, 300000)
SMART_TOPOLOGY = "smart-topology"


class GenerationError(ValueError):
    """The settings would not make a valid request, or no price is known for them."""


def _load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GenerationError(f"Expected a JSON object in {path}")
    return value


def load_pricing(path: Path = PRICING_PATH) -> Dict[str, Any]:
    return _load(path)


def load_contract(path: Path = CONTRACT_PATH) -> Dict[str, Any]:
    return _load(path)


def load_schema_lock(path: Path = SCHEMA_LOCK_PATH) -> Dict[str, Any]:
    return _load(path)


def locked_server_version(schema_lock: Optional[Dict[str, Any]] = None) -> str:
    """The Meshy MCP version the reviewed schema lock was captured from."""

    return str((schema_lock or load_schema_lock())["server_version"])


def _model_prices(pricing: Dict[str, Any], model: str) -> Dict[str, Any]:
    models = pricing["image_to_3d"]["models"]
    entry = models.get(model)
    if entry is None:
        raise GenerationError(f"config/meshy_pricing.json has no price for {model!r}.")
    if "same_price_as" in entry:
        return _model_prices(pricing, str(entry["same_price_as"]))
    return entry


def generation_credits(
    model: str,
    texture_resolution: Optional[str] = "2k",
    *,
    pricing: Optional[Dict[str, Any]] = None,
) -> int:
    """Credits for one image-to-3d request; no resolution means a mesh-only request."""

    entry = _model_prices(pricing or load_pricing(), model)
    if texture_resolution is None:
        return int(entry["mesh_only"])
    price = entry["textured"].get(texture_resolution)
    if price is None:
        raise GenerationError(f"{model} does not offer {texture_resolution} textures.")
    return int(price)


def operation_credits(
    operation: str,
    *,
    pricing: Optional[Dict[str, Any]] = None,
    actions: int = 1,
    mode: Optional[str] = None,
    texture_resolution: str = "2k",
) -> int:
    """Credits for a post-generation operation (remesh, rig, animation, text_to_motion, ...)."""

    prices = (pricing or load_pricing())["operations"]
    if operation == "animation":
        return int(prices["animation_per_action"]) * actions
    if operation not in prices:
        raise GenerationError(f"config/meshy_pricing.json has no price for {operation!r}.")
    price = prices[operation]
    if isinstance(price, dict):
        key = mode if operation == "text_to_motion" else texture_resolution
        if key not in price:
            raise GenerationError(f"No {operation} price for {key!r}.")
        return int(price[key])
    return int(price)


def _type_problems(generation: Dict[str, Any]) -> List[str]:
    problems = []
    for key in ("ai_model", "model_type", "texture_resolution"):
        if not isinstance(generation[key], str) or not generation[key].strip():
            problems.append(f"{key} must be a non-empty string")
    for key in ("should_remesh", "enable_pbr"):
        if not isinstance(generation[key], bool):
            problems.append(f"{key} must be true or false")
    target = generation["target_polycount"]
    if target is not None and (isinstance(target, bool) or not isinstance(target, int)):
        problems.append("target_polycount must be a whole number or null")
    if not isinstance(generation.get("target_polycount_applies", False), bool):
        problems.append("target_polycount_applies must be true or false")
    return problems


def _model_problems(model: str, model_type: str, policy: Dict[str, Any], lock: Dict[str, Any]) -> List[str]:
    image_tool = lock["required_tools"]["meshy_image_to_3d"]
    accepted_types = image_tool["input_schema"]["properties"]["model_type"]["enum"]
    problems = []
    if model in policy.get("retired_generation_models", []):
        problems.append(f"{model} is retired by Meshy")
    elif model in policy.get("unpinned_model_aliases", []):
        problems.append(f"{model!r} is an alias Meshy can repoint; name an explicit model")
    elif model not in image_tool["accepted_ai_models"]:
        problems.append(f"{model} is not accepted by the locked meshy_image_to_3d schema")
    if model_type in policy.get("retired_model_types", []):
        problems.append(f"model_type {model_type} is retired by Meshy")
    elif model_type not in accepted_types:
        problems.append(f"model_type {model_type} is not accepted by the locked schema")
    return problems


def _target_problems(generation: Dict[str, Any], model: str, policy: Dict[str, Any]) -> List[str]:
    smart_models = policy.get("smart_topology_models", {})
    smart = generation["model_type"] == SMART_TOPOLOGY
    target = generation["target_polycount"]
    problems = []
    if smart != (model in smart_models):
        problems.append(f"model_type {SMART_TOPOLOGY} requires exactly the models {sorted(smart_models)}")
    if smart:
        cap = smart_models.get(model, {}).get("max_target_polycount")
        if target is None or target < 100 or (cap is not None and target > cap):
            problems.append(f"{model} target_polycount must be between 100 and {cap}, got {target}")
        if generation["should_remesh"]:
            problems.append(f"should_remesh is ignored under {SMART_TOPOLOGY}; set it to false")
        return problems
    low, high = STANDARD_POLYCOUNT_RANGE
    if generation["should_remesh"] and target is None:
        problems.append("should_remesh needs a target_polycount")
    if target is not None and not low <= target <= high:
        problems.append(f"target_polycount must be between {low} and {high:,}, got {target}")
    if generation.get("target_polycount_applies", False) and not generation["should_remesh"]:
        problems.append(
            "target_polycount is meant to apply, but Meshy ignores it on a standard model "
            "unless should_remesh is true"
        )
    return problems


def generation_problems(
    generation: Any,
    *,
    contract: Optional[Dict[str, Any]] = None,
    schema_lock: Optional[Dict[str, Any]] = None,
    pricing: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Every reason the settings cannot be sent to Meshy; empty when they are valid."""

    if not isinstance(generation, dict):
        return ["the profile has no generation settings"]
    missing = [key for key in GENERATION_KEYS if key not in generation]
    if missing:
        return [f"generation settings are missing {missing}"]
    problems = _type_problems(generation)
    if problems:
        return problems
    policy = (contract or load_contract()).get("provider_policy", {})
    model = generation["ai_model"].strip().lower()
    model_type = generation["model_type"].strip().lower()
    problems = _model_problems(model, model_type, policy, schema_lock or load_schema_lock())
    problems += _target_problems({**generation, "model_type": model_type}, model, policy)
    try:
        generation_credits(model, generation["texture_resolution"], pricing=pricing)
    except GenerationError as error:
        problems.append(str(error))
    return problems


def validate_generation(
    generation: Any,
    *,
    contract: Optional[Dict[str, Any]] = None,
    schema_lock: Optional[Dict[str, Any]] = None,
    pricing: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return the normalized settings, or raise GenerationError listing every problem."""

    problems = generation_problems(generation, contract=contract, schema_lock=schema_lock, pricing=pricing)
    if problems:
        raise GenerationError("Invalid Meshy generation settings: " + "; ".join(problems) + ".")
    return {
        **generation,
        "ai_model": generation["ai_model"].strip().lower(),
        "model_type": generation["model_type"].strip().lower(),
        "texture_resolution": generation["texture_resolution"].strip().lower(),
        "target_polycount_applies": bool(generation.get("target_polycount_applies", False)),
    }


def generation_estimate(generation: Dict[str, Any], *, pricing: Optional[Dict[str, Any]] = None) -> int:
    """Credits for the textured image-to-3d request these settings make."""

    return generation_credits(generation["ai_model"], generation["texture_resolution"], pricing=pricing)
