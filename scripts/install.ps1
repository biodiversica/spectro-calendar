# Install spectro-calendar on Windows.
#
#   powershell -ExecutionPolicy ByPass -c "irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | Out-String | iex"
#
# Installs uv if it is missing (uv brings its own Python, so none is needed
# beforehand) and installs spectro-calendar as an isolated tool, with the
# spectro-calendar command on the PATH. Run it again to upgrade.
#
# To uninstall, set SPECTRO_CALENDAR_UNINSTALL and run it in the PowerShell
# window itself:
#
#   $env:SPECTRO_CALENDAR_UNINSTALL=1; irm https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.ps1 | Out-String | iex
#
# Not through powershell -c '...', with the variable in single quotes: those
# quotes can be lost on the way in (it happened on Windows 10), and the window's
# PowerShell then expands the variable to nothing and installs instead.
#
# Either way, it says what it is about to do and asks before doing any of it.
#
# Environment overrides:
#   SPECTRO_CALENDAR_PACKAGE    what to install   (default: spectro-calendar)
#   SPECTRO_CALENDAR_UNINSTALL  1 removes spectro-calendar. Calendars and
#                               spectrograms it made are never removed, nor is uv.
#   SPECTRO_CALENDAR_YES=1      go ahead without asking, e.g. from a script or CI
#
# Keep this file ASCII: Windows PowerShell 5.1 reads a BOM-less script as ANSI.

# All of it in a script block: the uninstall command runs this in the reader's
# own window, and its variables ($ErrorActionPreference above all) and
# functions must not stay behind there.
& {

$ErrorActionPreference = "Stop"

$Package = if ($env:SPECTRO_CALENDAR_PACKAGE) { $env:SPECTRO_CALENDAR_PACKAGE } else { "spectro-calendar" }
$Uninstall = $env:SPECTRO_CALENDAR_UNINSTALL
# Cleared once read, so that the window it was set in does not uninstall the
# next time the installer is run from it.
if (Test-Path Env:SPECTRO_CALENDAR_UNINSTALL) { Remove-Item Env:SPECTRO_CALENDAR_UNINSTALL }
# The version CI tests the installer on.
$Python = "3.12"

function Say($Message) { Write-Host "==> $Message" }

function Find-Uv {
    $Found = Get-Command uv -ErrorAction SilentlyContinue
    if ($Found) { $Found.Source } else { Join-Path $HOME ".local\bin\uv.exe" }
}

# Whether to go ahead: yes under SPECTRO_CALENDAR_YES=1, otherwise whatever is
# answered.
function Confirm-Plan($Doing) {
    if ($env:SPECTRO_CALENDAR_YES -eq "1") { return $true }
    if ([Console]::IsInputRedirected) {
        throw "there is no console to ask in; set SPECTRO_CALENDAR_YES=1 to $Doing without asking."
    }
    $Answer = Read-Host "Continue? [y/N]"
    return ($Answer -match '^\s*(y|yes)\s*$')
}

function Uninstall-SpectroCalendar {
    if ($Uninstall -ne "1") {
        throw "SPECTRO_CALENDAR_UNINSTALL must be 1, not '$Uninstall'"
    }
    Write-Host @"
This uninstalls spectro-calendar. It will:

  - remove spectro-calendar, with uv (uv itself stays)

Calendars and spectrograms it made are not removed.

"@
    if (-not (Confirm-Plan "uninstall")) {
        Write-Host "Nothing was removed."
        return
    }
    # Windows will not delete a program that is running.
    if (Get-Process -Name spectro-calendar -ErrorAction SilentlyContinue) {
        throw "spectro-calendar is running. Wait for it to finish (or press Ctrl+C in its window), then run this again."
    }

    $Uv = Find-Uv
    if ((Test-Path $Uv) -and ((& $Uv tool list | Out-String) -match "(?m)^spectro-calendar ")) {
        Say "Uninstalling spectro-calendar"
        & $Uv tool uninstall spectro-calendar
        if ($LASTEXITCODE -ne 0) { throw "uv tool uninstall failed with exit code $LASTEXITCODE" }
        Say "Done. spectro-calendar is uninstalled."
    } else {
        Say "spectro-calendar is not installed with uv; nothing to remove."
    }
}

function Install-SpectroCalendar {
    $Uv = Find-Uv
    $HaveUv = Test-Path $Uv

    # --- confirmation --------------------------------------------------------
    $UvText = if ($HaveUv) { "use uv, already installed at $Uv" } else { "install uv, the tool that installs spectro-calendar, into $(Join-Path $HOME '.local\bin')" }
    Write-Host @"
This installs spectro-calendar, a command that turns a folder of WAV
recordings into a calendar of spectrograms viewed in the browser. It will:

  - $UvText
  - install $Package with uv, isolated, along with a Python $Python
    of its own; your other Pythons are not touched (if spectro-calendar is
    already installed, it is upgraded)
  - add uv's tools folder to your user PATH

"@
    if (-not (Confirm-Plan "install")) {
        Write-Host "Nothing was installed."
        return
    }

    # --- uv ------------------------------------------------------------------
    if (-not $HaveUv) {
        Say "Installing uv"
        $env:UV_INSTALL_DIR = Join-Path $HOME ".local\bin"
        # A separate process, so an exit in uv's installer cannot end this one.
        powershell -NoProfile -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path $Uv)) { throw "uv could not be installed" }
    }

    # --- spectro-calendar ----------------------------------------------------
    Say "Installing $Package"
    # Native commands do not stop on failure under $ErrorActionPreference, and
    # their stderr must not be redirected: 5.1 would turn uv's progress lines
    # into errors.
    & $Uv tool install --python $Python --upgrade $Package
    if ($LASTEXITCODE -ne 0) { throw "uv tool install failed with exit code $LASTEXITCODE" }
    & $Uv tool update-shell
    $Bin = (& $Uv tool dir --bin | Out-String).Trim()
    $Exe = Join-Path $Bin "spectro-calendar.exe"
    if (-not (Test-Path $Exe)) { throw "spectro-calendar was not installed where uv said it would be ($Exe)" }

    $Version = (& $Exe --version | Out-String).Trim()
    Say "Done. $Version is installed."
    Write-Host ""
    Write-Host "  Open a new terminal and run, for example:"
    Write-Host ""
    Write-Host "    spectro-calendar C:\path\to\recordings --include-audio"
    Write-Host ""
    Write-Host "  then open the index_.html file it writes in a web browser."
    Write-Host "  'spectro-calendar --help' lists every option."
    Write-Host "  To upgrade later, run this installer again."

    if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
        Write-Host ""
        Write-Host "  Optional: ffmpeg was not found. It enables the faster spectrogram"
        Write-Host "  backend (--use-ffmpeg); install it with, e.g., 'winget install --id Gyan.FFmpeg'."
    }
}

# Functions rather than an early return: under iex, a return at the top level
# does not reliably end the script.
if ($Uninstall) { Uninstall-SpectroCalendar } else { Install-SpectroCalendar }

}
