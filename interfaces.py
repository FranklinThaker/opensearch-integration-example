import typing as t
from dataclasses import dataclass, field


@dataclass
class Resource:
    name: str

    def __post_init__(self) -> None:
        self.name = self.name.lower()


@dataclass
class Resources:
    users: Resource = field(default_factory=lambda: Resource("Users"))
