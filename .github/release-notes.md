## Install

No Python needed: the installer sets everything up and adds the `spectro-calendar` command. Run it again to upgrade.

**Windows**: open PowerShell and paste:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | Out-String | iex"
```

**macOS and Linux**: open a terminal and paste:

```sh
curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | sh
```

Already using Python? `uv tool install spectro-calendar` or `pip install spectro-calendar`. See the [README](https://github.com/biodiversica/spectro-calendar#installation) ([português](https://github.com/biodiversica/spectro-calendar/blob/main/README.pt-BR.md#instalação)).

[ffmpeg](https://ffmpeg.org/) is optional: when installed, `--use-ffmpeg` selects the faster spectrogram backend. To uninstall, run the installer with `SPECTRO_CALENDAR_UNINSTALL=1` (see [Uninstalling](https://github.com/biodiversica/spectro-calendar#installation)); the calendars it made are kept.

## What's in this release

<!-- Write the highlights here before publishing. -->
