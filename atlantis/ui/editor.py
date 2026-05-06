"""Source editor widget for Mermaid text."""

from __future__ import annotations

from collections.abc import Iterable

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QSyntaxHighlighter, QTextCharFormat, QTextFormat
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget


class MermaidHighlighter(QSyntaxHighlighter):
    """Minimal Mermaid-aware syntax highlighter for MVP."""

    def __init__(self, parent: object) -> None:
        super().__init__(parent)
        self._keyword_format = QTextCharFormat()
        self._keyword_format.setForeground(QColor("#2f6feb"))
        self._keyword_format.setFontWeight(QFont.Weight.Bold)

        self._comment_format = QTextCharFormat()
        self._comment_format.setForeground(QColor("#6a737d"))
        self._comment_format.setFontItalic(True)

    def highlightBlock(self, text: str) -> None:
        """Apply basic styles for Mermaid declarations and comments."""
        keywords = (
            "flowchart",
            "graph",
            "sequenceDiagram",
            "classDiagram",
            "stateDiagram",
            "erDiagram",
        )
        for keyword in keywords:
            start = text.find(keyword)
            if start >= 0:
                self.setFormat(start, len(keyword), self._keyword_format)

        comment_prefix = "%%"
        if text.strip().startswith(comment_prefix):
            self.setFormat(0, len(text), self._comment_format)


class LineNumberArea(QWidget):
    """Gutter widget that paints line numbers."""

    def __init__(self, editor: MermaidEditor) -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event: object) -> None:
        self.editor.line_number_area_paint_event(event)


class MermaidEditor(QPlainTextEdit):
    """Native source editor with line numbers and lightweight highlighting."""

    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)
        self._highlighter = MermaidHighlighter(self.document())
        self._error_lines: set[int] = set()
        self._line_number_area = LineNumberArea(self)
        self.setPlaceholderText("Write Mermaid source here...")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.setFont(QFont("Menlo", 12))
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.update_line_number_area_width(0)
        self._highlight_current_line()

    def line_number_area_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_number_area_width(self, _: int) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event: object) -> None:
        super().resizeEvent(event)
        contents_rect = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(contents_rect.left(), contents_rect.top(), self.line_number_area_width(), contents_rect.height())
        )

    def line_number_area_paint_event(self, event: object) -> None:
        painter = QPainter(self._line_number_area)
        painter.fillRect(self._line_number_area.rect(), QColor("#f5f5f5"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= self.viewport().rect().bottom():
            if block.isVisible() and bottom >= self.viewport().rect().top():
                painter.setPen(QColor("#8b949e"))
                painter.drawText(
                    0,
                    top,
                    self._line_number_area.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(block_number + 1),
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def set_error_lines(self, lines: Iterable[int]) -> None:
        """Highlight specific one-based line numbers as render errors."""
        self._error_lines = {line for line in lines if line > 0}
        self._highlight_current_line()

    def clear_error_lines(self) -> None:
        """Remove all error line highlights."""
        self._error_lines.clear()
        self._highlight_current_line()

    def _highlight_current_line(self) -> None:
        selections: list[QTextEdit.ExtraSelection] = []
        current_line_selection = QTextEdit.ExtraSelection()
        current_line_selection.format.setBackground(QColor("#f2f8ff"))
        current_line_selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        current_line_selection.cursor = self.textCursor()
        current_line_selection.cursor.clearSelection()
        selections.append(current_line_selection)

        for line_number in sorted(self._error_lines):
            block = self.document().findBlockByNumber(line_number - 1)
            if not block.isValid():
                continue
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor("#fdecea"))
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.setPosition(block.position())
            selection.cursor.clearSelection()
            selections.append(selection)

        self.setExtraSelections(selections)
