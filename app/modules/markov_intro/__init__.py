from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="markov_intro",
    name="Markov Chains — Basics",
    description="Generate a tiny random Markov chain, walk it from a start state, and compare empirical visitation to the stationary distribution.",
    controller=controller,
    accent_color="#3b82f6",
    template_name="module_markov_intro.html",
)

__all__ = ["MODULE_META"]
