# How It Works

*English · [Português (Brasil)](../pt-BR/how-it-works.md)*

The complete processing pipeline is implemented in
`src/spectro_calendar/cli.py`. A run consists of the following steps:

1. **Argument parsing.** `argparse` defines the [options](cli.md) and
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
   interchangeable [backends](backends.md). `--use-ffmpeg` selects the ffmpeg
   backend when the `ffmpeg` program is found (`shutil.which`); otherwise the
   scipy backend is used. Both write their images to the output directory:
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
   date (labelled `DD-MM-YYYY`) and one row per time of day, whose header row
   and first column remain visible while scrolling, and a footer linking to
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

   The settings of the run, listed by `settings_summary`, are placed as a
   table in a panel attached to the **?** in the page header. It is shown on
   hover or focus with CSS alone, without a script.

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
