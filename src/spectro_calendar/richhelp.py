"""
spectro_calendar.richhelp
=========================

Typer-styled ``--help`` output for the ``argparse`` parser in :mod:`cli`.

The sibling ``segment-reviewer`` tool builds its CLI on Typer, whose help
screen Rich renders as a padded usage line, the description, and one rounded
panel per parameter group. This module reproduces that layout and its palette
on top of ``argparse`` so both tools' ``-h`` look the same: the styles and
panel construction below are ported from ``typer.rich_utils``.

argparse's ``formatter_class`` hook cannot express panels, so the entry point
is :class:`RichHelpParser` instead: it overrides ``format_help`` and leaves
argument parsing untouched.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, NoReturn

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console, RenderableType
from rich.highlighter import RegexHighlighter
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# Styles, copied from typer.rich_utils so the two CLIs read identically.
STYLE_OPTION = "bold cyan"
STYLE_SWITCH = "bold green"
STYLE_NEGATIVE_OPTION = "bold magenta"
STYLE_NEGATIVE_SWITCH = "bold red"
STYLE_TYPES = "bold yellow"
STYLE_TYPES_SEPARATOR = "dim"
STYLE_USAGE = "yellow"
STYLE_USAGE_COMMAND = "bold"
STYLE_HELPTEXT_FIRST_LINE = ""
STYLE_HELPTEXT = "dim"
STYLE_OPTION_HELP = ""
STYLE_OPTION_DEFAULT = "dim"
STYLE_REQUIRED_SHORT = "red"
STYLE_REQUIRED_LONG = "dim red"
STYLE_OPTIONS_PANEL_BORDER = "dim"
ALIGN_OPTIONS_PANEL = "left"
STYLE_OPTIONS_TABLE_PADDING = (0, 1)
STYLE_ERROR = "red"
STYLE_ERRORS_PANEL_BORDER = "red"
ALIGN_ERRORS_PANEL = "left"
STYLE_ERRORS_SUGGESTION = "dim"

DEFAULT_STRING = "[default: {}]"
REQUIRED_SHORT_STRING = "*"
REQUIRED_LONG_STRING = "[required]"
ARGUMENTS_PANEL_TITLE = "Arguments"
OPTIONS_PANEL_TITLE = "Options"
ERRORS_PANEL_TITLE = "Error"
RICH_HELP = "Try [blue]'{command_path} {help_option}'[/] for help."


class OptionHighlighter(RegexHighlighter):
    """Colours option flags and ``<type>`` markers wherever they appear."""

    highlights = [
        r"(^|\W)(?P<switch>\-\w+)(?![a-zA-Z0-9])",
        r"(^|\W)(?P<option>\-\-[\w\-]+)(?![a-zA-Z0-9])",
        r"(?P<types>\<[^\>]+\>)",
        r"(?P<usage>Usage: )",
    ]


class NegativeOptionHighlighter(RegexHighlighter):
    """Colours the ``--no-x`` half of a paired boolean flag."""

    highlights = [
        r"(^|\W)(?P<negative_switch>\-\w+)(?![a-zA-Z0-9])",
        r"(^|\W)(?P<negative_option>\-\-[\w\-]+)(?![a-zA-Z0-9])",
    ]


class TypesHighlighter(RegexHighlighter):
    """Dims the brackets around a type so only the type name stands out."""

    highlights = [
        r"^(?P<types_sep>(\[|<))",
        r"(?P<types_sep>\|)",
        r"(?P<types_sep>(\]|>))(\.\.\.)?$",
    ]


highlighter = OptionHighlighter()
negative_highlighter = NegativeOptionHighlighter()
types_highlighter = TypesHighlighter()


def _console(stderr: bool = False) -> Console:
    return Console(
        theme=Theme(
            {
                "option": STYLE_OPTION,
                "switch": STYLE_SWITCH,
                "negative_option": STYLE_NEGATIVE_OPTION,
                "negative_switch": STYLE_NEGATIVE_SWITCH,
                "types": STYLE_TYPES,
                "types_sep": STYLE_TYPES_SEPARATOR,
                "usage": STYLE_USAGE,
            },
        ),
        highlighter=highlighter,
        stderr=stderr,
    )


def _takes_value(action: argparse.Action) -> bool:
    """False for flags like ``--clear`` or ``-h``, which consume no argument."""
    return action.nargs != 0


def _type_name(action: argparse.Action) -> str:
    """The ``<...>`` type marker for an action, in Click's vocabulary."""
    t = action.type
    if t is None:
        name = "str"
    elif t is Path:
        name = "path"
    else:
        name = getattr(t, "__name__", str(t))
    marker = f"<{name}>"
    if action.nargs in ("*", "+") or isinstance(action.nargs, int):
        marker += "..."
    return marker


def _metavar(action: argparse.Action) -> str:
    if action.metavar:
        return str(action.metavar)
    return (action.dest or "").upper()


def _is_required(action: argparse.Action) -> bool:
    if action.option_strings:
        return bool(action.required)
    return action.nargs not in ("?", "*")


def _default_text(action: argparse.Action) -> str:
    """Typer shows a ``[default: ...]`` tag, but not for empty or boolean ones."""
    default = action.default
    if default is None or default is argparse.SUPPRESS or isinstance(default, bool):
        return ""
    if isinstance(default, (list, tuple)):
        return ", ".join(str(x) for x in default)
    return str(default)


def _expand_help(parser: argparse.ArgumentParser, action: argparse.Action) -> str:
    """Apply argparse's own ``%(default)s``-style substitutions to a help string."""
    if not action.help:
        return ""
    params = {k: v for k, v in vars(action).items() if v is not argparse.SUPPRESS}
    params["prog"] = parser.prog
    for name, value in list(params.items()):
        if hasattr(value, "__name__"):
            params[name] = value.__name__
    if params.get("choices") is not None:
        params["choices"] = ", ".join(str(c) for c in params["choices"])
    try:
        return action.help % params
    except (TypeError, ValueError, KeyError):
        return action.help


def _help_cell(parser: argparse.ArgumentParser, action: argparse.Action) -> Columns:
    """The right-hand cell: help prose, then the default and required tags."""
    items: list[RenderableType] = []
    text = _expand_help(parser, action)
    if text:
        paragraphs = [p.replace("\n", " ").strip() for p in text.split("\n\n")]
        items.append(
            highlighter(Text("\n".join(paragraphs).strip(), style=STYLE_OPTION_HELP))
        )
    default = _default_text(action)
    if default:
        items.append(Text(DEFAULT_STRING.format(default), style=STYLE_OPTION_DEFAULT))
    if _is_required(action):
        items.append(Text(REQUIRED_LONG_STRING, style=STYLE_REQUIRED_LONG))
    return Columns(items)


def _panel(
    parser: argparse.ArgumentParser,
    name: str,
    actions: list[argparse.Action],
    console: Console,
) -> None:
    """Render one group of parameters as a rounded panel, Typer-style."""
    rows: list[list[RenderableType]] = []
    required_flags: list[RenderableType] = []
    for action in actions:
        long_strs = [o for o in action.option_strings if o.startswith("--")]
        short_strs = [o for o in action.option_strings if not o.startswith("--")]
        secondary_long: list[str] = []
        if not action.option_strings:  # a positional: its name goes in the short column
            short_strs = [_metavar(action)]
        else:
            # BooleanOptionalAction pairs --flag with --no-flag; show the negative
            # half in its own column, as Typer does for `--x/--no-x`.
            negatives = [o for o in long_strs if o.startswith("--no-")]
            if negatives and len(long_strs) > len(negatives):
                secondary_long = negatives
                long_strs = [o for o in long_strs if o not in negatives]

        types = Text(style=STYLE_TYPES, overflow="fold")
        if _takes_value(action):
            types.append(_type_name(action))

        required_flags.append(
            Text(REQUIRED_SHORT_STRING, style=STYLE_REQUIRED_SHORT)
            if _is_required(action)
            else ""
        )
        rows.append(
            [
                highlighter(",".join(long_strs)),
                highlighter(",".join(short_strs)),
                negative_highlighter(",".join(secondary_long)),
                types_highlighter(types),
                _help_cell(parser, action),
            ]
        )

    if not rows:
        return
    if any(bool(flag) for flag in required_flags):
        rows = [[flag, *row] for flag, row in zip(required_flags, rows)]

    table = Table(
        highlight=True,
        show_header=False,
        expand=True,
        box=None,
        border_style=None,
        row_styles=None,
        pad_edge=False,
        padding=STYLE_OPTIONS_TABLE_PADDING,
        leading=0,
        show_lines=False,
    )
    for row in rows:
        table.add_row(*row)
    console.print(
        Panel(
            table,
            border_style=STYLE_OPTIONS_PANEL_BORDER,
            title=name,
            title_align=ALIGN_OPTIONS_PANEL,
            box=box.ROUNDED,
        )
    )


def _usage(parser: argparse.ArgumentParser, positionals: list[argparse.Action]) -> str:
    """``Usage: prog [OPTIONS] {REQUIRED} [OPTIONAL]``, as Click writes it."""
    pieces = [parser.prog, "[OPTIONS]"]
    for action in positionals:
        metavar = _metavar(action)
        pieces.append(f"{{{metavar}}}" if _is_required(action) else f"[{metavar}]")
        if action.nargs in ("*", "+"):
            pieces[-1] += "..."
    return "Usage: " + " ".join(pieces)


def _description(parser: argparse.ArgumentParser) -> Align:
    """First paragraph plain, the rest dim — Typer's treatment of the docstring."""
    text = (parser.description or "").strip()
    first, *rest = text.split("\n\n")
    parts: list[RenderableType] = [
        highlighter(Text(first.replace("\n", " ").strip(), style=STYLE_HELPTEXT_FIRST_LINE))
    ]
    if rest:
        parts.append(Text(""))
        parts.append(highlighter(Text("\n\n".join(rest), style=STYLE_HELPTEXT)))
    return Align(_stack(parts), pad=False)


def _stack(parts: list[RenderableType]) -> Table:
    """Lay renderables out one per line, the way Rich's @group decorator does."""
    grid = Table.grid()
    grid.add_column()
    for part in parts:
        grid.add_row(part)
    return grid


class RichHelpParser(argparse.ArgumentParser):
    """An ``ArgumentParser`` whose ``-h`` prints Typer's Rich help screen."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for action in self._actions:
            if isinstance(action, argparse._HelpAction):
                action.help = "Show this message and exit."  # Typer's wording

    def format_help(self) -> str:
        console = _console()
        with console.capture() as capture:
            self._render_help(console)
        return capture.get()

    def _render_help(self, console: Console) -> None:
        positionals = [a for a in self._actions if not a.option_strings]
        # Typer lists --help last; argparse registers it first.
        optionals = sorted(
            (a for a in self._actions if a.option_strings),
            key=lambda a: isinstance(a, argparse._HelpAction),
        )

        console.print(
            Padding(highlighter(_usage(self, positionals)), 1), style=STYLE_USAGE_COMMAND
        )
        if self.description:
            console.print(Padding(_description(self), (0, 1, 1, 1)))
        _panel(self, ARGUMENTS_PANEL_TITLE, positionals, console)
        _panel(self, OPTIONS_PANEL_TITLE, optionals, console)

    def error(self, message: str) -> NoReturn:
        """Report a usage error the way Typer does: usage, a hint, a red panel."""
        console = _console(stderr=True)
        positionals = [a for a in self._actions if not a.option_strings]
        console.print(highlighter(_usage(self, positionals)), style=STYLE_USAGE_COMMAND)
        help_option = self._help_option()
        if help_option:
            console.print(
                RICH_HELP.format(
                    command_path=escape(self.prog), help_option=help_option
                ),
                style=STYLE_ERRORS_SUGGESTION,
            )
        console.print(
            Panel(
                highlighter(message),
                border_style=STYLE_ERRORS_PANEL_BORDER,
                title=ERRORS_PANEL_TITLE,
                title_align=ALIGN_ERRORS_PANEL,
                box=box.ROUNDED,
            )
        )
        self.exit(2)

    def _help_option(self) -> str:
        """The flag to suggest in the hint line, or "" when help is disabled."""
        for action in self._actions:
            if isinstance(action, argparse._HelpAction) and action.option_strings:
                return action.option_strings[0]
        return ""


def fatal(message: str, code: int = 1) -> NoReturn:
    """Exit with a red message on stderr.

    How ``segment-reviewer`` reports a failure that isn't a usage error -- those
    get the panel above, these get Typer's plain ``secho(fg=RED, err=True)``.
    The message is passed as ``Text`` so brackets in a path are not read as
    markup or highlighted.
    """
    _console(stderr=True).print(Text(message, style=STYLE_ERROR))
    raise SystemExit(code)
