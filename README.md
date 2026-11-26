# |=|=| spectro-calendar

*English · [Português (Brasil)](https://github.com/biodiversica/spectro-calendar/blob/main/README.pt-BR.md)*

spectro-calendar generates a browsable HTML calendar of spectrograms from a
folder of `.wav` recordings made by an
[AudioMoth](https://www.openacousticdevices.info/audiomoth) or any other
passive acoustic recorder that writes a timestamp into each filename.

Each recording is represented by a spectrogram thumbnail placed in a table,
with dates as columns and times of day as rows, so that weeks of acoustic
monitoring data can be surveyed at a glance. Optionally, each cell includes an
audio player for the recording, a playback speed control for listening to
ultrasound, and a checkbox for selecting recordings and exporting the
selection as a list. With `--save-fullsize`, a full-resolution spectrogram is
also written next to each thumbnail, for closer inspection.

The tool is an extended adaptation of the
[scripts created by Nathan Wolek](https://github.com/nwolek/audiomoth-scripts).

## Installation

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

The installer lists what it is going to do and asks for confirmation before
changing anything.

**Uninstalling.** Run the installer again with `SPECTRO_CALENDAR_UNINSTALL=1`.
On Windows, run in PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c '$env:SPECTRO_CALENDAR_UNINSTALL=1; irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | Out-String | iex'
```

On macOS and Linux:

```sh
curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | SPECTRO_CALENDAR_UNINSTALL=1 sh
```

Calendars and spectrograms are never removed.

**With uv or pip.** spectro-calendar is published on PyPI and requires
Python 3.10 or later:

```bash
uv tool install spectro-calendar   # as an isolated command-line tool
pip install spectro-calendar       # or with pip, into the current environment
```

[Installation](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/installation.md)
describes what the installer does, its environment variables, the optional
ffmpeg backend, and installing from source.

## Quick Start

```bash
spectro-calendar /data/site-1                          # calendar written beside the recordings
spectro-calendar /data/site-1 --output-dir calendar    # or into its own folder
spectro-calendar /data/site-1 --include-audio --speed-control --annotate
spectro-calendar --config example_config.yaml          # every option from a YAML file
```

Open the `index_.html` the run writes in a web browser. Filenames are read as
`YYYYMMDD_HHMMSS.WAV`, the AudioMoth convention, unless `--datetime-format`
and `--filename-prefix` say otherwise. `spectro-calendar --help` lists every
option.

## Documentation

| Page | Contents |
|---|---|
| [Installation](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/installation.md) | The installer, uninstalling, uv and pip, ffmpeg, from source |
| [Making a Calendar](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/usage.md) | The files a run writes, a separate output directory, subfolders, the settings panel |
| [Configuration File](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/configuration.md) | Setting options in YAML, precedence over the command line |
| [Command-Line Options](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/cli.md) | An example and every option |
| [Filename Formats](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/filename-formats.md) | `--datetime-format` and `--filename-prefix` for other recorders |
| [Listening to Ultrasound](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/ultrasound.md) | The playback speed selector and time expansion |
| [Annotation Mode](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/annotation.md) | Selecting recordings, Shift+click ranges, exporting the list |
| [Backends](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/backends.md) | ffmpeg and scipy compared |
| [How It Works](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/how-it-works.md) | The processing pipeline, step by step |
| [Development](https://github.com/biodiversica/spectro-calendar/blob/main/docs/en/development.md) | Working on spectro-calendar itself, tests and CI, project layout |

## License

[MIT](https://github.com/biodiversica/spectro-calendar/blob/main/LICENSE)
