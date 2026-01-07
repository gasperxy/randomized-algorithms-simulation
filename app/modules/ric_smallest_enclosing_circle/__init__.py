from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="ric-smallest-circle",
    name="Smallest Enclosing Circle (RIC)",
    description="Use randomized incremental construction to maintain the minimal circle as points arrive.",
    controller=controller,
    accent_color="#0ea5e9",
    template_name="module_ric_smallest_enclosing_circle.html",
)

__all__ = ["MODULE_META"]
