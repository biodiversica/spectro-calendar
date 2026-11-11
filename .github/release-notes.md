## Install

No Python needed: the installer sets everything up and adds the `spectro-calendar` command. Run it again to upgrade.

**Windows**: open PowerShell and paste:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | iex"
```

**macOS and Linux**: open a terminal and paste:

```sh
curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | sh
```

Already using Python? `uv tool install spectro-calendar` or `pip install spectro-calendar`. See the [README](https://github.com/biodiversica/spectro-calendar#installation) ([português](https://github.com/biodiversica/spectro-calendar/blob/main/README.pt-BR.md#instalação)).

[ffmpeg](https://ffmpeg.org/) is optional: when installed, `--use-ffmpeg` selects the faster spectrogram backend.

## What's in this release

<!-- Write the highlights here before publishing. -->
