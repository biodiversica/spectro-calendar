#!/bin/sh
# Install spectro-calendar on macOS or Linux.
#
#   curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | sh
#
# Installs uv if it is missing (uv brings its own Python, so none is needed
# beforehand) and installs spectro-calendar as an isolated tool, with the
# spectro-calendar command on the PATH. Run it again to upgrade.
#
# To uninstall, run it with SPECTRO_CALENDAR_UNINSTALL set:
#
#   curl -LsSf https://github.com/biodiversica/spectro-calendar/releases/latest/download/install.sh | SPECTRO_CALENDAR_UNINSTALL=1 sh
#
# Either way, it says what it is about to do and asks before doing any of it.
#
# Environment overrides:
#   SPECTRO_CALENDAR_PACKAGE    what to install   (default: spectro-calendar)
#   SPECTRO_CALENDAR_UNINSTALL  1 removes spectro-calendar. Calendars and
#                               spectrograms it made are never removed, nor is uv.
#   SPECTRO_CALENDAR_YES=1      go ahead without asking, e.g. from a script or CI
set -eu

PACKAGE="${SPECTRO_CALENDAR_PACKAGE:-spectro-calendar}"
UNINSTALL="${SPECTRO_CALENDAR_UNINSTALL:-}"
# The version CI tests the installer on.
PYTHON=3.12

say() { printf '==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

# Ask before going on, unless SPECTRO_CALENDAR_YES=1. $1 is what to say if the
# answer is no, $2 what is being done, for the message when there is no one to
# ask.
confirm() {
  if [ "${SPECTRO_CALENDAR_YES:-}" = 1 ]; then return 0; fi
  # Asked of the terminal: under "curl ... | sh" standard input is the script.
  if ! (: </dev/tty) 2>/dev/null; then
    die "there is no terminal to ask in; set SPECTRO_CALENDAR_YES=1 to $2 without asking."
  fi
  printf 'Continue? [y/N] '
  read -r ANSWER </dev/tty || ANSWER=
  case "$ANSWER" in
    [yY] | [yY][eE][sS]) ;;
    *) echo "$1"; exit 0 ;;
  esac
}

case "$(uname -s)" in
  Darwin | Linux) ;;
  *) die "unsupported system $(uname -s); on Windows use install.ps1." ;;
esac

if command -v uv >/dev/null 2>&1; then
  UV=$(command -v uv)
elif [ -x "$HOME/.local/bin/uv" ]; then
  UV="$HOME/.local/bin/uv"
else
  UV=
fi

# ── uninstall ────────────────────────────────────────────────────────────────
if [ -n "$UNINSTALL" ]; then
  [ "$UNINSTALL" = 1 ] || die "SPECTRO_CALENDAR_UNINSTALL must be 1, not '$UNINSTALL'."
  cat <<EOF
This uninstalls spectro-calendar. It will:

  - remove spectro-calendar, with uv (uv itself stays)

Calendars and spectrograms it made are not removed.

EOF
  confirm "Nothing was removed." uninstall

  if [ -n "$UV" ] && "$UV" tool list 2>/dev/null | grep -q '^spectro-calendar '; then
    say "Uninstalling spectro-calendar"
    "$UV" tool uninstall spectro-calendar
    say "Done. spectro-calendar is uninstalled."
  else
    say "spectro-calendar is not installed with uv; nothing to remove."
  fi
  exit 0
fi

# ── confirmation ─────────────────────────────────────────────────────────────
if [ -n "$UV" ]; then
  UV_TEXT="use uv, already installed at $UV"
else
  UV_TEXT="install uv, the tool that installs spectro-calendar, into ~/.local/bin"
fi
cat <<EOF
This installs spectro-calendar, a command that turns a folder of WAV
recordings into a calendar of spectrograms viewed in the browser. It will:

  - $UV_TEXT
  - install $PACKAGE with uv, isolated, along with a Python $PYTHON
    of its own; your other Pythons are not touched (if spectro-calendar is
    already installed, it is upgraded)
  - add uv's tools folder to your PATH, in your shell's startup file

EOF
confirm "Nothing was installed." install

# ── uv ───────────────────────────────────────────────────────────────────────
if [ -z "$UV" ]; then
  say "Installing uv"
  if command -v curl >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$HOME/.local/bin" sh
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$HOME/.local/bin" sh
  else
    die "neither curl nor wget is available to download uv."
  fi
  UV="$HOME/.local/bin/uv"
fi

# ── spectro-calendar ─────────────────────────────────────────────────────────
say "Installing $PACKAGE"
"$UV" tool install --python "$PYTHON" --upgrade "$PACKAGE"
"$UV" tool update-shell >/dev/null 2>&1 || true
EXE="$("$UV" tool dir --bin)/spectro-calendar"
[ -x "$EXE" ] || die "spectro-calendar was not installed where uv said it would be ($EXE)."

say "Done. $("$EXE" --version 2>/dev/null || echo spectro-calendar) is installed."
cat <<EOF

  Open a new terminal and run, for example:

    spectro-calendar /path/to/recordings --include-audio

  then open the index_.html file it writes in a web browser.
  'spectro-calendar --help' lists every option.
  To upgrade later, run this installer again.
EOF

if ! command -v ffmpeg >/dev/null 2>&1; then
  cat <<EOF

  Optional: ffmpeg was not found. It enables the faster spectrogram backend
  (--use-ffmpeg); install it with your package manager, e.g.
  'brew install ffmpeg' or 'sudo apt install ffmpeg'.
EOF
fi
