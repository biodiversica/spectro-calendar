# spectro-calendar

Generate a browsable HTML "calendar" of spectrograms from a folder of `.wav`
recordings, e.g. from an [AudioMoth](https://www.openacousticdevices.info/audiomoth)
or any other passive acoustic recorder that embeds a timestamp in each
filename.

Each recording becomes a spectrogram thumbnail placed in a table, with dates
as columns and times-of-day as rows, so you can quickly scan weeks of
bioacoustic monitoring data at a glance and click through to the full-size
image (and optionally play the audio) for any cell.

This can be considered as an extended adaptation of the [scripts created by Nathan Wolek](https://github.com/nwolek/audiomoth-scripts).

## Requirements

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) (recommended) or plain `pip`, for dependency management
- Optionally, [`ffmpeg`](https://ffmpeg.org/) on your `PATH` for the fast
  spectrogram backend (see [Backends](#backends) below)
- Optionally, [`sshfs`](https://github.com/libfuse/sshfs), if the recordings
  live on a remote machine (see [Remote recordings over SSH](#remote-recordings-over-ssh) below)

## Installation

Clone the repository first:

```bash
git clone https://github.com/biodiversica/spectro-calendar.git
cd spectro-calendar
```

Then pick either workflow — both install the same runtime dependencies
(`numpy`, `scipy`, `matplotlib`, `pillow`, `pyyaml`):

**With `uv`** (creates `.venv` and installs from `pyproject.toml` /
`uv.lock`):

```bash
uv sync
```

**With `pip`** (in a virtual environment of your choice):

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

`requirements.txt` is kept in sync with the dependencies declared in
`pyproject.toml`, for anyone who'd rather not install `uv`. The editable
install (`pip install -e .`) needs `pip>=21.3`; if it complains about
`setup.py`, run `pip install --upgrade pip` first.

## Usage

Run it as a CLI through `uv run`, as an installed console script, or as a
Python module — all are equivalent entry points into the same code,
whichever way you installed it:

```bash
# via uv (no separate "activate" step needed)
uv run spectro-calendar /path/to/recordings

# as a python module (works with either uv or a pip-installed venv)
uv run python -m spectro_calendar /path/to/recordings
python -m spectro_calendar /path/to/recordings  # if using pip's venv, activated

# the console script is also on the venv's PATH either way
.venv/bin/spectro-calendar /path/to/recordings
```

`recording_dir` must contain `.wav` files with a date/time embedded in their
filename. By default the tool expects AudioMoth's convention,
`YYYYMMDD_HHMMSS.WAV` (e.g. `20260315_063000.WAV`), but this is fully
configurable via `--datetime-format` and `--filename-prefix` — see
[Filename formats](#filename-formats) below for recorders that use a
different convention (e.g. Wildlife Acoustics SM4's `SM4_YYYYMMDD_HHMMSS.wav`).

Running the command produces the following, inside `recording_dir` by
default, or entirely inside `--output-dir` if given (in which case
`recording_dir` is only ever read from, never written to):

- `<original-name>-fullsize-<label>.png` — one full-resolution spectrogram per WAV file
- `<original-name>-thumbnail-<label>.png` — the matching downscaled thumbnail
- `index_<label>.html` — the calendar table linking every thumbnail
- `spectrogram-table.css` — the stylesheet used by the HTML table

Open `index_<label>.html` in a browser to view the calendar. Pass
`--output-dir` to keep all generated files (images, HTML, CSS) separate
from the raw recordings, e.g. to publish just that folder:

```bash
uv run spectro-calendar /data/site-1/recordings --output-dir /data/site-1/calendar
```

The HTML still links each thumbnail's optional `<audio>` player back to the
original WAV in `recording_dir` via a relative path, so `--include-audio`
keeps working even though the recordings themselves aren't copied into
`--output-dir`.

### Config file

Instead of (or alongside) command-line flags, options can be set in a YAML
file and passed with `--config`:

```bash
uv run spectro-calendar --config example_config.yaml
```

See [`example_config.yaml`](example_config.yaml) for a full example. Each
YAML key matches a CLI flag with dashes replaced by underscores (e.g.
`--output-dir` → `output_dir`), including `recording_dir` itself, so a run
can be fully described by a config file with no positional argument at all.

**Any flag passed explicitly on the command line overrides the config
file** — the config only supplies defaults for options you don't specify on
the command line:

```bash
# uses every value from example_config.yaml, except max_cores which is
# overridden to 2 regardless of what the file says
uv run spectro-calendar --config example_config.yaml --max-cores 2
```

An unrecognized key in the config file is treated as an error (with the
list of valid keys) rather than silently ignored.

### Options

| Flag | Default | Description |
|---|---|---|
| `recording_dir` | — | Directory containing `.wav` recordings (positional; required unless set via `recording_dir` in `--config`) |
| `--config PATH` | none | YAML file of default option values (see [Config file](#config-file)); explicit CLI flags always override it |
| `--use-ffmpeg` | off | Use the ffmpeg backend instead of scipy (falls back to scipy if ffmpeg isn't installed) |
| `--max-cores N` | `4` | Number of files to process in parallel (`1` disables parallelism) |
| `--gain N` | `1` | Gain in dB applied to the spectrogram (ffmpeg backend only) |
| `--gain-scale` | `log` | ffmpeg gain scaling (`log`, `sqrt`, `lin`, ...) |
| `--highest-freq N` | `20000` | Upper bound of the frequency axis, in Hz |
| `--lowest-freq N` | `0` | Lower bound of the frequency axis, in Hz |
| `--freq-scale` | `lin` | Frequency axis scale, `lin` or `log` (ffmpeg backend only) |
| `--color-choice` | `plasma` | Color palette (ffmpeg backend; scipy backend is hard-coded to `plasma`) |
| `--spec-label` | `""` | Suffix used to distinguish output filenames, e.g. run `lf`/`hf` bands into the same directory without collisions |
| `--img-size WxH` | `1080x720` | Full-size spectrogram image dimensions in pixels |
| `--thumbnail-scale W:H` | `108:72` | Thumbnail dimensions in pixels; also sets the HTML `<img>` cell size |
| `--clear` | off | Delete existing `*<label>.png` files in the output directory before generating new ones |
| `--include-audio` | off | Embed an `<audio>` player under each thumbnail, linking back to the matching WAV in `recording_dir` |
| `--dates D1 D2 ...` | all dates | Restrict processing to specific `YYYYMMDD` dates (validated against dates actually present, using the parsed recording date regardless of filename format) |
| `--start-date YYYYMMDD` | earliest available | First date to include; selects a contiguous range instead of an explicit list. Cannot be combined with `--dates` |
| `--end-date YYYYMMDD` | latest available | Last date to include (inclusive). Cannot be combined with `--dates` |
| `--time-step N` | none | Keep only one recording per N-minute interval per day, instead of every recording |
| `--start-time HHMMSS` | `000000` | Start of the daily time window to include |
| `--end-time HHMMSS` | `235900` | End of the daily time window to include |
| `--output-dir DIR` | `recording_dir` | Directory for all generated output (spectrogram PNGs, `index_<label>.html`, `spectrogram-table.css`); created if it doesn't exist. When set, `recording_dir` is only read from -- nothing is written there. The HTML's `<audio>` player (`--include-audio`) still links back to the original WAV via a relative path |
| `--datetime-format FMT` | `%Y%m%d_%H%M%S` | strptime-compatible format describing how date/time are embedded in each filename, after stripping `--filename-prefix` |
| `--filename-prefix PREFIX` | `""` | Literal prefix to strip from the filename before parsing `--datetime-format`, e.g. `SM4_` for `SM4_20260304_100000.wav` |

Example — fast ffmpeg backend, low-frequency band only, one sample every 30
minutes between 5 AM and 9 AM, 6 parallel workers:

```bash
uv run spectro-calendar /data/site-1 \
  --use-ffmpeg --max-cores 6 \
  --spec-label lf --highest-freq 2000 \
  --time-step 30 --start-time 050000 --end-time 090000
```

### Filename formats

`--datetime-format` takes any [strptime](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
format string; `--filename-prefix` is stripped from the filename stem (the
part before the extension) before that format is applied.

| Recorder / convention | Example filename | Flags |
|---|---|---|
| AudioMoth (default) | `20260304_100000.WAV` | none needed |
| Wildlife Acoustics SM4 | `SM4_20260304_100000.wav` | `--filename-prefix SM4_` |
| Date-first with dashes | `2026-03-04_10-00-00.wav` | `--datetime-format "%Y-%m-%d_%H-%M-%S"` |
| Site-tagged recorder | `SITE1-20260304-100000.wav` | `--filename-prefix SITE1- --datetime-format "%Y%m%d-%H%M%S"` |

If a filename doesn't start with `--filename-prefix`, or the remainder
doesn't match `--datetime-format`, the tool exits with an error naming the
offending file rather than silently skipping or misparsing it.

### Remote recordings over SSH

If the recordings live on a remote machine, mount that directory locally with
[`sshfs`](https://github.com/libfuse/sshfs) and point `recording_dir` at the
mount. Nothing else changes — the tool only ever reads from `recording_dir`,
so a read-only mount is enough:

```bash
sshfs user@host:/data/site-1/recordings ~/mnt/site-1 \
  -o ro,reconnect,cache=yes,kernel_cache

uv run spectro-calendar ~/mnt/site-1 \
  --output-dir ~/calendars/site-1 \
  --use-ffmpeg --include-audio
```

Generating the spectrograms pulls every selected WAV across the link once —
that is the slow part, and there is no way around it, since each file has to
be read in full to compute its spectrogram. The date/time filters
(`--dates` or `--start-date`/`--end-date`, `--start-time`/`--end-time`,
`--time-step`) are the lever for keeping that transfer down. Everything
written out — PNGs, HTML, CSS — lands locally in `--output-dir`.

**Playing the audio does not require downloading it.** With `--include-audio`,
each cell's `<audio>` element streams straight through the mount: the browser
fetches only the recording you actually press play on, and only as far as you
listen. Nothing is copied to local disk beyond the OS page cache. Note that
WAV is uncompressed (an AudioMoth minute at 48 kHz is roughly 23 MB), so
playback is comfortable over a LAN or VPN and can stall on a slow link.

Two things to watch for:

- Open `index_<label>.html` straight from disk (`file://`). The relative path
  from `--output-dir` back to the mount points outside the output directory
  (e.g. `../../mnt/site-1/20260304_100000.WAV`), so serving `--output-dir`
  with something like `python -m http.server` will fail to resolve the audio,
  even though the thumbnails still load — that server refuses to serve paths
  above its root.
- If the connection drops, `-o reconnect` restores the mount, but any
  in-flight read fails first; re-run the command to fill in spectrograms that
  were missed. Unmount with `fusermount -u ~/mnt/site-1`.

## How it works

The whole pipeline lives in `src/spectro_calendar/cli.py`. Running the
command executes these steps, in order:

1. **Argument parsing** — `argparse` builds the CLI surface documented in
   the table above and validates/normalizes user input types (e.g. `Path`
   for the recording directory, `int` for frequencies). Before the real
   parse, a quick first pass extracts `--config` (if given), and
   `load_yaml_config` reads that YAML file (rejecting unknown keys) and
   installs its values as the parser's new defaults via
   `parser.set_defaults(**config)`. Because argparse only falls back to a
   default when a flag isn't present on the command line, any flag the user
   *does* pass on argv wins over both the config file and the built-in
   default. `recording_dir` is required at this point (either as the
   positional argument or via the config's `recording_dir` key).

2. **Optional cleanup** — if `--clear` is passed, any existing
   `*<spec-label>.png` files in the output directory (`--output-dir` if
   given, else `recording_dir`) are deleted first, so stale spectrograms
   from a previous run with different parameters don't linger.

3. **File discovery** — every `.wav` file (case-insensitive) directly inside
   `recording_dir` is listed. `parse_recording_datetime` strips
   `--filename-prefix` from each filename stem and parses the remainder with
   `datetime.strptime(stem, --datetime-format)`, building a
   `{wav_path: datetime}` mapping; any filename that doesn't match exits the
   program with an error identifying it. Files are then sorted chronologically
   by that parsed datetime (not by filename), and `get_available_dates` /
   `get_available_times` derive the distinct `YYYYMMDD`/`HHMMSS` values from
   it for use in later steps — decoupling all downstream date/time logic
   from the original filename convention.

4. **Date filtering** — if `--dates` was given, those values are checked
   against the dates actually present (`validate_dates` raises if any
   requested date has no recordings). If `--start-date`/`--end-date` was
   given instead, `filter_dates_by_range` keeps the discovered dates inside
   that inclusive range — the bounds themselves need not have recordings,
   and either bound may be omitted to leave that end open, but the run
   aborts if the range selects nothing. The two forms are mutually
   exclusive; with neither, all discovered dates are used.

5. **Time-of-day filtering** — `filter_wav_files_by_time_window` keeps only
   files whose time falls within `[--start-time, --end-time]` for each
   selected date (this window is always applied, using its permissive
   00:00:00–23:59:00 defaults when not customized).

6. **Time-step downsampling** — if `--time-step` is set,
   `filter_wav_files_by_time_step` walks each day's remaining files in time
   order and keeps only the first file at/after the previous kept file's
   time plus `N` minutes — turning e.g. one recording per minute into one
   every 30 minutes without needing recordings to fall on exact clock
   boundaries.

7. **Spectrogram generation** — every remaining file is handed to one of two
   interchangeable backends (`--use-ffmpeg` selects the ffmpeg one, provided
   the `ffmpeg` binary is found via `shutil.which`; otherwise scipy is used
   regardless of the flag). Both backends write their output PNGs to the
   output directory (`--output-dir` if given, else `recording_dir`) — the
   source WAV directory itself is never written to when `--output-dir` is set:
   - **`spectrogram_ffmpeg`** shells out twice via `subprocess.run`: once to
     ffmpeg's `showspectrumpic` filter to render the full-size PNG directly
     from the WAV, and once more to scale that PNG down into the thumbnail.
     It skips files whose full-size and thumbnail images already exist.
   - **`spectrogram_scipy`** reads the WAV with `scipy.io.wavfile`, downmixes
     stereo to mono, computes a short-time Fourier transform
     (`scipy.signal.stft`, `nperseg=2048`), masks it to
     `[--lowest-freq, --highest-freq]`, and renders the log-magnitude
     spectrogram with `matplotlib` (`plasma` colormap, axes hidden). The
     saved PNG is then reopened and resized with `Pillow` to produce the
     thumbnail.

   When `--max-cores` is greater than 1, files are distributed across a
   `concurrent.futures.ProcessPoolExecutor` pool of that size instead of
   being processed one at a time; the ffmpeg backend parallelizes well
   because each worker is I/O-bound waiting on a subprocess, while the
   scipy backend benefits from true multi-process CPU parallelism. See the
   benchmark table in `cli.py`'s module docstring for measured throughput
   of both backends at 1/2/4/6 cores.

8. **HTML calendar generation** — `generate_html` builds a
   `{(date, time): wav_path}` lookup from the parsed `file_dates` mapping for
   the *processed* files, then writes `index_<spec-label>.html`: a
   sticky-header/sticky-first-column HTML table with one column per date and
   one row per time-of-day. Each cell either shows the matching thumbnail
   (named after that file's actual stem, whatever its filename convention)
   with an `<audio>` player added when `--include-audio` is set, or is left
   blank if no recording exists for that date/time combination. The
   thumbnail `src` is a plain relative filename within the output directory;
   the `<audio>` `src` is computed with `os.path.relpath` from the output
   directory back to `recording_dir`, so the two directories don't need to
   be nested inside one another.

9. **Stylesheet** — the CSS embedded in `SPECTROGRAM_TABLE_CSS` is written
   out as `spectrogram-table.css` next to the HTML file, in the same
   `--output-dir`/`recording_dir` destination (sticky headers, scroll
   container, alternating week/hour highlighting), so the generated
   `index_<label>.html` renders correctly when opened directly from disk.

10. **Timing** — total wall-clock time for the whole run is measured with
    `time.time()` and printed at the end, matching the methodology used to
    produce the ffmpeg-vs-scipy benchmark table in the module docstring.

## Backends

| | ffmpeg | scipy |
|---|---|---|
| Speed | Faster (see benchmark in `cli.py`) | Slower, pure Python |
| Dependency | Requires the `ffmpeg` binary on `PATH` | Only Python packages (`scipy`, `matplotlib`, `pillow`) |
| Color palette | Configurable via `--color-choice` | Fixed to `plasma` |
| Frequency scale | Configurable via `--freq-scale` (`lin`/`log`) | Linear only |

If `--use-ffmpeg` is passed but ffmpeg isn't found, the tool automatically
falls back to the scipy backend.

## Development

```bash
uv sync --group dev
uv run ruff check .
```

Project layout:

```
src/spectro_calendar/
├── __init__.py   # package version
├── __main__.py   # enables `python -m spectro_calendar`
└── cli.py        # argument parsing + full processing pipeline
```

## License

MIT — see [LICENSE](LICENSE).
