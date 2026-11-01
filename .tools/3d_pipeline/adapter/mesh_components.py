"""Connected-component counting for the loose-parts acceptance check.

Pure Python so the Blender worker and the unit tests share one implementation.
A component is a set of vertices joined by edges; a vertex with no edges is a
component of its own, matching Blender's "Separate by Loose Parts".
"""

from __future__ import annotations

from typing import Iterable, List, Tuple


def count_connected_components(vertex_count: int, edges: Iterable[Tuple[int, int]]) -> int:
    """Count components of a graph given as a vertex count and (a, b) index pairs."""

    if vertex_count < 0:
        raise ValueError("vertex_count must not be negative.")
    parent: List[int] = list(range(vertex_count))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    components = vertex_count
    for first, second in edges:
        if not (0 <= first < vertex_count and 0 <= second < vertex_count):
            raise ValueError(f"Edge ({first}, {second}) refers outside {vertex_count} vertices.")
        root_first, root_second = find(first), find(second)
        if root_first != root_second:
            parent[root_second] = root_first
            components -= 1
    return components
