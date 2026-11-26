# Filename Formats

*English · [Português (Brasil)](../pt-BR/filename-formats.md)*

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
