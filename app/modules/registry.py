from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ModuleMetadata:
    slug: str
    name: str
    description: str
    controller: Any
    accent_color: str = "#2563eb"
    template_name: str = "module.html"


_MODULES: Dict[str, ModuleMetadata] = {}


def _load_default_modules() -> None:
    """Import modules and populate the registry exactly once."""
    if _MODULES:
        return

    from .phase_transition import MODULE_META as phase_transition_meta
    from .g_nm import MODULE_META as gnm_meta
    from .monte_carlo_union import MODULE_META as union_area_meta
    from .monte_carlo_ln2 import MODULE_META as ln2_meta
    from .markov_intro import MODULE_META as markov_intro_meta
    from .markov_random_2sat import MODULE_META as markov_random_2sat_meta
    from .markov_random_3sat import MODULE_META as markov_random_3sat_meta
    from .markov_random_walks import MODULE_META as markov_random_walks_meta
    from .markov_metropolis_paths import MODULE_META as markov_metropolis_paths_meta
    from .ric_smallest_enclosing_circle import MODULE_META as ric_smallest_circle_meta
    from .ric_closest_pair import MODULE_META as ric_closest_pair_meta
    from .bloom_filter import MODULE_META as bloom_filter_meta

    register_module(phase_transition_meta)
    register_module(gnm_meta)
    register_module(union_area_meta)
    register_module(ln2_meta)
    register_module(markov_intro_meta)
    register_module(markov_random_2sat_meta)
    register_module(markov_random_3sat_meta)
    register_module(markov_random_walks_meta)
    register_module(markov_metropolis_paths_meta)
    register_module(ric_smallest_circle_meta)
    register_module(ric_closest_pair_meta)
    register_module(bloom_filter_meta)


def register_module(metadata: ModuleMetadata) -> None:
    _MODULES[metadata.slug] = metadata


def list_modules() -> List[ModuleMetadata]:
    _load_default_modules()
    return sorted(_MODULES.values(), key=lambda m: m.name)


def get_module_metadata(slug: str) -> Optional[ModuleMetadata]:
    _load_default_modules()
    return _MODULES.get(slug)
