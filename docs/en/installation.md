# Installation

*English · [Português (Brasil)](../pt-BR/installation.md)*

**Without Python.** The installer sets up everything required and adds the
`spectro-calendar` command. Running it again upgrades the installation.

On Windows, open PowerShell and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | Out-String | iex"
```

On macOS and Linux, open a terminal and run:

```sh
curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | sh
```

The installer first lists what it is going to do and asks for confirmation
before changing anything. It then performs the following steps:

1. Installs [uv](https://docs.astral.sh/uv/) into `~/.local/bin` if it is not
   already present. uv downloads its own Python, so no prior installation is
   required, and any existing Python installation is left unchanged.
2. Runs `uv tool install --python 3.12 spectro-calendar`, which installs the
   tool in an isolated environment and adds `spectro-calendar` to the PATH.

The command becomes available in terminals opened after the installation. The
environment variable `SPECTRO_CALENDAR_PACKAGE` changes what the installer
installs (for example, a specific version such as `spectro-calendar==0.1.0`),
and `SPECTRO_CALENDAR_YES=1` skips the confirmation, for installing or
uninstalling from a script.

**Uninstalling.** Run the installer again with `SPECTRO_CALENDAR_UNINSTALL=1`.
It lists what it is going to remove and asks for confirmation first. On
Windows, run in PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c '$env:SPECTRO_CALENDAR_UNINSTALL=1; irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | Out-String | iex'
```

On macOS and Linux:

```sh
curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | SPECTRO_CALENDAR_UNINSTALL=1 sh
```

This removes spectro-calendar. The calendars and spectrograms it made are
never removed, and neither is uv, which other programs may use. Running
`uv tool uninstall spectro-calendar` directly has the same effect.

**With uv or pip.** spectro-calendar is published on PyPI and requires
Python 3.10 or later:

```bash
uv tool install spectro-calendar   # as an isolated command-line tool
pip install spectro-calendar       # or with pip, into the current environment
```

`uv tool upgrade spectro-calendar` upgrades the tool. It can also be run once,
without a permanent installation, with `uvx spectro-calendar /path/to/recordings`.

**Optional system program.** [ffmpeg](https://ffmpeg.org/), which is not
installed by the methods above, enables the faster spectrogram backend
(`--use-ffmpeg`; see [Backends](backends.md)). It is available through the
usual package managers, for example `brew install ffmpeg`,
`sudo apt install ffmpeg` or `winget install --id Gyan.FFmpeg`.

**From source.** To modify the code, clone the repository and install it with
uv, which creates `.venv` from `pyproject.toml` and `uv.lock`:

```bash
git clone https://github.com/biodiversica/spectro-calendar.git
cd spectro-calendar
uv sync
uv run spectro-calendar /path/to/recordings
```

Alternatively, with pip in a virtual environment (an editable installation
requires `pip>=21.3`):

```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

`requirements.txt` lists the same runtime dependencies as `pyproject.toml`.
From a source checkout, the commands in this documentation are prefixed with
`uv run`, or run as `python -m spectro_calendar` in an activated environment.
See [Development](development.md) for the tests and the project layout.
