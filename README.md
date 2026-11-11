# spectro-calendar

*[Versão em português](https://github.com/biodiversica/spectro-calendar/blob/main/README.pt-BR.md)*

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
powershell -ExecutionPolicy ByPass -c "irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | iex"
```

On macOS and Linux, open a terminal and run:

```sh
curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | sh
```

The installer performs the following steps:

1. Installs [uv](https://docs.astral.sh/uv/) into `~/.local/bin` if it is not
   already present. uv downloads its own Python, so no prior installation is
   required, and any existing Python installation is left unchanged.
2. Runs `uv tool install --python 3.12 spectro-calendar`, which installs the
   tool in an isolated environment and adds `spectro-calendar` to the PATH.

The command becomes available in terminals opened after the installation. The
environment variable `SPECTRO_CALENDAR_PACKAGE` changes what the installer
installs (for example, a specific version such as `spectro-calendar==0.1.0`).
To uninstall, run `uv tool uninstall spectro-calendar`.

**With uv or pip.** spectro-calendar is published on PyPI and requires
Python 3.10 or later:

```bash
uv tool install spectro-calendar   # as an isolated command-line tool
pip install spectro-calendar       # or with pip, into the current environment
```

`uv tool upgrade spectro-calendar` upgrades the tool. It can also be run once,
without a permanent installation, with `uvx spectro-calendar /path/to/recordings`.

**Optional system programs.** Two external programs extend the tool. Neither
is installed by the methods above:

- [ffmpeg](https://ffmpeg.org/) enables the faster spectrogram backend
  (`--use-ffmpeg`; see [Backends](#backends)). It is available through the
  usual package managers, for example `brew install ffmpeg`,
  `sudo apt install ffmpeg` or `winget install --id Gyan.FFmpeg`.
- [sshfs](https://github.com/libfuse/sshfs) allows recordings stored on a
  remote machine to be processed (see
  [Remote Recordings over SSH](#remote-recordings-over-ssh)).

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
From a source checkout, the commands in this document are prefixed with
`uv run`, or run as `python -m spectro_calendar` in an activated environment.

## Usage

```bash
spectro-calendar /path/to/recordings
```

The recording directory must contain `.wav` files whose names include the
recording date and time. By default, the tool expects the AudioMoth
convention, `YYYYMMDD_HHMMSS.WAV` (for example, `20260315_063000.WAV`); other
conventions are configured with `--datetime-format` and `--filename-prefix`
(see [Filename Formats](#filename-formats)). Only the top level of the
directory is searched unless `--recursive` is given (see
[Subfolders](#subfolders)).

A run produces the following files, in the recording directory by default or
in the directory given with `--output-dir`:

- `<name>-thumbnail-<label>.png`: one spectrogram thumbnail per recording.
- `<name>-fullsize-<label>.png`: the full-resolution spectrogram, written only
  with `--save-fullsize`.
- `index_<label>.html`: the calendar page.
- `spectrogram-table.css`: the stylesheet used by the calendar page.

`<label>` is the value of `--spec-label`, empty by default. The calendar is
viewed by opening `index_<label>.html` in a web browser. Its columns are
labelled with dates in `DD-MM-YYYY` format, while the date options
(`--dates`, `--start-date`, `--end-date`) take dates as `YYYYMMDD`.

With `--output-dir`, all generated files are written to a separate directory
and the recording directory is only read, never written to:

```bash
spectro-calendar /data/site-1/recordings --output-dir /data/site-1/calendar
```

The audio players (`--include-audio`) refer to the original recordings by a
relative path, so they continue to work although the recordings are not
copied into the output directory. When no relative path exists, as with
recordings and output on different drives on Windows, an absolute path is
used instead.

### Subfolders

By default, only `.wav` files located directly in the recording directory are
processed. With `--recursive`, subfolders are searched as well:

```bash
spectro-calendar /data/site-1/recordings --recursive
```

The images of each recording are then written to a subdirectory of the output
directory that mirrors the location of the recording. For example, a
recording at `recordings/moth-a/20260304_100000.WAV` produces its images
under `calendar/moth-a/`. This prevents recordings with identical names in
different subfolders (typically one folder per recorder or deployment) from
overwriting each other's spectrograms. The calendar page and stylesheet remain
at the top of the output directory.

The calendar has a single cell for each combination of date and time of day.
When two recordings share the same timestamp, for instance two recorders
operating on the same schedule, only one of them can appear in the table. The
tool prints a warning naming both files in that case, and the spectrograms of
all recordings are still generated. To display every recording, the tool can
be run once per subfolder, each time with its own `--output-dir`.

### Configuration File

Options can also be set in a YAML file passed with `--config`:

```bash
spectro-calendar --config example_config.yaml
```

[`example_config.yaml`](https://github.com/biodiversica/spectro-calendar/blob/main/example_config.yaml) contains a complete example.
Each key corresponds to a command-line option, with hyphens replaced by
underscores (for example, `--output-dir` becomes `output_dir`). The recording
directory can also be set, as `recording_dir`, so that a run can be described
entirely by a configuration file.

Options given on the command line take precedence over the configuration
file, which only supplies default values:

```bash
# Uses every value from example_config.yaml, except max_cores, which is set
# to 2 regardless of the value in the file.
spectro-calendar --config example_config.yaml --max-cores 2
```

An unrecognised key in the configuration file is reported as an error, with
the list of valid keys.

### Options

| Option | Default | Description |
|---|---|---|
| `recording_dir` | none | Directory containing the `.wav` recordings. Positional; required unless set as `recording_dir` in the configuration file |
| `--config PATH` | none | YAML file providing default option values (see [Configuration File](#configuration-file)) |
| `--version` | | Show the installed version and exit |
| `--use-ffmpeg` | off | Use the ffmpeg backend instead of scipy. The scipy backend is used when ffmpeg is not installed |
| `--max-cores N` | `4` | Number of recordings processed in parallel (`1` disables parallel processing) |
| `--gain N` | `1` | Gain in dB applied to the spectrogram (ffmpeg backend only) |
| `--gain-scale` | `log` | Intensity scale of the ffmpeg spectrogram (`log`, `sqrt`, `lin`, and others accepted by ffmpeg) |
| `--highest-freq N` | `20000` | Upper limit of the frequency axis, in Hz |
| `--lowest-freq N` | `0` | Lower limit of the frequency axis, in Hz |
| `--freq-scale` | `lin` | Frequency axis scale, `lin` or `log` (ffmpeg backend only) |
| `--color-choice` | `plasma` | Colour palette (ffmpeg backend only; the scipy backend always uses `plasma`) |
| `--spec-label` | `""` | Suffix added to the output filenames, so that several frequency bands (for example `lf` and `hf`) can be written to the same directory |
| `--img-size WxH` | `1080x720` | Dimensions of the full-size spectrogram, in pixels. The thumbnail is reduced from this image, so this value also affects the detail of the thumbnail |
| `--thumbnail-scale W:H` | `108:72` | Dimensions of the thumbnail, in pixels; also the image size in the calendar |
| `--save-fullsize` | off | Also save the full-size spectrogram next to each thumbnail. Off by default, since the calendar uses only the thumbnails and full-size images occupy considerably more disk space |
| `--clear` | off | Delete existing `*<label>.png` files in the output directory before generating new ones |
| `--include-audio` | off | Add an audio player under each thumbnail, linked to the original recording. The players use `preload="none"`, so a recording is loaded only when it is played |
| `--speed-control` | off | Add a playback speed selector (from 1× to 1/16) above the calendar. Reducing the speed also lowers the pitch, which makes ultrasound audible (see [Listening to Ultrasound](#listening-to-ultrasound)). Requires `--include-audio` |
| `--annotate` | off | Annotation mode: add a checkbox under each thumbnail and a toolbar that exports the selected recordings as a `.txt` list (see [Annotation Mode](#annotation-mode)) |
| `--dates D1 D2 ...` | all dates | Process only the given dates, in `YYYYMMDD` format. Each date must have recordings |
| `--start-date YYYYMMDD` | earliest date | First date of a continuous range. Cannot be combined with `--dates` |
| `--end-date YYYYMMDD` | latest date | Last date of the range (inclusive). Cannot be combined with `--dates` |
| `--time-step N` | none | Keep at most one recording per interval of N minutes on each day |
| `--start-time HHMMSS` | `000000` | Start of the daily time window |
| `--end-time HHMMSS` | `235900` | End of the daily time window |
| `--recursive` | off | Also search the subfolders of the recording directory (see [Subfolders](#subfolders)) |
| `--output-dir DIR` | recording directory | Directory for all generated files; created if it does not exist. When set, the recording directory is only read |
| `--datetime-format FMT` | `%Y%m%d_%H%M%S` | `strptime` format describing how the date and time appear in each filename, after the prefix is removed |
| `--filename-prefix PREFIX` | `""` | Fixed text preceding the date and time in each filename, for example `SM4_` for `SM4_20260304_100000.wav` |

The following example uses the ffmpeg backend with six parallel workers, shows
only frequencies up to 2 kHz, and keeps one recording every 30 minutes
between 05:00 and 09:00:

```bash
spectro-calendar /data/site-1 \
  --use-ffmpeg --max-cores 6 \
  --spec-label lf --highest-freq 2000 \
  --time-step 30 --start-time 050000 --end-time 090000
```

### Filename Formats

`--datetime-format` accepts any
[strptime format](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).
`--filename-prefix` is removed from the filename stem (the name without its
extension) before the format is applied.

| Recorder or convention | Example filename | Options |
|---|---|---|
| AudioMoth (default) | `20260304_100000.WAV` | none |
| Wildlife Acoustics SM4 | `SM4_20260304_100000.wav` | `--filename-prefix SM4_` |
| Date first, with hyphens | `2026-03-04_10-00-00.wav` | `--datetime-format "%Y-%m-%d_%H-%M-%S"` |
| Site identifier | `SITE1-20260304-100000.wav` | `--filename-prefix SITE1- --datetime-format "%Y%m%d-%H%M%S"` |

When a prefix is set, `.wav` files that do not begin with it are skipped and
their number is reported, so that recordings from other devices can remain in
the same directory. A file that begins with the prefix but does not match
`--datetime-format` stops the run with an error naming the file, rather than
being skipped or interpreted incorrectly.

### Listening to Ultrasound

`--speed-control` adds a **Playback speed** selector above the calendar,
with the values 1×, 1/2, 1/4, 1/8, 1/10 and 1/16, which applies to every audio
player:

```bash
spectro-calendar /data/site-1 --include-audio --speed-control
```

The speed is changed in the same way as Audacity's "Change Speed" effect,
not as a tempo change that preserves pitch: the pitch is divided by the same
factor as the speed. This technique, known as time expansion, is the usual
way of listening to ultrasound. A 40 kHz bat call played at 1/10 speed is
heard at 4 kHz, and a one-minute recording lasts ten minutes. The selector
displays this conversion for the chosen speed.

The selector only sets the `playbackRate` and `preservesPitch` properties of
each `<audio>` element in the browser. No audio is decoded or processed by the
page, and the players still load nothing until they are played. The
recordings must have a sample rate high enough to contain the ultrasound (for
example, an AudioMoth recording at 250 or 384 kHz). 1/16 is the lowest speed
that browsers play reliably.

### Annotation Mode

`--annotate` turns the calendar into a simple annotation tool. Each cell
receives a checkbox under its thumbnail, and a toolbar at the top of the page
exports the selected recordings as a plain text file:

```bash
spectro-calendar /data/site-1 --include-audio --annotate
```

The recordings of interest are selected while the calendar is reviewed, and
the button **Export selection (.txt)** downloads the list. No label needs to
be entered, since the exported list itself serves as the annotation. Each
line identifies one selected recording, in the format chosen in the selector
next to the button:

| Format | Example line |
|---|---|
| `filename` (default) | `20260304_100000.WAV` |
| `date & time` | `2026-03-04 10:00:00` |
| `filename + date & time` | `20260304_100000.WAV<TAB>2026-03-04 10:00:00` |

The lines are in chronological order, and the file is named
`annotations_<label>_<YYYYMMDD-HHMMSS>.txt`, where the timestamp is the time
of the export, so that successive exports do not overwrite each other. With
`--recursive`, each filename includes the subfolder it was found in (for
example, `moth-a/20260304_100000.WAV`), since the same name can occur once
per recorder. Calendars generated for different frequency bands
(`--spec-label lf`, `hf`, and so on) export under their own names.

To select several recordings at once, one checkbox is clicked and another is
clicked while holding **Shift**. Every checkbox in the rectangle between the
two is then set to the same state: the times between the two rows, on each
date between the two columns. For example, clicking 01 Mar 05:00 and then
Shift+clicking 03 Mar 07:00 selects 05:00 to 07:00 on 1, 2 and 3 March. All
boxes take the new state of the Shift+clicked box, so the same action over
selected boxes clears the range. Each Shift+click also becomes the starting
corner of the next range.

Selected cells are highlighted, the toolbar shows the number of selected
recordings, and **Clear selection** clears the whole selection after a
confirmation. The selection is also stored in the browser's local storage,
under a key derived from the page's location, so that it is restored when the
calendar is reloaded or reopened later.

Chrome does not provide local storage to pages opened directly from disk
(`file://`). In Chrome, the selection is therefore kept only while the tab is
open, and should be exported before the tab is closed. Firefox provides local
storage to such pages. Serving the calendar over HTTP makes the selection
persistent in every browser; the server must then be started from a directory
that contains both the output directory and the recordings, so that the audio
players can reach the recordings (for example, `python -m http.server` run in
their common parent directory). All other functions, including the export,
work from `file://` in both browsers.

### Remote Recordings over SSH

Recordings stored on a remote machine can be processed by mounting the remote
directory locally with [sshfs](https://github.com/libfuse/sshfs) and passing
the mount point as the recording directory. Since the tool only reads from
the recording directory, a read-only mount is sufficient:

```bash
mkdir -p ~/mnt/site-1
sshfs user@host:/path/on/server ~/mnt/site-1 \
  -o ro,reconnect,cache=yes,kernel_cache \
  -o IdentityFile=$HOME/.ssh/your_key,IdentitiesOnly=yes

spectro-calendar ~/mnt/site-1 \
  --output-dir ~/calendars/site-1 \
  --use-ffmpeg --include-audio
```

**Determining the remote path.** sshfs uses the SFTP subsystem of the SSH
server, whose view of the file system frequently differs from that of a login
shell. NAS devices in particular often present shared folders at the SFTP
root. A path that works with `scp` may therefore fail with sshfs, especially
with OpenSSH clients older than 9.0, in which `scp` uses the remote shell
instead of SFTP. The correct path can be obtained from SFTP directly:

```bash
sftp user@host
sftp> pwd     # the current directory, as seen by SFTP
sftp> ls /    # the contents of the SFTP root
```

On a Synology device, for example, the shell may report
`/volume1/homes/user`, while SFTP presents the shared folder as
`/Recordings/site-1`; sshfs requires the latter. The whole `user@host:path`
argument should be quoted when the remote path contains spaces or accented
characters. The generated page refers to the recordings through the local
mount point, so remote names do not appear in it.

Generating the spectrograms transfers each selected recording over the
connection once. This is the slowest part of the process and cannot be
avoided, since each file must be read completely to compute its spectrogram.
The date and time filters (`--dates` or `--start-date`/`--end-date`,
`--start-time`/`--end-time`, `--time-step`) are the means of reducing the
transfer. All generated files are written locally, to `--output-dir`.

**Playback does not require downloading the recordings.** With
`--include-audio`, each audio player reads its recording through the mount,
and `preload="none"` ensures that only the recordings actually played are
transferred, and only as far as they are played. Opening the calendar itself
transfers nothing. Since WAV is an uncompressed format (one minute of
AudioMoth audio at 48 kHz is approximately 23 MB), playback is comfortable
over a local network or VPN but may stall over a slow connection.

Two further points apply:

- The calendar should be opened directly from disk (`file://`). The relative
  path from the output directory to the mount point leads outside the output
  directory (for example, `../../mnt/site-1/20260304_100000.WAV`), so a web
  server started in the output directory, such as `python -m http.server`,
  cannot serve the audio, although the thumbnails still load.
- If the connection is interrupted, `-o reconnect` restores the mount, but
  reads in progress fail first. Running the command again generates the
  missing spectrograms; with the ffmpeg backend, as in the example above,
  existing spectrograms are kept and not transferred again. The mount is removed
  with `fusermount -u ~/mnt/site-1`.

## How It Works

The complete processing pipeline is implemented in
`src/spectro_calendar/cli.py`. A run consists of the following steps:

1. **Argument parsing.** `argparse` defines the options listed above and
   converts their values to the appropriate types. Before the main parse, a
   preliminary pass extracts `--config`; `load_yaml_config` reads that file,
   rejects unknown keys and installs its values as the parser's defaults with
   `parser.set_defaults(**config)`. Since argparse uses a default only for
   options absent from the command line, any option given on the command
   line takes precedence over both the configuration file and the built-in
   default.

2. **Optional clean-up.** With `--clear`, existing `*<label>.png` files in the
   output directory are deleted, so that spectrograms from an earlier run with
   different parameters do not remain.

3. **File discovery.** Every `.wav` file (regardless of case) in the recording
   directory is listed, including subfolders with `--recursive`. When
   `--filename-prefix` is set, files without that prefix are excluded.
   `parse_recording_datetime` removes the prefix from each filename stem and
   parses the remainder with `datetime.strptime` and `--datetime-format`; a
   filename that does not match stops the run with an error naming the file.
   The files are then sorted by the parsed date and time, not by name, and
   all later steps depend only on these parsed values, not on the filename
   convention.

4. **Date filtering.** Dates given with `--dates` are checked against the dates
   present (`validate_dates` reports any date without recordings). With
   `--start-date`/`--end-date`, `filter_dates_by_range` keeps the dates inside
   the inclusive range; the limits need not have recordings, either limit may
   be omitted, and the run stops if the range contains no recordings. The two
   forms are mutually exclusive; without either, all dates are used.

5. **Time-of-day filtering.** `filter_wav_files_by_time_window` keeps the files
   whose time lies between `--start-time` and `--end-time` on each selected
   date. This window is always applied, with defaults that include the whole
   day.

6. **Time-step reduction.** With `--time-step`,
   `filter_wav_files_by_time_step` processes each day's files in time order
   and keeps the first file at or after the previously kept time plus N
   minutes. This reduces, for example, one recording per minute to one every
   30 minutes, without requiring the recordings to start at exact clock
   times.

7. **Spectrogram generation.** Each remaining file is processed by one of two
   interchangeable backends. `--use-ffmpeg` selects the ffmpeg backend when
   the `ffmpeg` program is found (`shutil.which`); otherwise the scipy backend
   is used. Both write their images to the output directory:
   - **`spectrogram_ffmpeg`** runs ffmpeg's `showspectrumpic` filter, chained
     with a `scale` filter, so that the thumbnail is produced from the
     recording in a single call. With `--save-fullsize`, ffmpeg runs twice:
     once to produce the full-size image and once to reduce it to the
     thumbnail. Recordings whose requested images already exist are skipped.
   - **`spectrogram_scipy`** reads the recording with `scipy.io.wavfile`,
     mixes stereo recordings down to mono, computes a short-time Fourier
     transform (`scipy.signal.stft`, `nperseg=2048`), restricts it to the
     range between `--lowest-freq` and `--highest-freq`, and plots the
     magnitude in decibels with matplotlib (`plasma` colour map, without
     axes). The full-size image, kept in memory unless `--save-fullsize` is
     set, is then reduced to the thumbnail with Pillow. Existing images are
     regenerated.

   A recording that cannot be read, such as a file truncated when a recorder's
   memory card filled up, is reported at the end of the run and receives an
   empty cell, without stopping the run. When `--max-cores` is greater than
   1, the recordings are distributed over a
   `concurrent.futures.ProcessPoolExecutor` of that size. The ffmpeg backend
   benefits because each worker mostly waits for its ffmpeg process, and the
   scipy backend because the computation runs in several processes at once.
   The module docstring of `cli.py` contains measured processing times for
   both backends with 1, 2, 4 and 6 workers.

8. **Calendar generation.** `generate_html` builds a lookup from each
   processed recording's date and time to its file, and writes
   `index_<label>.html` in UTF-8. The page consists of a fixed header
   (`spectro-calendar`), the optional toolbars, a table with one column per
   date (labelled `DD-MM-YYYY`) and one row per time of day, whose header row and first column remain
   visible while scrolling, and a footer linking to
   [biodiversica.xyz](https://biodiversica.xyz/). Each cell shows the
   matching thumbnail, together with an audio player when `--include-audio`
   is set, or is empty when no recording exists for that date and time.

   The players use `preload="none"`. Without it, a browser reads the header
   of every recording when the page opens, only to display its duration; in
   a large calendar (a month at 15-minute intervals has about 3000 cells)
   this delays the page considerably, particularly when the recordings are on
   a network mount. Image and audio addresses are computed by `html_link`
   relative to the output directory, so the output directory and the
   recording directory need not be nested. Each path segment is
   percent-encoded, so names with spaces, accents or symbols such as `#`
   resolve correctly; when no relative path exists (different drives on
   Windows), an absolute `file://` address is used.

   With `--speed-control`, the page includes the speed selector and the
   `SPEED_SCRIPT` handler. With `--annotate`, each cell also includes a
   checkbox that carries the recording's path relative to the recording
   directory and its parsed timestamp, and the page includes the toolbar and
   the `ANNOTATION_SCRIPT` handler. Both scripts are embedded in the page,
   rather than written as separate `.js` files, so that the calendar remains a
   single page that can be moved or shared. They use plain JavaScript without
   libraries. The annotation script builds the exported text from the
   checkbox attributes and offers it as a download, applies Shift+click
   ranges using each checkbox's row and column, and stores the selection in
   `localStorage`. Every storage access is guarded, since Chrome denies
   storage to `file://` pages and the page must keep working in that case.

9. **Stylesheet.** The CSS in `SPECTROGRAM_TABLE_CSS` is written as
   `spectrogram-table.css` next to the calendar page, so that the page
   renders correctly when opened directly from disk.

10. **Timing.** The total processing time is measured and printed at the end
    of the run, using the same method as the backend comparison in the
    module docstring.

## Backends

| | ffmpeg | scipy |
|---|---|---|
| Speed | Faster (see the measurements in `cli.py`) | Slower |
| Requirements | The `ffmpeg` program on the PATH | Python packages only (`scipy`, `matplotlib`, `pillow`) |
| Colour palette | Configurable with `--color-choice` | Always `plasma` |
| Frequency scale | Configurable with `--freq-scale` (`lin` or `log`) | Linear only |

If `--use-ffmpeg` is given but ffmpeg is not found, the scipy backend is used
automatically.

## Development

```bash
uv sync               # installs the project and the development tools
uv run ruff check .   # lint
uv run pytest         # tests
```

The tests generate short synthetic recordings, run the complete tool on them
and inspect the generated files. The ffmpeg backend test is skipped when
ffmpeg is not installed. Continuous integration runs the lint and the tests on
Linux, macOS and Windows, and also runs the installers on all three systems
with the built package.

Project layout:

```
src/spectro_calendar/
├── __init__.py   # package version
├── __main__.py   # enables `python -m spectro_calendar`
├── cli.py        # argument parsing and the complete processing pipeline
└── richhelp.py   # formatted --help output
tests/            # end-to-end tests
scripts/          # installers attached to each release
```

### Making a Release

Set the new version in both `pyproject.toml` and
`src/spectro_calendar/__init__.py`, run `uv lock`, commit the change, and then
create and push a tag:

```bash
git tag v0.2.0 && git push origin v0.2.0
```

The tag triggers `.github/workflows/release.yml`. The tests run on all three
systems, the package is uploaded to PyPI, and a **draft** GitHub release is
created with the installers attached and the notes from
`.github/release-notes.md`. After the highlights have been written, the
release must be published, because the installation commands download from
the latest *published* release. The build fails if the tag does not match the
version in `pyproject.toml`, or if that version differs from the one in
`src/spectro_calendar/__init__.py`.

## License

MIT; see [LICENSE](https://github.com/biodiversica/spectro-calendar/blob/main/LICENSE).
