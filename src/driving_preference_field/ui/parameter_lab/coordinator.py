from __future__ import annotations

from driving_preference_field.ui.async_raster_evaluator import AsyncRasterEvaluator


class ParameterLabCoordinator:
    def __init__(self, *, debounce_ms: int = 100) -> None:
        self._evaluator = AsyncRasterEvaluator(debounce_ms=debounce_ms)

    @property
    def evaluator(self) -> AsyncRasterEvaluator:
        return self._evaluator

    def request(
        self,
        snapshot,
        context,
        *,
        baseline_config,
        candidate_config,
        x_samples: int,
        y_samples: int,
    ) -> None:
        self._evaluator.request(
            snapshot,
            context,
            baseline_config=baseline_config,
            candidate_config=candidate_config,
            x_samples=x_samples,
            y_samples=y_samples,
        )

    def shutdown(self) -> None:
        self._evaluator.shutdown()
