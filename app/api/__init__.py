"""API package with canonical and legacy router registries.

The runtime entrypoint uses `v1_api_router` from `app.api.v1.router`.
`legacy_api_router` is provided for controlled migration/testing only.
"""

from app.api.v1.router import api_router as v1_api_router


def get_legacy_api_router():
	"""Lazy-load legacy router to avoid side effects during normal startup."""
	from app.api.legacy.router import legacy_api_router
	return legacy_api_router

__all__ = ["v1_api_router", "get_legacy_api_router"]
