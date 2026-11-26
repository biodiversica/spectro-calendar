# Backends

*English · [Português (Brasil)](../pt-BR/backends.md)*

Spectrograms are drawn by one of two interchangeable backends. scipy is the
default; `--use-ffmpeg` selects ffmpeg.

| | ffmpeg | scipy |
|---|---|---|
| Speed | Faster (see the measurements in `cli.py`) | Slower |
| Requirements | The `ffmpeg` program on the PATH | Python packages only (`scipy`, `matplotlib`, `pillow`) |
| Colour palette | Configurable with `--color-choice` | Always `plasma` |
| Frequency scale | Configurable with `--freq-scale` (`lin` or `log`) | Linear only |

If `--use-ffmpeg` is given but ffmpeg is not found, the scipy backend is used
automatically. [Installation](installation.md) lists how to install ffmpeg,
and [How It Works](how-it-works.md) describes what each backend does.
