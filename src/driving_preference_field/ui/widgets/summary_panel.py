from __future__ import annotations

import json

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from driving_preference_field.ui.locale import DEFAULT_LANGUAGE, t


class SummaryPanelWidget(QWidget):
    noteChanged = pyqtSignal(str)

    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__()
        self._language = language
        self._normalization_banner = QLabel()
        self._normalization_banner.setWordWrap(True)
        self._normalization_banner.setTextFormat(Qt.TextFormat.PlainText)
        self._target_label = QLabel()
        self._target_label.setWordWrap(True)
        self._target_label.setTextFormat(Qt.TextFormat.PlainText)
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._note = QTextEdit()
        self._note.textChanged.connect(self._emit_note_changed)
        self._summary_label = QLabel()
        self._note_label = QLabel()
        layout = QVBoxLayout(self)
        layout.addWidget(self._summary_label)
        layout.addWidget(self._normalization_banner)
        layout.addWidget(self._target_label)
        layout.addWidget(self._text)
        layout.addWidget(self._note_label)
        layout.addWidget(self._note)
        self.retranslate(language)

    def set_summary(self, payload: dict[str, object]) -> None:
        self._set_normalization_banner(payload.get("progression_normalization"))
        self._set_target_label(payload.get("progression_target"))
        self._text.setPlainText(json.dumps(payload, indent=2, sort_keys=True))

    def note(self) -> str:
        return self._note.toPlainText().strip()

    def set_note(self, note: str) -> None:
        self._note.blockSignals(True)
        self._note.setPlainText(note)
        self._note.blockSignals(False)
        self.noteChanged.emit(note.strip())

    def _emit_note_changed(self) -> None:
        self.noteChanged.emit(self.note())

    def retranslate(self, language: str) -> None:
        self._language = language
        self._summary_label.setText(t(language, "summary.title"))
        self._note_label.setText(t(language, "summary.qualitative_note"))

    def _set_normalization_banner(self, normalization: object) -> None:
        if not isinstance(normalization, dict):
            self._normalization_banner.hide()
            self._normalization_banner.clear()
            return
        severity = str(normalization.get("severity", "info"))
        source_kind = str(normalization.get("source_kind", "unknown"))
        messages = normalization.get("messages", [])
        message_text = " ".join(str(message) for message in messages) if isinstance(messages, list) else str(messages)
        banner_text = (
            f"{t(self._language, 'summary.progression_normalization')} "
            f"[{t(self._language, f'severity.{severity}')}] "
            f"{source_kind} | {normalization.get('input_guide_count')} -> {normalization.get('output_guide_count')}\n"
            f"{message_text}"
        )
        palette = {
            "info": ("#e8f4ff", "#2b6cb0"),
            "warning": ("#fff8db", "#9c6b00"),
            "error": ("#ffe8e8", "#b83232"),
        }
        background, foreground = palette.get(severity, palette["info"])
        self._normalization_banner.setStyleSheet(
            "QLabel {"
            f"background: {background};"
            f"color: {foreground};"
            "border: 1px solid rgba(0,0,0,0.18);"
            "border-radius: 4px;"
            "padding: 6px;"
            "}"
        )
        self._normalization_banner.setText(banner_text)
        self._normalization_banner.show()

    def _set_target_label(self, target: object) -> None:
        if not isinstance(target, dict):
            self._target_label.hide()
            self._target_label.clear()
            return
        kind = str(target.get("kind", "unknown"))
        if kind == "future_anchor":
            point = target.get("point", [None, None])
            text = (
                f"{t(self._language, 'summary.progression_target')}: "
                f"{t(self._language, 'summary.target.future_anchor')} "
                f"({point[0]:.3f}, {point[1]:.3f})"
            )
        elif kind == "guide_endpoint":
            point = target.get("point", [None, None])
            guide_id = str(target.get("guide_id", "guide"))
            closed_loop = bool(target.get("closed_loop", False))
            suffix = f" | {t(self._language, 'summary.target.closed_loop')}" if closed_loop else ""
            text = (
                f"{t(self._language, 'summary.progression_target')}: "
                f"{t(self._language, 'summary.target.endpoint')} {guide_id} "
                f"({point[0]:.3f}, {point[1]:.3f}){suffix}"
            )
        else:
            endpoints = target.get("guide_endpoints", [])
            formatted = []
            if isinstance(endpoints, list):
                for endpoint in endpoints:
                    if not isinstance(endpoint, dict):
                        continue
                    point = endpoint.get("point", [None, None])
                    guide_id = str(endpoint.get("guide_id", "guide"))
                    formatted.append(f"{guide_id}@({point[0]:.3f}, {point[1]:.3f})")
            text = (
                f"{t(self._language, 'summary.progression_target')}: "
                f"{t(self._language, 'summary.target.endpoints')} "
                + ", ".join(formatted)
            )
        self._target_label.setStyleSheet(
            "QLabel {"
            "background: rgba(240, 240, 240, 0.92);"
            "color: #222;"
            "border: 1px solid rgba(0,0,0,0.18);"
            "border-radius: 4px;"
            "padding: 6px;"
            "}"
        )
        self._target_label.setText(text)
        self._target_label.show()
