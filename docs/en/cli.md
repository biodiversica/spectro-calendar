# Command-Line Options

*English · [Português (Brasil)](../pt-BR/cli.md)*

`spectro-calendar --help` lists the same options. Every option can also be set
in a [configuration file](configuration.md).

## Example

The following example uses the ffmpeg backend with six parallel workers, shows
only frequencies up to 2 kHz, and keeps one recording every 30 minutes
between 05:00 and 09:00:

```bash
spectro-calendar /data/site-1 \
  --use-ffmpeg --max-cores 6 \
  --spec-label lf --highest-freq 2000 \
  --time-step 30 --start-time 050000 --end-time 090000
```

## Options

| Option | Default | Description |
|---|---|---|
| `recording_dir` | none | Directory containing the `.wav` recordings. Positional; required unless set as `recording_dir` in the configuration file |
| `--config PATH` | none | YAML file providing default option values (see [Configuration File](configuration.md)) |
| `--version` | | Show the installed version and exit |
| `--use-ffmpeg` | off | Use the ffmpeg backend instead of scipy. The scipy backend is used when ffmpeg is not installed (see [Backends](backends.md)) |
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
| `--speed-control` | off | Add a playback speed selector (from 1× to 1/16) above the calendar. Reducing the speed also lowers the pitch, which makes ultrasound audible (see [Listening to Ultrasound](ultrasound.md)). Requires `--include-audio` |
| `--annotate` | off | Annotation mode: add a checkbox under each thumbnail and a toolbar that exports the selected recordings as a `.txt` list (see [Annotation Mode](annotation.md)) |
| `--dates D1 D2 ...` | all dates | Process only the given dates, in `YYYYMMDD` format. Each date must have recordings |
| `--start-date YYYYMMDD` | earliest date | First date of a continuous range. Cannot be combined with `--dates` |
| `--end-date YYYYMMDD` | latest date | Last date of the range (inclusive). Cannot be combined with `--dates` |
| `--time-step N` | none | Keep at most one recording per interval of N minutes on each day |
| `--start-time HHMMSS` | `000000` | Start of the daily time window |
| `--end-time HHMMSS` | `235900` | End of the daily time window |
| `--recursive` | off | Also search the subfolders of the recording directory (see [Subfolders](usage.md#subfolders)) |
| `--output-dir DIR` | recording directory | Directory for all generated files; created if it does not exist. When set, the recording directory is only read |
| `--datetime-format FMT` | `%Y%m%d_%H%M%S` | `strptime` format describing how the date and time appear in each filename, after the prefix is removed (see [Filename Formats](filename-formats.md)) |
| `--filename-prefix PREFIX` | `""` | Fixed text preceding the date and time in each filename, for example `SM4_` for `SM4_20260304_100000.wav` |
