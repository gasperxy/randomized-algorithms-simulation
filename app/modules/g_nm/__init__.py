from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="gnm",
    name="Random Graph Edge Process (G(n, m))",
    description="Observe Erdős–Rényi G(n, m) graphs as edges are added one by one and relate them to the equivalent G(n, p).",
    controller=controller,
    accent_color="#10b981",
    template_name="module_gnm.html",
)

__all__ = ["MODULE_META"]
