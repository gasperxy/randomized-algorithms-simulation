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

    register_module(phase_transition_meta)
    register_module(gnm_meta)
    register_module(union_area_meta)
    register_module(ln2_meta)


def register_module(metadata: ModuleMetadata) -> None:
    _MODULES[metadata.slug] = metadata


def list_modules() -> List[ModuleMetadata]:
    _load_default_modules()
    return sorted(_MODULES.values(), key=lambda m: m.name)


def get_module_metadata(slug: str) -> Optional[ModuleMetadata]:
    _load_default_modules()
    return _MODULES.get(slug)
