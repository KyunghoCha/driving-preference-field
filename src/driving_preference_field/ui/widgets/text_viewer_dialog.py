from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)


class TextViewerDialog(QDialog):
    def __init__(
        self,
        *,
        title: str,
        text: str = "",
        text_format: str = "markdown",
        source_path: Path | None = None,
        home_path: Path | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(860, 720)
        self._source_path = source_path.resolve() if source_path is not None else None

        self._text = QTextBrowser()
        self._text.setReadOnly(True)
        self._text.setOpenLinks(True)
        self._text.setOpenExternalLinks(True)
        self._text.document().setDocumentMargin(16)
        nav_row = None
        if self._source_path is not None and self._source_path.exists():
            search_paths = [self._source_path.parent]
            if self._source_path.parent.parent not in search_paths:
                search_paths.append(self._source_path.parent.parent)
            self._text.setSearchPaths([str(path) for path in search_paths])
            self._text.setSource(QUrl.fromLocalFile(str(self._source_path)))
            nav_row = QHBoxLayout()
            self._back_button = QPushButton("Back")
            self._forward_button = QPushButton("Forward")
            self._home_button = QPushButton("Home")
            self._back_button.clicked.connect(self._text.backward)
            self._forward_button.clicked.connect(self._text.forward)
            self._home_button.clicked.connect(self._text.home)
            self._text.backwardAvailable.connect(self._back_button.setEnabled)
            self._text.forwardAvailable.connect(self._forward_button.setEnabled)
            self._back_button.setEnabled(False)
            self._forward_button.setEnabled(False)
            nav_row.addWidget(self._back_button)
            nav_row.addWidget(self._forward_button)
            nav_row.addWidget(self._home_button)
            nav_row.addStretch(1)
        elif self._source_path is not None:
            self._text.setPlainText(f"문서를 읽을 수 없습니다.\n\nexpected path: {self._source_path}")
        elif text_format == "html":
            self._text.setHtml(text)
        elif text_format == "plain":
            self._text.setPlainText(text)
        else:
            self._text.setMarkdown(text)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        if nav_row is not None:
            layout.addLayout(nav_row)
        layout.addWidget(self._text)
        layout.addWidget(buttons)
