from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="phase-transition",
    name="Random Graphs G(n,p)",
    description="Animate Erdős–Rényi G(n, p) graphs as edge probability increases and observe structural changes.",
    controller=controller,
    accent_color="#10b981",
)

__all__ = ["MODULE_META"]
