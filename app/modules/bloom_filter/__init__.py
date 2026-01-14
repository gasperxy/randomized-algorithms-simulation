from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="bloom-filter",
    name="Bloom Filter Simulator",
    description="Visualize bit-array updates and false positives as items are inserted.",
    controller=controller,
    accent_color="#0ea5e9",
    template_name="module_bloom_filter.html",
)

__all__ = ["MODULE_META"]
