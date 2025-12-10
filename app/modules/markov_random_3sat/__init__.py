from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="markov_random_3sat",
    name="Markov Random 3-SAT Walk",
    description="Restart-based random walk for 3-SAT: flip variables in unsatisfied clauses across repeated trials to hunt for a satisfying assignment.",
    controller=controller,
    accent_color="#ec4899",
    template_name="module_markov_random_3sat.html",
)

__all__ = ["MODULE_META"]
