from __future__ import annotations

from dataclasses import dataclass


@dataclass(eq=False)
class Node:
    freq: int
    letter: int | None = None
    left: Node | None = None
    right: Node | None = None

    @classmethod
    def parent(cls, left: Node, right: Node) -> Node:
        return cls(freq=left.freq + right.freq, left=left, right=right)

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None
