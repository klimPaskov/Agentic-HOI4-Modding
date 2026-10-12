#!/usr/bin/env python3
"""Refresh the canonical provider allowlist shipped with the local MCP adapter."""

from image_generation_provider_data import write_runtime_provider_catalog


if __name__ == "__main__":
    print(write_runtime_provider_catalog())
