from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="markov_random_2sat",
    name="Markov Random 2-SAT Walk",
    description="Follow Papadimitriou's random walk on a random 2-SAT instance and watch satisfied clauses evolve as a Markov chain.",
    controller=controller,
    accent_color="#a855f7",
    template_name="module_markov_random_2sat.html",
)

__all__ = ["MODULE_META"]
