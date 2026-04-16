from __future__ import annotations

from pathlib import Path
import re

from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)

from driving_preference_field.ui.locale import DEFAULT_LANGUAGE, t


HEADING_PATTERN = re.compile(r"^(#{1,2})\s+(.+?)\s*$")
ANCHOR_PATTERN = re.compile(r'^\s*<a\s+id="([^"]+)"></a>\s*$')


class TextViewerDialog(QDialog):
    def __init__(
        self,
        *,
        title: str,
        text: str = "",
        text_format: str = "markdown",
        source_path: Path | None = None,
        home_path: Path | None = None,
        language: str = DEFAULT_LANGUAGE,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.resize(860, 720)
        self._title = title
        self._language = language
        self._source_path = source_path.resolve() if source_path is not None else None
        self._home_path = home_path.resolve() if home_path is not None else self._source_path
        self._current_source_path = self._source_path
        self._text_payload = text
        self._text_format = text_format
        self._current_anchor = ""

        self._text = QTextBrowser()
        self._text.setReadOnly(True)
        self._text.setOpenLinks(True)
        self._text.setOpenExternalLinks(True)
        self._text.document().setDocumentMargin(16)
        nav_row = None
        if self._source_path is not None:
            nav_row = QHBoxLayout()
            self._back_button = QPushButton()
            self._forward_button = QPushButton()
            self._home_button = QPushButton()
            self._jump_label = QLabel()
            self._jump_selector = QComboBox()
            self._jump_selector.currentIndexChanged.connect(self._on_jump_selected)
            self._back_button.clicked.connect(self._text.backward)
            self._forward_button.clicked.connect(self._text.forward)
            self._home_button.clicked.connect(self._go_home)
            self._text.backwardAvailable.connect(self._back_button.setEnabled)
            self._text.forwardAvailable.connect(self._forward_button.setEnabled)
            self._text.sourceChanged.connect(self._on_source_changed)
            self._back_button.setEnabled(False)
            self._forward_button.setEnabled(False)
            nav_row.addWidget(self._back_button)
            nav_row.addWidget(self._forward_button)
            nav_row.addWidget(self._home_button)
            nav_row.addWidget(self._jump_label)
            nav_row.addWidget(self._jump_selector, 1)
            nav_row.addStretch(1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        self._close_button = buttons.button(QDialogButtonBox.StandardButton.Close)

        layout = QVBoxLayout(self)
        if nav_row is not None:
            layout.addLayout(nav_row)
        layout.addWidget(self._text)
        layout.addWidget(buttons)
        self._load_current_content()
        self.retranslate(self._language)

    def set_source_document(self, *, title: str, source_path: Path | None, language: str) -> None:
        self._title = title
        self._language = language
        self._source_path = source_path.resolve() if source_path is not None else None
        self._home_path = self._source_path
        self._current_source_path = self._source_path
        self._text_payload = ""
        self._text_format = "markdown"
        self._load_current_content()
        self.retranslate(language)

    def set_text_document(self, *, title: str, text: str, text_format: str, language: str) -> None:
        self._title = title
        self._language = language
        self._source_path = None
        self._home_path = None
        self._current_source_path = None
        self._text_payload = text
        self._text_format = text_format
        self._load_current_content()
        self.retranslate(language)

    def retranslate(self, language: str) -> None:
        self._language = language
        self.setWindowTitle(self._title)
        if hasattr(self, "_back_button"):
            self._back_button.setText(t(language, "viewer.back"))
            self._forward_button.setText(t(language, "viewer.forward"))
            self._home_button.setText(t(language, "viewer.home"))
            self._jump_label.setText(t(language, "viewer.jump_to"))
            if self._jump_selector.count() > 0:
                self._jump_selector.setItemText(0, t(language, "viewer.jump_to"))
        self._close_button.setText(t(language, "viewer.close"))
        if self._source_path is not None and not self._source_path.exists():
            self._text.setPlainText(t(language, "viewer.missing_path", path=self._source_path))

    def _go_home(self) -> None:
        if self._home_path is not None:
            self._text.setSource(QUrl.fromLocalFile(str(self._home_path)))
        else:
            self._text.home()

    def _on_source_changed(self, url: QUrl) -> None:
        if not url.isLocalFile():
            return
        self._current_source_path = Path(url.toLocalFile()).resolve()
        self._rebuild_jump_targets(self._current_source_path, fragment=url.fragment())

    def _on_jump_selected(self, index: int) -> None:
        if index <= 0 or not hasattr(self, "_jump_selector"):
            return
        anchor = str(self._jump_selector.itemData(index) or "")
        if not anchor:
            return
        self._current_anchor = anchor
        self._text.scrollToAnchor(anchor)

    def _rebuild_jump_targets(self, source_path: Path, *, fragment: str = "") -> None:
        if not hasattr(self, "_jump_selector") or not source_path.exists():
            return
        headings = self._parse_headings(source_path)
        self._jump_selector.blockSignals(True)
        self._jump_selector.clear()
        self._jump_selector.addItem(t(self._language, "viewer.jump_to"), "")
        for level, title, anchor in headings:
            prefix = "" if level == 1 else "  "
            self._jump_selector.addItem(f"{prefix}{title}", anchor)
        target_anchor = fragment or self._current_anchor
        if target_anchor:
            index = self._jump_selector.findData(target_anchor)
            if index != -1:
                self._jump_selector.setCurrentIndex(index)
            else:
                self._jump_selector.setCurrentIndex(0)
        else:
            self._jump_selector.setCurrentIndex(0)
        self._jump_selector.setEnabled(self._jump_selector.count() > 1)
        self._jump_selector.blockSignals(False)

    def _parse_headings(self, source_path: Path) -> list[tuple[int, str, str]]:
        headings: list[tuple[int, str, str]] = []
        pending_anchor = ""
        for raw_line in source_path.read_text(encoding="utf-8").splitlines():
            anchor_match = ANCHOR_PATTERN.match(raw_line)
            if anchor_match:
                pending_anchor = anchor_match.group(1)
                continue
            heading_match = HEADING_PATTERN.match(raw_line)
            if not heading_match:
                continue
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip().strip("`")
            anchor = pending_anchor or self._slugify_heading(title)
            headings.append((level, title, anchor))
            pending_anchor = ""
        return headings

    @staticmethod
    def _slugify_heading(title: str) -> str:
        slug = re.sub(r"<[^>]+>", "", title)
        slug = re.sub(r"[`*_]+", "", slug)
        slug = slug.strip().lower()
        slug = re.sub(r"[^0-9a-zA-Z가-힣]+", "-", slug)
        return slug.strip("-")

    def _load_current_content(self) -> None:
        if self._source_path is not None and self._source_path.exists():
            search_paths = [self._source_path.parent]
            if self._source_path.parent.parent not in search_paths:
                search_paths.append(self._source_path.parent.parent)
            self._text.setSearchPaths([str(path) for path in search_paths])
            self._text.setSource(QUrl.fromLocalFile(str(self._source_path)))
            self._rebuild_jump_targets(self._source_path)
            return
        if self._source_path is not None:
            self._text.setPlainText(t(self._language, "viewer.missing_path", path=self._source_path))
            return
        if self._text_format == "html":
            self._text.setHtml(self._text_payload)
        elif self._text_format == "plain":
            self._text.setPlainText(self._text_payload)
        else:
            self._text.setMarkdown(self._text_payload)
