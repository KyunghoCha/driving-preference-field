from __future__ import annotations

import json

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget


class SummaryPanelWidget(QWidget):
    noteChanged = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._note = QTextEdit()
        self._note.textChanged.connect(self._emit_note_changed)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Summary"))
        layout.addWidget(self._text)
        layout.addWidget(QLabel("Qualitative Note"))
        layout.addWidget(self._note)

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
