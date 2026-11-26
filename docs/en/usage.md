# Making a Calendar

*English · [Português (Brasil)](../pt-BR/usage.md)*

```bash
spectro-calendar /path/to/recordings
```

The recording directory must contain `.wav` files whose names include the
recording date and time. By default, the tool expects the AudioMoth
convention, `YYYYMMDD_HHMMSS.WAV` (for example, `20260315_063000.WAV`); other
conventions are configured with `--datetime-format` and `--filename-prefix`
(see [Filename Formats](filename-formats.md)). Only the top level of the
directory is searched unless `--recursive` is given (see
[Subfolders](#subfolders)).

## Output Files

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

## A Separate Output Directory

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

## Subfolders

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

## The Settings of a Calendar

Every calendar records the settings it was made with. Hover over the **?** at
the right of the page header (or tab to it, or tap it on a touch screen) to
see them: a table with one parameter per row, named as in a
[configuration file](configuration.md), with the value used, whether it came
from the command line, the configuration file or the default. Above the table
are the spectro-calendar version, the time of the run and the configuration
file used, if any.
