from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, QTimer, pyqtSignal

from driving_preference_field.config import FieldConfig
from driving_preference_field.contracts import QueryContext, SemanticInputSnapshot
from driving_preference_field.evaluator import StateEvaluationResult, evaluate_state
from driving_preference_field.raster import RasterSampleResult, sample_local_raster


@dataclass(frozen=True)
class RasterComparisonResult:
    baseline_raster: RasterSampleResult
    candidate_raster: RasterSampleResult
    baseline_state: StateEvaluationResult
    candidate_state: StateEvaluationResult


class _WorkerSignals(QObject):
    finished = pyqtSignal(int, object)
    failed = pyqtSignal(int, str)


class _RasterRunnable(QRunnable):
    def __init__(
        self,
        *,
        generation: int,
        snapshot: SemanticInputSnapshot,
        context: QueryContext,
        baseline_config: FieldConfig,
        candidate_config: FieldConfig,
        x_samples: int,
        y_samples: int,
        signals: _WorkerSignals,
    ) -> None:
        super().__init__()
        self._generation = generation
        self._snapshot = snapshot
        self._context = context
        self._baseline_config = baseline_config
        self._candidate_config = candidate_config
        self._x_samples = x_samples
        self._y_samples = y_samples
        self._signals = signals

    def run(self) -> None:
        try:
            baseline_raster = sample_local_raster(
                self._snapshot,
                self._context,
                config=self._baseline_config,
                x_samples=self._x_samples,
                y_samples=self._y_samples,
            )
            candidate_raster = sample_local_raster(
                self._snapshot,
                self._context,
                config=self._candidate_config,
                x_samples=self._x_samples,
                y_samples=self._y_samples,
            )
            baseline_state = evaluate_state(
                self._snapshot,
                self._context,
                self._context.ego_pose,
                config=self._baseline_config,
            )
            candidate_state = evaluate_state(
                self._snapshot,
                self._context,
                self._context.ego_pose,
                config=self._candidate_config,
            )
            result = RasterComparisonResult(
                baseline_raster=baseline_raster,
                candidate_raster=candidate_raster,
                baseline_state=baseline_state,
                candidate_state=candidate_state,
            )
        except Exception as exc:  # noqa: BLE001
            self._signals.failed.emit(self._generation, str(exc))
            return
        self._signals.finished.emit(self._generation, result)


class AsyncRasterEvaluator(QObject):
    comparisonReady = pyqtSignal(int, object)
    evaluationFailed = pyqtSignal(int, str)
    busyChanged = pyqtSignal(bool)

    def __init__(self, *, debounce_ms: int = 100) -> None:
        super().__init__()
        self._thread_pool = QThreadPool(self)
        self._thread_pool.setMaxThreadCount(1)
        self._thread_pool.setExpiryTimeout(0)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(debounce_ms)
        self._timer.timeout.connect(self._dispatch)
        self._latest_generation = 0
        self._busy = False
        self._active_signals: _WorkerSignals | None = None
        self._pending: tuple[
            SemanticInputSnapshot,
            QueryContext,
            FieldConfig,
            FieldConfig,
            int,
            int,
        ] | None = None

    def request(
        self,
        snapshot: SemanticInputSnapshot,
        context: QueryContext,
        *,
        baseline_config: FieldConfig,
        candidate_config: FieldConfig,
        x_samples: int,
        y_samples: int,
    ) -> int:
        self._latest_generation += 1
        self._pending = (
            snapshot,
            context,
            baseline_config,
            candidate_config,
            x_samples,
            y_samples,
        )
        self._timer.start()
        return self._latest_generation

    def shutdown(self, *, wait_ms: int = 1000) -> None:
        self._timer.stop()
        self._pending = None
        self._active_signals = None
        self._thread_pool.clear()
        self._thread_pool.waitForDone(wait_ms)
        self._busy = False
        self.busyChanged.emit(False)

    def _dispatch(self) -> None:
        if self._pending is None or self._busy:
            return
        snapshot, context, baseline_config, candidate_config, x_samples, y_samples = self._pending
        self._busy = True
        self.busyChanged.emit(True)
        generation = self._latest_generation
        signals = _WorkerSignals()
        self._active_signals = signals
        signals.finished.connect(self._on_finished)
        signals.failed.connect(self._on_failed)
        runnable = _RasterRunnable(
            generation=generation,
            snapshot=snapshot,
            context=context,
            baseline_config=baseline_config,
            candidate_config=candidate_config,
            x_samples=x_samples,
            y_samples=y_samples,
            signals=signals,
        )
        self._thread_pool.start(runnable)

    def _on_finished(self, generation: int, result: RasterComparisonResult) -> None:
        self._busy = False
        self._active_signals = None
        if generation == self._latest_generation:
            self.comparisonReady.emit(generation, result)
            if not self._timer.isActive():
                self.busyChanged.emit(False)
                return
        QTimer.singleShot(0, self._dispatch)

    def _on_failed(self, generation: int, message: str) -> None:
        self._busy = False
        self._active_signals = None
        if generation == self._latest_generation:
            self.evaluationFailed.emit(generation, message)
            if not self._timer.isActive():
                self.busyChanged.emit(False)
                return
        QTimer.singleShot(0, self._dispatch)
