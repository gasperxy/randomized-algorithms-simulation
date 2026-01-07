from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="markov_metropolis_paths",
    name="Metropolis–Hastings Grid Paths",
    description="Sample simple grid paths with MH, favoring shorter routes and visualizing moves with obstacles.",
    controller=controller,
    accent_color="#16a34a",
    template_name="module_markov_metropolis_paths.html",
)

__all__ = ["MODULE_META"]
