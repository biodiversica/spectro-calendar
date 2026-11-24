"""End-to-end tests: generate short WAV files, run the tool, inspect the output.

Most tests call ``main()`` in-process with ``--max-cores 1`` so they stay fast
and debuggable. One test runs the real console entry point in a subprocess
with several workers, which on Windows and macOS exercises the "spawn"
process start method used by the parallel pool.
"""

import html
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

import numpy as np
import pytest
import scipy.io.wavfile as wavfile

from spectro_calendar import __version__, cli

SAMPLE_RATE = 8000


def write_wav(path, seconds=0.5, sample_rate=SAMPLE_RATE):
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(0)
    data = (rng.standard_normal(int(seconds * sample_rate)) * 3000).astype(np.int16)
    wavfile.write(path, sample_rate, data)
    return path


def run_cli(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["spectro-calendar", *map(str, argv), "--max-cores", "1"])
    cli.main()


def read_html(out_dir, label=""):
    return (out_dir / f"index_{label}.html").read_text(encoding="utf-8")


def links(page, tag):
    """The decoded src of every <img> or <audio><source> in the page."""
    pattern = r'<img src="([^"]+)"' if tag == "img" else r'<source src="([^"]+)"'
    return [urllib.parse.unquote(src) for src in re.findall(pattern, page)]


@pytest.fixture
def recordings(tmp_path):
    rec = tmp_path / "recordings"
    for name in ("20260301_050000", "20260301_060000", "20260302_050000"):
        write_wav(rec / f"{name}.WAV")
    return rec


def test_version(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["spectro-calendar", "--version"])
    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    assert exit_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"spectro-calendar {__version__}"


def test_help(monkeypatch, capsys):
    # -h must be printed by Rich itself, not pre-rendered to an ANSI string and
    # written out: the classic Windows console would show that string's escape
    # codes as "←[1m" text instead of colours.
    rendered_strings = []
    original = cli.RichHelpParser.format_help
    monkeypatch.setattr(
        cli.RichHelpParser,
        "format_help",
        lambda self: rendered_strings.append(1) or original(self),
    )
    monkeypatch.setattr(sys, "argv", ["spectro-calendar", "-h"])
    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    assert exit_info.value.code == 0
    out = capsys.readouterr().out
    assert "Usage:" in out and "--output-dir" in out
    assert not rendered_strings


def test_basic_calendar(monkeypatch, recordings):
    run_cli(monkeypatch, recordings)

    thumbs = sorted(p.name for p in recordings.glob("*-thumbnail-.png"))
    assert thumbs == [
        "20260301_050000-thumbnail-.png",
        "20260301_060000-thumbnail-.png",
        "20260302_050000-thumbnail-.png",
    ]
    assert not list(recordings.glob("*-fullsize-*.png"))
    assert (recordings / "spectrogram-table.css").is_file()

    page = read_html(recordings)
    assert '<meta charset="utf-8">' in page
    assert "<th>01-03-2026</th>" in page and "<th>02-03-2026</th>" in page
    assert len(links(page, "img")) == 3
    # 2 dates x 2 times, one of them without a recording
    assert page.count("<td>&nbsp;</td>") == 1
    assert '<header class="page-header">|=|=| spectro-calendar<div class="settings">' in page
    assert 'href="https://biodiversica.xyz/"' in page
    # Optional parts stay out unless asked for
    for absent in ("<audio", "speed-select", "annotate-bar", "<script"):
        assert absent not in page


def test_optional_page_features(monkeypatch, recordings, tmp_path):
    out = tmp_path / "calendar"
    run_cli(
        monkeypatch, recordings, "--output-dir", out, "--spec-label", "lf",
        "--include-audio", "--speed-control", "--annotate", "--save-fullsize",
    )
    page = read_html(out, "lf")
    assert page.count('<audio controls preload="none">') == 3
    assert 'id="speed-select"' in page and "preservesPitch" in page
    assert 'class="annotate-bar"' in page and page.count('class="annotate-check"') == 3
    # The Shift+click hint sits inside the "Annotation" title, shown on hover
    assert re.search(r'<span class="annotate-title"[^>]*>Annotation<span class="annotate-hint"', page)
    assert len(list(out.glob("*-fullsize-lf.png"))) == 3
    # Nothing is written next to the recordings when --output-dir is set
    assert sorted(p.suffix for p in recordings.iterdir()) == [".WAV"] * 3


def test_speed_control_needs_audio(monkeypatch, recordings, capsys):
    run_cli(monkeypatch, recordings, "--speed-control")
    assert "speed-select" not in read_html(recordings)
    assert "--speed-control has no effect without --include-audio" in capsys.readouterr().out


def test_links_resolve_with_awkward_names(monkeypatch, tmp_path):
    # Spaces, accents and '#' in both the recording and the output folders
    rec = tmp_path / "gravações #1" / "sítio A"
    write_wav(rec / "20260301_050000.WAV")
    out = tmp_path / "saída 100%"
    run_cli(monkeypatch, rec, "--output-dir", out, "--include-audio")

    page = read_html(out)
    (img,) = links(page, "img")
    (audio,) = links(page, "audio")
    assert (out / img).resolve() == (out / "20260301_050000-thumbnail-.png").resolve()
    assert (out / audio).resolve() == (rec / "20260301_050000.WAV").resolve()


def test_link_to_another_drive_is_absolute(monkeypatch, tmp_path):
    # Windows cannot write a relative path between drives; relpath raises.
    def no_relpath(*_):
        raise ValueError("path is on mount 'D:', start on mount 'C:'")

    monkeypatch.setattr(cli.os.path, "relpath", no_relpath)
    target = tmp_path / "rec #1" / "a.WAV"
    assert cli.html_link(target, tmp_path / "out") == target.resolve().as_uri()


def test_recursive_mirrors_subfolders(monkeypatch, tmp_path):
    rec = tmp_path / "recordings"
    write_wav(rec / "moth-a" / "20260301_050000.WAV")
    write_wav(rec / "moth-b" / "20260302_050000.WAV")
    out = tmp_path / "calendar"

    # Without --recursive, subfolders are not searched
    monkeypatch.setattr(sys, "argv", ["spectro-calendar", str(rec), "--max-cores", "1"])
    with pytest.raises(SystemExit):
        cli.main()

    run_cli(monkeypatch, rec, "--recursive", "--output-dir", out)
    assert (out / "moth-a" / "20260301_050000-thumbnail-.png").is_file()
    assert (out / "moth-b" / "20260302_050000-thumbnail-.png").is_file()


def test_prefix_and_datetime_format(monkeypatch, tmp_path):
    rec = tmp_path / "recordings"
    write_wav(rec / "SITE1-20260301-050000.wav")
    write_wav(rec / "OTHER-20260301-060000.wav")
    run_cli(
        monkeypatch, rec, "--filename-prefix", "SITE1-", "--datetime-format", "%Y%m%d-%H%M%S",
    )
    assert [Path(p).name for p in links(read_html(rec), "img")] == ["SITE1-20260301-050000-thumbnail-.png"]


def test_time_window_and_step(monkeypatch, tmp_path):
    rec = tmp_path / "recordings"
    for minute in range(0, 60, 10):
        write_wav(rec / f"20260301_05{minute:02d}00.WAV")
    write_wav(rec / "20260301_070000.WAV")
    run_cli(
        monkeypatch, rec, "--start-time", "050000", "--end-time", "060000", "--time-step", "20",
    )
    names = [Path(p).name[:15] for p in links(read_html(rec), "img")]
    assert names == ["20260301_050000", "20260301_052000", "20260301_054000"]


def test_config_file_with_cli_override(monkeypatch, recordings, tmp_path):
    out_config = tmp_path / "from-config"
    out_cli = tmp_path / "from-cli"
    config = tmp_path / "config.yaml"
    config.write_text(
        f"recording_dir: {recordings.as_posix()!r}\n"
        f"output_dir: {out_config.as_posix()!r}\n"
        "spec_label: cfg\n"
        "include_audio: true\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys, "argv",
        ["spectro-calendar", "--config", str(config), "--output-dir", str(out_cli), "--max-cores", "1"],
    )
    cli.main()
    assert not out_config.exists()
    assert "<audio" in read_html(out_cli, "cfg")


def test_settings_panel_lists_every_option(monkeypatch, recordings, tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("gain: 3\ndates: ['20260301']\n", encoding="utf-8")
    run_cli(monkeypatch, recordings, "--config", config, "--include-audio")
    page = read_html(recordings)
    assert 'class="settings-toggle"' in page
    panel = re.search(r'<div class="settings-panel".*?</table>', page, re.S).group(0)
    assert f"spectro-calendar {__version__}, run on" in panel
    assert html.escape(f"Config file: {config.resolve()}") in panel
    rows = dict(
        (html.unescape(key), html.unescape(value))
        for key, value in re.findall(
            r'<tr><td class="settings-key">(.*?)</td><td class="settings-value[^"]*">(.*?)</td></tr>', panel
        )
    )
    # One row per option, from the config file, the command line and the
    # defaults alike; the paths resolved, and unset options marked as such
    assert rows["gain"] == "3"
    assert rows["dates"] == "20260301"
    assert rows["include_audio"] == "true"
    assert rows["max_cores"] == "1"
    assert rows["start_time"] == "000000"
    assert rows["time_step"] == "not set"
    assert rows["recording_dir"] == str(recordings.resolve())
    assert rows["output_dir"] == str(recordings.resolve())


def test_date_without_recordings_is_an_error(monkeypatch, recordings, capsys):
    monkeypatch.setattr(sys, "argv", ["spectro-calendar", str(recordings), "--dates", "20991231"])
    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    assert exit_info.value.code != 0
    assert "20991231" in capsys.readouterr().err


def test_unknown_config_key_is_an_error(monkeypatch, recordings, tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("include_audoi: true\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["spectro-calendar", str(recordings), "--config", str(config)])
    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    assert exit_info.value.code != 0


def test_unreadable_wav_is_skipped(monkeypatch, recordings, capsys):
    (recordings / "20260302_060000.WAV").write_bytes(b"RIFF\x00\x00not a wav file")
    run_cli(monkeypatch, recordings)
    assert len(links(read_html(recordings), "img")) == 3
    assert "could not be read" in capsys.readouterr().out


def test_help_does_not_load_the_scientific_stack():
    # numpy, scipy, matplotlib, Pillow and PyYAML take seconds to import, so
    # -h must not touch them. A fresh interpreter, since this one has them.
    heavy = ("numpy", "scipy", "matplotlib", "PIL", "yaml")
    code = (
        "import sys\n"
        "sys.argv = ['spectro-calendar', '-h']\n"
        "from spectro_calendar import cli\n"
        "try:\n"
        "    cli.main()\n"
        "except SystemExit:\n"
        "    pass\n"
        f"print('LOADED', [m for m in {heavy!r} if m in sys.modules])\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "LOADED []" in result.stdout, result.stdout[-500:]


def test_spectrograms_do_not_use_pyplot_or_tk(recordings):
    # pyplot picks an interactive backend (TkAgg on Windows) and sets up
    # Tcl/Tk for every image, which can fail on its own and leave recordings
    # out of the calendar. A fresh interpreter, since tests may load pyplot.
    code = (
        "import sys\n"
        f"sys.argv = ['spectro-calendar', {str(recordings)!r}, '--max-cores', '1']\n"
        "from spectro_calendar import cli\n"
        "cli.main()\n"
        "print('LOADED', [m for m in ('matplotlib.pyplot', 'tkinter') if m in sys.modules])\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "LOADED []" in result.stdout, result.stdout[-500:]
    assert len(list(recordings.glob("*-thumbnail-.png"))) == 3


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg is not installed")
def test_ffmpeg_backend(monkeypatch, recordings):
    run_cli(monkeypatch, recordings, "--use-ffmpeg", "--save-fullsize")
    assert len(list(recordings.glob("*-thumbnail-.png"))) == 3
    assert len(list(recordings.glob("*-fullsize-.png"))) == 3
    # A second run finds the images and leaves them alone
    run_cli(monkeypatch, recordings, "--use-ffmpeg", "--save-fullsize")


def test_parallel_run_through_the_module(recordings):
    result = subprocess.run(
        [sys.executable, "-m", "spectro_calendar", str(recordings), "--max-cores", "2"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert len(list(recordings.glob("*-thumbnail-.png"))) == 3
