"""Compatibility wrapper for the pre-rename ``driving_preference_field`` import path.

The implementation package was renamed to ``local_reference_path_cost``.
Downstream consumers should migrate imports when practical; this shim keeps
existing SSC integrations importable during the transition.
"""

from __future__ import annotations

import local_reference_path_cost as _impl
from local_reference_path_cost import *  # noqa: F401,F403

__path__ = _impl.__path__
__all__ = getattr(_impl, "__all__", ())
