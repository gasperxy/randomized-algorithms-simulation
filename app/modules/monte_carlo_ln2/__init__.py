from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="ln2-estimator",
    name="Monte Carlo ln(2)",
    description="Estimate ln(2) by sampling x ∈ [1, 2] and averaging 1/x values.",
    controller=controller,
    accent_color="#ef4444",
    template_name="module_ln2.html",
)

__all__ = ["MODULE_META"]
