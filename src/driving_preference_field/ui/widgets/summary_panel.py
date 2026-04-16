from __future__ import annotations

import json

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from driving_preference_field.ui.locale import DEFAULT_LANGUAGE, t


class SummaryPanelWidget(QWidget):
    noteChanged = pyqtSignal(str)

    def __init__(self, *, language: str = DEFAULT_LANGUAGE) -> None:
        super().__init__()
        self._language = language
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._note = QTextEdit()
        self._note.textChanged.connect(self._emit_note_changed)
        self._summary_label = QLabel()
        self._note_label = QLabel()
        layout = QVBoxLayout(self)
        layout.addWidget(self._summary_label)
        layout.addWidget(self._text)
        layout.addWidget(self._note_label)
        layout.addWidget(self._note)
        self.retranslate(language)

    def set_summary(self, payload: dict[str, object]) -> None:
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
