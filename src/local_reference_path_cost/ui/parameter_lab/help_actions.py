from __future__ import annotations

from pathlib import Path

from local_reference_path_cost.ui.help.render import parameter_help_html
from local_reference_path_cost.ui.locale import guide_doc_path, t
from local_reference_path_cost.ui.widgets.text_viewer_dialog import TextViewerDialog


class ParameterLabHelpActions:
    def __init__(self, *, repo_root: Path, parent) -> None:
        self._repo_root = repo_root
        self._parent = parent
        self._parameter_help_dialog: TextViewerDialog | None = None
        self._guide_dialog: TextViewerDialog | None = None

    @property
    def parameter_help_dialog(self) -> TextViewerDialog | None:
        return self._parameter_help_dialog

    @property
    def guide_dialog(self) -> TextViewerDialog | None:
        return self._guide_dialog

    def update_repo_root(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def retranslate(self, language: str) -> None:
        if self._parameter_help_dialog is not None:
            self._parameter_help_dialog.set_text_document(
                title=t(language, "help.parameter.title"),
                text=parameter_help_html(language).strip(),
                text_format="html",
                language=language,
            )
        if self._guide_dialog is not None:
            self._guide_dialog.set_source_document(
                title=t(language, "help.guide.title"),
                source_path=guide_doc_path(self._repo_root, language),
                language=language,
            )

    def show_parameter_help(self, language: str) -> None:
        if self._parameter_help_dialog is None:
            self._parameter_help_dialog = TextViewerDialog(
                title=t(language, "help.parameter.title"),
                text=parameter_help_html(language).strip(),
                text_format="html",
                language=language,
                parent=self._parent,
            )
        self._parameter_help_dialog.show()
        self._parameter_help_dialog.raise_()
        self._parameter_help_dialog.activateWindow()

    def show_guide(self, language: str) -> None:
        if self._guide_dialog is None:
            self._guide_dialog = TextViewerDialog(
                title=t(language, "help.guide.title"),
                source_path=guide_doc_path(self._repo_root, language),
                language=language,
                parent=self._parent,
            )
        self._guide_dialog.show()
        self._guide_dialog.raise_()
        self._guide_dialog.activateWindow()
