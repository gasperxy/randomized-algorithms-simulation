from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="ric-closest-pair",
    name="Closest Pair Distance (RIC)",
    description="Track the closest pair as points arrive, using a randomized incremental grid.",
    controller=controller,
    accent_color="#14b8a6",
    template_name="module_ric_closest_pair.html",
)

__all__ = ["MODULE_META"]
