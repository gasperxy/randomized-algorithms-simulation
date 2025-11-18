from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="union-area",
    name="Monte Carlo Union of Rectangles",
    description="Estimate the area of overlapping rectangles via random sampling and ε-δ style reasoning.",
    controller=controller,
    accent_color="#f59e0b",
    template_name="module_union_area.html",
)

__all__ = ["MODULE_META"]
