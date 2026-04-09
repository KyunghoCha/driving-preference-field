from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QTextBrowser, QVBoxLayout


class TextViewerDialog(QDialog):
    def __init__(self, *, title: str, text: str, text_format: str = "markdown", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(860, 720)

        self._text = QTextBrowser()
        self._text.setReadOnly(True)
        self._text.setOpenExternalLinks(False)
        self._text.document().setDocumentMargin(16)
        if text_format == "html":
            self._text.setHtml(text)
        elif text_format == "plain":
            self._text.setPlainText(text)
        else:
            self._text.setMarkdown(text)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self._text)
        layout.addWidget(buttons)
