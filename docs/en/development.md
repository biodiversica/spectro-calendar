# Development

*English · [Português (Brasil)](../pt-BR/development.md)*

```bash
git clone https://github.com/biodiversica/spectro-calendar.git
cd spectro-calendar
uv sync               # installs the project and the development tools
uv run ruff check .   # lint
uv run pytest         # tests
uv run spectro-calendar /path/to/recordings
```

## Tests and CI

The tests generate short synthetic recordings, run the complete tool on them
and inspect the generated files. The ffmpeg backend test is skipped when
ffmpeg is not installed. Continuous integration runs the lint and the tests on
Linux, macOS and Windows, and also runs the installers on all three systems
with the built package.

## Project Layout

```
src/spectro_calendar/
├── __init__.py   # package version
├── __main__.py   # enables `python -m spectro_calendar`
├── cli.py        # argument parsing and the complete processing pipeline
└── richhelp.py   # formatted --help output
tests/            # end-to-end tests
scripts/          # installers attached to each release
docs/             # this documentation, in English and Portuguese
```

[How It Works](how-it-works.md) walks through `cli.py` step by step.

## Documentation

The documentation lives in [`docs/`](../README.md), one page per topic in
English and Portuguese under the same file name. A change to one language
should be made to the other in the same commit.
