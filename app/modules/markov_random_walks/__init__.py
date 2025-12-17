from . import controller
from ..registry import ModuleMetadata

MODULE_META = ModuleMetadata(
    slug="markov_random_walks",
    name="Random Walks in Graphs",
    description="Animate random walks on graph families and explore cover-time growth vs theory.",
    controller=controller,
    accent_color="#9333ea",
    template_name="module_markov_random_walks.html",
)

__all__ = ["MODULE_META"]
