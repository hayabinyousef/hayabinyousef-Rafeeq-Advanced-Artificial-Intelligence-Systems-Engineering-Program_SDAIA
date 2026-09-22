"""Validated runtime configuration for the mandatory offline learner path."""

from __future__ import annotations

from dataclasses import dataclass, field
import os


@dataclass(frozen=True, slots=True)
class Limits:
    """Hard safety limits for a single run.

    The defaults are part of the learner contract.  Smaller values are useful
    in tests; larger values are rejected to keep the graph bounded.
    """

    max_steps: int = 6
    max_transitions: int = 12
    max_handoffs: int = 2
    max_reflections: int = 1
    max_input_chars: int = 2_000
    session_memory_items: int = 20

    def __post_init__(self) -> None:
        ceilings = {
            "max_steps": (self.max_steps, 6),
            "max_transitions": (self.max_transitions, 12),
            "max_handoffs": (self.max_handoffs, 2),
            "max_reflections": (self.max_reflections, 1),
        }
        for name, (value, ceiling) in ceilings.items():
            if value < 0 or value > ceiling:
                raise ValueError(f"{name} must be between 0 and {ceiling}")
        if self.max_input_chars < 100:
            raise ValueError("max_input_chars must be at least 100")
        if self.session_memory_items < 1:
            raise ValueError("session_memory_items must be positive")


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings loaded without secrets.

    Only ``stub`` is accepted by the public package.  A live model, when
    demonstrated privately, must be injected outside this package.
    """

    llm_mode: str = "stub"
    limits: Limits = field(default_factory=Limits)

    def __post_init__(self) -> None:
        if self.llm_mode.strip().lower() != "stub":
            raise ValueError("The public learner path supports LLM_MODE=stub only")

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from the safe ``LLM_MODE`` environment variable."""

        return cls(llm_mode=os.getenv("LLM_MODE", "stub"))
