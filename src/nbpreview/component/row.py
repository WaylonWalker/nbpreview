"""Jupyter notebook rows."""
import dataclasses
from dataclasses import InitVar
from typing import Optional
from typing import Tuple
from typing import Union

from nbformat import NotebookNode

from . import execution_indicator
from . import input
from .display_data import DisplayData
from .error import Error
from .execution_indicator import Execution
from .input import Cell
from .link import Hyperlink
from .stream import Stream

Output = Union[DisplayData, Error, Hyperlink, Stream]
TableRow = Union[Tuple[Union[Execution, str], Cell], Tuple[Cell]]


@dataclasses.dataclass
class Row:
    """A Jupyter notebook row."""

    cell: Cell
    plain: bool
    execution: InitVar[Optional[Execution]] = None

    def __post_init__(self, execution: Optional[Execution]) -> None:
        """Initialize the execution indicator."""
        self.execution: Union[Execution, str]
        self.execution = execution_indicator.choose_execution(execution)

    def to_table_row(self) -> TableRow:
        """Convert to row for table usage."""
        table_row: TableRow
        if self.plain:
            table_row = (self.cell,)
        else:
            table_row = (self.execution, self.cell)
        return table_row


def render_input_row(
    cell: NotebookNode,
    plain: bool,
    pad: Tuple[int, int, int, int],
    language: str,
    theme: str,
    unicode_border: Optional[bool] = None,
) -> Row:
    """Render a Jupyter Notebook cell.

    Args:
        cell (NotebookNode): The cell to render.
        plain (bool): Only show plain style. No decorations such as
            boxes or execution counts.
        pad (Tuple[int, int, int, int]): The output padding to use.
        language (str): The programming language of the notebook. Will
            be used when highlighting the syntax of code cells.
        theme (str): The theme to use for syntax highlighting. May be
            "ansi_light", "ansi_dark", or any Pygments theme. By default
            "ansi_dark".
        unicode_border (Optional[bool]): Whether to render the cell
            borders using unicode characters. Will autodetect by
            default.

    Returns:
        Row: The execution count indicator and cell
            content.
    """
    cell_type = cell.get("cell_type")
    source = cell.source
    default_lexer_name = "ipython" if language == "python" else language
    safe_box = None if unicode_border is None else not unicode_border
    rendered_cell: Optional[Cell] = None
    execution: Union[Execution, None] = None
    top_pad = not plain
    if cell_type == "markdown":
        rendered_cell = input.MarkdownCell(source, theme=theme, pad=pad)

    elif cell_type == "code":
        execution = Execution(cell.execution_count, top_pad=top_pad)
        rendered_cell = input.CodeCell(
            source,
            plain=plain,
            safe_box=safe_box,
            theme=theme,
            default_lexer_name=default_lexer_name,
        )

    # Includes cell_type == "raw"
    else:
        rendered_cell = Cell(source, plain=plain, safe_box=safe_box)

    cell_row = Row(rendered_cell, plain=plain, execution=execution)
    return cell_row
