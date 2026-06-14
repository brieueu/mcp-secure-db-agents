from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


@dataclass(frozen=True)
class RolePolicy:
    name: str
    allowed_tools: set[str]
    allowed_objects: set[str]
    forbidden_objects: set[str]
    denied_columns: set[str]


class PolicyEngine:
    def __init__(self, roles: dict[str, RolePolicy]):
        self.roles = roles

    @classmethod
    def from_yaml(cls, path: str | Path) -> "PolicyEngine":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        roles = {}
        for name, raw in data.get("roles", {}).items():
            allowed_objects = raw.get("allowed_objects", raw.get("allowed_tables", []))
            roles[name] = RolePolicy(
                name=name,
                allowed_tools=set(raw.get("allowed_tools", [])),
                allowed_objects={o.lower() for o in allowed_objects},
                forbidden_objects={o.lower() for o in raw.get("forbidden_objects", [])},
                denied_columns={c.lower() for c in raw.get("denied_columns", [])},
            )
        return cls(roles)

    def role(self, role: str) -> RolePolicy:
        if role not in self.roles:
            raise KeyError(f"Papel desconhecido: {role}")
        return self.roles[role]

    def allowed_objects(self, role: str) -> set[str]:
        return set(self.role(role).allowed_objects)

    def forbidden_objects(self, role: str) -> set[str]:
        return set(self.role(role).forbidden_objects)

    def authorize(self, role: str, tool: str, objects: set[str] | list[str] | tuple[str, ...]) -> PolicyDecision:
        try:
            policy = self.role(role)
        except KeyError as exc:
            return PolicyDecision(False, str(exc))
        if tool not in policy.allowed_tools:
            return PolicyDecision(False, f"Ferramenta não autorizada para {role}: {tool}")
        normalized = {obj.lower() for obj in objects}
        blocked = normalized & policy.forbidden_objects
        if blocked:
            return PolicyDecision(False, f"Objeto bloqueado pela política: {', '.join(sorted(blocked))}")
        denied = normalized - policy.allowed_objects
        if denied:
            return PolicyDecision(False, f"Objeto não autorizado para {role}: {', '.join(sorted(denied))}")
        return PolicyDecision(True, "Acesso autorizado")

    def as_dict(self) -> dict[str, Any]:
        return {name: {
            "allowed_tools": sorted(role.allowed_tools),
            "allowed_objects": sorted(role.allowed_objects),
            "forbidden_objects": sorted(role.forbidden_objects),
            "denied_columns": sorted(role.denied_columns),
        } for name, role in self.roles.items()}
