#!/usr/bin/env python3
"""
spectro_calendar.cli
=====================

Command-line implementation of the spectrogram calendar generator.

Pipeline overview (see ``main()`` for the orchestration):

1. **Argument parsing** -- ``argparse`` defines all tunable spectrogram and
   filtering parameters (frequency range, gain, image sizes, date/time
   filters, backend choice, parallelism). ``--config`` optionally points to
   a YAML file (see ``example_config.yaml``) whose keys become argparse
   defaults via ``parser.set_defaults``; explicit CLI flags still win over
   both the config file and the built-in defaults.
2. **File discovery** -- all ``.wav`` files directly inside ``recording_dir``
   are listed (``--recursive`` also descends into its subfolders)
   and their embedded recording date/time is parsed from each filename via
   ``parse_recording_datetime``, using ``--datetime-format`` (a strptime
   format string, default ``"%Y%m%d_%H%M%S"`` -- AudioMoth's convention) and
   an optional ``--filename-prefix`` stripped beforehand (e.g. ``"SM4_"`` for
   SM4 recorders' ``SM4_YYYYMMDD_HHMMSS.wav``). This makes the tool
   recorder-agnostic rather than tied to one filename convention.
3. **Filtering** -- the discovered files are narrowed down by:
   - explicit ``--dates`` (validated against dates actually present),
   - a daily ``--start-time``/``--end-time`` window,
   - an optional ``--time-step`` that keeps only the first recording at/after
     each N-minute interval per day.
4. **Spectrogram generation** -- for every remaining file, a full-size PNG
   and a downscaled thumbnail PNG are generated into the output directory
   (``--output-dir`` if given, else ``recording_dir``); with ``--recursive``
   each file's PNGs go into a subdirectory mirroring its location under
   ``recording_dir`` (see ``spectrogram_output_dir``), so same-named files in
   different subfolders don't overwrite each other. Generation uses one of two
   interchangeable backends:
   - ``spectrogram_ffmpeg`` -- shells out to ffmpeg's ``showspectrumpic``
     filter (fast, see benchmark below, but requires the ffmpeg binary).
   - ``spectrogram_scipy`` -- pure-Python STFT via ``scipy.signal.stft`` +
     ``matplotlib`` rendering (no external dependency, slower).
   Both backends can run in parallel across files using
   ``concurrent.futures.ProcessPoolExecutor`` (``--max-cores``). When
   ``--output-dir`` is set, ``recording_dir`` is only ever read from.
5. **HTML calendar table** -- ``generate_html`` lays out every generated
   thumbnail in a scrollable HTML table (dates as columns, times of day as
   rows), optionally embedding an ``<audio>`` player per cell that links
   back to the source WAV in ``recording_dir`` (``--include-audio``). A
   companion CSS file is written alongside it, both into the output
   directory.

Parallel processing computation time (Lenovo ThinkPad X1 Carbon 7th generation)
- 107 wav files of 1min (23MB each)
---------------------------------------
type   |  n_cores	|  exec_time[s]
---------------------------------------
ffmpeg |  1	        | 143.76001620292664
ffmpeg |  2	        | 92.58392882347107
ffmpeg |  4	        | 64.96807098388672
ffmpeg |  6	        | 58.00045132637024
scipy  |  1	        | 195.77234363555908
scipy  |  2	        | 128.88741254806519
scipy  |  4	        | 91.91525173187256
scipy  |  6	        | 90.41856098175049
---------------------------------------

"""

import argparse
import subprocess
import shutil
import sys
from pathlib import Path
import numpy as np
import scipy.io.wavfile as wav
import scipy.signal as signal
import matplotlib.pyplot as plt
import concurrent.futures
import os
from PIL import Image
import time
from datetime import datetime
import yaml


# ------------------------
# CSS for the HTML Table (self-contained)
# ------------------------

SPECTROGRAM_TABLE_CSS = """\
html {
  box-sizing: border-box;
  height: 100%;
}
body {
  height: 100%;
  margin: 0;
  display: flex;
  flex-direction: column;
}
*,
*:before,
*:after {
  box-sizing: inherit;
}
* {
  font-family: 'Consolas', 'Courier New', monospace;
}
.intro {
  max-width: 1280px;
  margin: 1em auto;
}
.table-scroll {
  position: relative;
  width:100%;
  z-index: 1;
  margin: 0 auto;
  overflow: auto;
  /* Fill whatever vertical space is left in the body's flex column, rather
     than a fixed height, so the calendar uses the full window on any screen.
     min-height:0 lets the flex item shrink below its content height, which is
     what keeps the scrolling inside the table instead of on the page. */
  flex: 1 1 auto;
  min-height: 0;
}
.table-scroll table {
  width: 100%;
  min-width: 1280px;
  margin: auto;
  border-collapse: separate;
  border-spacing: 0;
}
.table-wrap {
  position: relative;
}
.table-scroll th,
.table-scroll td {
  padding: 5px 10px;
  border: 1px solid #000;
  background: #fff;
  vertical-align: top;
  text-align: center;
}
.table-scroll td.start-of-week {
  background: #ffc2df;
}
.table-scroll th.start-of-hour {
  background: #c2dfff;
}
.table-scroll thead th {
  background: #333;
  color: #fff;
  position: -webkit-sticky;
  position: sticky;
  top: 0;
}
.table-scroll tfoot,
.table-scroll tfoot th,
.table-scroll tfoot td {
  position: -webkit-sticky;
  position: sticky;
  bottom: 0;
  background: #666;
  color: #fff;
  z-index:4;
}
a:focus {
  background: red;
}
th:first-child {
  position: -webkit-sticky;
  position: sticky;
  left: 0;
  z-index: 2;
  background: #ccc;
}
thead th:first-child,
tfoot th:first-child {
  z-index: 5;
}
"""

# ------------------------
# Utility functions
# ------------------------


def parse_time_string(time_str):
    """
    Parses a time string in HHMMSS format into a datetime object.
    """
    return datetime.strptime(time_str, "%H%M%S")

def parse_recording_datetime(wav_path, datetime_format, filename_prefix=""):
    """
    Parses the recording date/time embedded in a WAV filename.

    This decouples the tool from any single recorder's naming convention:
    ``datetime_format`` is a strptime-compatible format string describing
    where/how the date and time appear (default: AudioMoth's
    "%Y%m%d_%H%M%S", e.g. "20260304_100000.WAV"), and ``filename_prefix`` is
    an optional literal prefix stripped before parsing (e.g. "SM4_" for
    "SM4_20260304_100000.wav").

    Args:
        wav_path (Path): Path to the .wav file
        datetime_format (str): strptime format string for the date/time portion
        filename_prefix (str): Literal prefix to strip before parsing (default: "")

    Returns:
        datetime: The parsed recording date and time

    Raises:
        ValueError: If the filename doesn't start with the expected prefix,
            or the remainder doesn't match datetime_format
    """
    stem = wav_path.stem
    if filename_prefix:
        if not stem.startswith(filename_prefix):
            raise ValueError(
                f"Filename '{wav_path.name}' does not start with expected prefix '{filename_prefix}'"
            )
        stem = stem[len(filename_prefix):]
    try:
        return datetime.strptime(stem, datetime_format)
    except ValueError as e:
        raise ValueError(
            f"Filename '{wav_path.name}' does not match datetime format "
            f"'{datetime_format}' (after stripping prefix '{filename_prefix}'): {e}"
        ) from e

def get_available_dates(file_dates):
    """
    Extracts the distinct recording dates (YYYYMMDD) from a {wav_path: datetime} mapping.
    """
    return sorted({dt.strftime("%Y%m%d") for dt in file_dates.values()})

def get_available_times(file_dates):
    """
    Extracts the distinct recording times (HHMMSS) from a {wav_path: datetime} mapping.
    """
    return sorted({dt.strftime("%H%M%S") for dt in file_dates.values()})

def filter_wav_files_by_time_step(wav_files, file_dates, dates_to_process, time_step_minutes):
    """
    Filters WAV files to include only those that are at the specified time intervals.
    The time step is in minutes (e.g., 40 minutes).
    """
    filtered_files = []
    for date in dates_to_process:
        date_files = [w for w in wav_files if file_dates[w].strftime("%Y%m%d") == date]
        date_files.sort(key=lambda w: file_dates[w])  # Sort by datetime

        if not date_files:
            print(f'Skipping {date} since there are no files from chosen start-time on...')
            continue
        # Start with the first file (earliest time)
        filtered_files.append(date_files[0])

        # Now select files that match the time step
        last_selected_dt = file_dates[date_files[0]]
        for wav in date_files[1:]:
            current_dt = file_dates[wav]
            time_diff = (current_dt - last_selected_dt).total_seconds() / 60  # in minutes

            # If the time difference is greater than or equal to the time step, select this file
            if time_diff >= time_step_minutes:
                filtered_files.append(wav)
                last_selected_dt = current_dt

    return filtered_files

def filter_wav_files_by_time_window(wav_files, file_dates, start_time, end_time, dates_to_process):
    """
    Filters WAV files to include only those that fall within the specified time window each day.

    Args:
        start_time (time): Start of the daily window (time-of-day only)
        end_time (time): End of the daily window (time-of-day only)
    """
    filtered_files = []
    for date in dates_to_process:
        date_files = [w for w in wav_files if file_dates[w].strftime("%Y%m%d") == date]
        date_files.sort(key=lambda w: file_dates[w])  # Sort by datetime

        for wav in date_files:
            current_time = file_dates[wav].time()

            # Check if the current file's time is within the start and end time window
            if start_time <= current_time <= end_time:
                filtered_files.append(wav)

    return filtered_files

def round_time_step(time_step, available_times):
    """
    Rounds the given time step to the closest available time step.
    """
    closest_step = min(available_times, key=lambda x: abs(int(x[:2])*60 + int(x[2:4]) - time_step))
    return closest_step

def validate_dates(dates, available_dates):
    """
    Validates if the provided dates exist in the available dates.
    """
    invalid_dates = [date for date in dates if date not in available_dates]
    if invalid_dates:
        raise ValueError(f"Invalid dates provided: {', '.join(invalid_dates)}")

def parse_date_string(date_str, label):
    """
    Parses a YYYYMMDD date string into a date object.

    Args:
        date_str: The value to parse; coerced to str first, so an unquoted
            YAML number such as 20260301 is accepted as well as "20260301"
        label (str): Name of the option being parsed, used in error messages

    Returns:
        date: The parsed date

    Raises:
        ValueError: If the value isn't a valid YYYYMMDD date
    """
    try:
        return datetime.strptime(str(date_str), "%Y%m%d").date()
    except ValueError as e:
        raise ValueError(f"{label} must be a date in YYYYMMDD format, got '{date_str}': {e}") from e

def filter_dates_by_range(available_dates, start_date, end_date):
    """
    Selects the available dates falling inside an inclusive date range.

    Either bound may be None, leaving that end of the range open. Unlike
    validate_dates, the bounds themselves need not have recordings -- only
    the dates in between that do are returned.

    Args:
        available_dates (list of str): Dates present in the recordings (YYYYMMDD)
        start_date (str or None): First date to include (YYYYMMDD)
        end_date (str or None): Last date to include (YYYYMMDD)

    Returns:
        list of str: The subset of available_dates within the range, sorted

    Raises:
        ValueError: If a bound isn't a valid YYYYMMDD date, or start is after end
    """
    start = parse_date_string(start_date, "start_date") if start_date else None
    end = parse_date_string(end_date, "end_date") if end_date else None

    if start and end and start > end:
        raise ValueError(f"start_date '{start_date}' is after end_date '{end_date}'")

    selected = []
    for date in available_dates:
        current = parse_date_string(date, "recording date")
        if start and current < start:
            continue
        if end and current > end:
            continue
        selected.append(date)

    return selected

def load_yaml_config(config_path, valid_keys):
    """
    Loads a YAML config file mapping CLI argument names (dest, e.g.
    "output_dir", "use_ffmpeg") to values, to be used as argparse defaults.

    Args:
        config_path (Path): Path to the YAML config file
        valid_keys (set): Set of recognized argparse dest names

    Returns:
        dict: Parsed config, ready to pass to argparse.ArgumentParser.set_defaults

    Raises:
        ValueError: If the file can't be parsed, isn't a mapping, or
            contains keys that don't match any CLI argument
    """
    with config_path.open() as f:
        config = yaml.safe_load(f)

    if config is None:
        return {}
    if not isinstance(config, dict):
        raise ValueError(f"Config file '{config_path}' must contain a YAML mapping of option: value")

    unknown_keys = sorted(set(config) - valid_keys)
    if unknown_keys:
        raise ValueError(
            f"Config file '{config_path}' has unknown option(s): {', '.join(unknown_keys)}. "
            f"Valid options are: {', '.join(sorted(valid_keys))}"
        )

    return config

def ffmpeg_available():
    """
    Checks if ffmpeg is installed on the system.

    Returns:
        bool: True if ffmpeg is available, False otherwise
    """
    return shutil.which("ffmpeg") is not None


def run(cmd):
    """
    Executes a shell command with error handling.

    stdin is detached: ffmpeg grabs the terminal into raw, no-echo mode to
    listen for its interactive keys, and parallel workers race each other
    restoring it, which can leave the shell with echo turned off.

    Args:
        cmd (list): List of command-line arguments for subprocess
    """
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL)

# ------------------------
# Spectrogram generation using scipy
# ------------------------

def spectrogram_output_dir(wav_path, rec_dir, out_dir):
    """
    Resolves where a WAV file's spectrogram PNGs belong.

    With ``--recursive``, recordings may live in subfolders of
    ``recording_dir``; mirroring that structure under the output directory
    keeps same-named files from different subfolders (a common case when one
    folder holds one recorder/deployment) from overwriting each other's PNGs.

    Args:
        wav_path (Path): Path to the .wav file
        rec_dir (Path): Directory the recordings were discovered under
        out_dir (Path): Root output directory

    Returns:
        Path: ``out_dir`` itself for a file sitting directly in ``rec_dir``,
        otherwise the matching subdirectory under ``out_dir``.
    """
    try:
        rel_parent = wav_path.parent.relative_to(rec_dir)
    except ValueError:
        # Not under rec_dir (shouldn't happen); fall back to the root.
        return out_dir
    return out_dir / rel_parent


def spectrogram_scipy(
    wav_path,
    highest_freq,
    lowest_freq,
    spec_label,
    img_size,
    thumbnail_scale,
    out_dir,
):
    """
    Generates spectrogram images using scipy.

    Args:
        wav_path (Path): Path to the .wav file
        highest_freq (int): Highest frequency for spectrogram (Hz)
        lowest_freq (int): Lowest frequency for spectrogram (Hz)
        spec_label (str): Frequency range identifier ("lf" or other)
        img_size (str): Image size for spectrogram (width x height, e.g. "1920x240")
        thumbnail_scale (str): Thumbnail image dimensions (e.g., "192:24")
        out_dir (Path): Directory the full-size/thumbnail PNGs are written to
    """

    # Read the audio file using scipy
    sample_rate, audio_data = wav.read(wav_path)

    # Check if audio is stereo, and convert to mono by averaging channels if necessary
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)

    # Perform Short-Time Fourier Transform (STFT)
    f, t, Zxx = signal.stft(audio_data, fs=sample_rate, nperseg=2048)

    # Get the magnitude spectrogram (absolute value of Zxx)
    spectrogram = np.abs(Zxx)

    # Limit the frequency range to the specified lowest and highest frequencies
    freq_mask = (f >= lowest_freq) & (f <= highest_freq)
    spectrogram = spectrogram[freq_mask, :]

    # Convert image size to float (in inches for matplotlib)
    fig_w, fig_h = [int(x) / 100 for x in img_size.split("x")]
    plt.figure(figsize=(fig_w, fig_h))

    # Display the spectrogram
    plt.pcolormesh(t, f[freq_mask], 10 * np.log10(spectrogram), shading='auto', cmap='plasma')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [s]')
    plt.axis("off")

    # Save the full-size spectrogram image
    base = wav_path.stem
    full_img = out_dir / f"{base}-fullsize-{spec_label}.png"
    thumb_img = out_dir / f"{base}-thumbnail-{spec_label}.png"
    plt.savefig(full_img, bbox_inches="tight", pad_inches=0)
    plt.close()

    # Generate thumbnail by resizing the full-size spectrogram image
    tw, th = [int(x) for x in thumbnail_scale.split(":")]
    img = Image.open(full_img)
    img = img.resize((tw, th))
    img.save(thumb_img)

    print(f"Spectrogram for {wav_path.name} generated.")



# ------------------------
# Spectrogram generation using ffmpeg
# ------------------------

def spectrogram_ffmpeg(
    wav_path,
    gain,
    highest_freq,
    lowest_freq,
    gain_scale,
    freq_scale,
    color_choice,
    spec_label,
    img_size,
    thumbnail_scale,
    out_dir,
):
    """
    Generates spectrogram images (full-size and thumbnail) using ffmpeg.

    Args:
        wav_path (Path): Path to the .wav file
        gain (int): Gain in dB for spectrogram image
        highest_freq (int): Highest frequency for spectrogram (Hz)
        lowest_freq (int): Lowest frequency for spectrogram (Hz)
        gain_scale (str): Scaling method for spectrogram ("log", "sqrt", etc.)
        freq_scale (str): Frequency scale ("lin", "log")
        color_choice (str): Color palette for spectrogram visualization
        spec_label (str): Frequency range identifier ("lf" or other)
        img_size (str): Image size for spectrogram (width x height, e.g. "1920x240")
        thumbnail_scale (str): Thumbnail image dimensions (e.g., "192:24")
        out_dir (Path): Directory the full-size/thumbnail PNGs are written to
    """
    base = wav_path.stem
    full_img = out_dir / f"{base}-fullsize-{spec_label}.png"
    thumb_img = out_dir / f"{base}-thumbnail-{spec_label}.png"

    # Skip if spectrogram already exists
    if full_img.exists() and thumb_img.exists():
        print(f"Spectrogram for {wav_path.name} already exists. Skipping...")
        return

    print(f"making fullsize spectrogram for {wav_path.name}...")

    # Run ffmpeg to generate the full-size spectrogram
    run([
        "ffmpeg",
        "-i", str(wav_path),
        "-lavfi",
        (
            f"showspectrumpic="
            f"s={img_size}:"
            f"stop={highest_freq}:"
            f"start={lowest_freq}:"
            f"scale={gain_scale}:"
            f"fscale={freq_scale}:"
            f"color={color_choice}:"
            f"gain={gain}:"
            f"legend=disable"
        ),
        "-v", "quiet",
        str(full_img)
    ])

    print(f"making thumbnail spectrogram for {wav_path.name}...")
    
    # Create the thumbnail spectrogram by resizing the full-size image
    run([
        "ffmpeg",
        "-i", str(full_img),
        "-vf", f"scale={thumbnail_scale}",
        "-v", "quiet",
        str(thumb_img)
    ])

# ------------------------
# HTML generation (creating the table)
# ------------------------

def generate_html(wav_files, file_dates, spec_label, rec_dir, out_dir, cell_width, cell_height, flag_audio=False):
    """
    Generates an HTML table to display spectrograms.

    Args:
        wav_files (list of Path): List of .wav file paths
        file_dates (dict): {wav_path: datetime} mapping produced by parse_recording_datetime
        spec_label (str): Frequency range identifier for filenames (e.g., "lf")
        rec_dir (Path): Directory containing the source recordings (read-only;
            only used to link an optional <audio> player back to the original WAV)
        out_dir (Path): Directory the HTML/CSS and spectrogram images live in
            (may differ from rec_dir, e.g. when --output-dir is used)
    """
    # Look up each WAV file by its (date, time) key, regardless of the
    # original filename format/prefix, so the table only depends on the
    # parsed datetime, not on any specific naming convention.
    files_by_datetime = {}
    for w in wav_files:
        key = (file_dates[w].strftime("%Y%m%d"), file_dates[w].strftime("%H%M%S"))
        previous = files_by_datetime.get(key)
        if previous is not None:
            # One cell per date+time: with --recursive, two subfolders can
            # easily hold recordings made at the same moment (e.g. two
            # recorders on the same schedule). Only one can be shown, so say
            # which one is dropped rather than losing it silently.
            print(
                f"Warning: {w} and {previous} share the recording time "
                f"{key[0]} {key[1]}; only {previous} is shown in the calendar."
            )
            continue
        files_by_datetime[key] = w
    unique_dates = sorted({key[0] for key in files_by_datetime})
    unique_times = sorted({key[1] for key in files_by_datetime})

    index = out_dir / f"index_{spec_label}.html"
    with index.open("w") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write('<link rel="stylesheet" type="text/css" href="spectrogram-table.css">\n')
        f.write("</head>\n<body>\n")

        f.write('<div id="table-scroll" class="table-scroll">\n')
        f.write('<table id="main-table" class="main-table">\n')

        # Header row: Time and Dates
        f.write("<thead><tr><th>Time</th>")
        for d in unique_dates:
            f.write(f"<th>{d}</th>")
        f.write("</tr></thead>\n")

        # Body rows: Times and corresponding spectrogram images + audio players
        f.write("<tbody>\n")
        for t in unique_times:
            f.write("<tr>")
            f.write(f"<th>{t[:2]}:{t[2:4]}</th>")
            for d in unique_dates:
                wav_for_cell = files_by_datetime.get((d, t))
                img = (
                    spectrogram_output_dir(wav_for_cell, rec_dir, out_dir)
                    / f"{wav_for_cell.stem}-thumbnail-{spec_label}.png"
                    if wav_for_cell
                    else None
                )

                if wav_for_cell is not None and img.exists():  # Check if the spectrogram image exists
                    # Use relative paths from out_dir, even when rec_dir isn't
                    # one of its ancestors (e.g. a separate --output-dir)
                    img_rel_path = os.path.relpath(img, out_dir)
                    wav_rel_path = os.path.relpath(wav_for_cell, out_dir)

                    # Add image and player
                    f.write(f'<td><img src="{img_rel_path}" width="{cell_width}" height="{cell_height}"><br>')
                    if flag_audio:
                        f.write(f'<audio controls preload="none"><source src="{wav_rel_path}" type="audio/wav">Your browser does not support the audio element.</audio>')
                    f.write('</td>')
                else:
                    f.write("<td>&nbsp;</td>")
            f.write("</tr>\n")

        f.write("</tbody></table></div>\n")
        f.write("</body></html>\n")

    print("index.html generated")

# ------------------------
# Process single wav file
# ------------------------
def process_wav_file(wav, args, out_dir):
    """
    Wrapper function for processing a single .wav file to generate its spectrogram.
    This allows for parallel processing of each .wav file.
    """
    print(f"Processing {wav.name}...")
    spectrogram_scipy(
        wav,
        args.highest_freq,
        args.lowest_freq,
        args.spec_label,
        args.img_size,
        args.thumbnail_scale,
        out_dir,
    )

# ------------------------
# Process single wav file by calling ffmpeg
# ------------------------
def process_wav_file_with_ffmpeg(wav, args, out_dir):
    """
    Wrapper function for processing a single .wav file to generate its spectrogram.
    This allows for parallel processing of each .wav file.
    """
    print(f"Processing {wav.name} with ffmpeg...")
    spectrogram_ffmpeg(
                    wav,
                    args.gain,
                    args.highest_freq,
                    args.lowest_freq,
                    args.gain_scale,
                    args.freq_scale,
                    args.color_choice,
                    args.spec_label,
                    args.img_size,
                    args.thumbnail_scale,
                    out_dir,
                )

# ------------------------
# Main function (entry point)
# ------------------------

def main():
    """
    Main entry point of the script. Parses command-line arguments, processes the WAV files,
    generates spectrograms, and creates the HTML table.
    """
    exec_start_time = time.time()

    parser = argparse.ArgumentParser(description="Generate a spectrogram calendar from WAV recordings")
    parser.add_argument("recording_dir", type=Path, nargs="?", default=None, help="Directory containing .wav recordings (required, unless set via 'recording_dir' in --config)")
    parser.add_argument("--config", type=Path, default=None, help="Path to a YAML file providing default values for any of these options (see example_config.yaml). Options passed on the command line always take precedence over the config file.")

    # Spectrogram parameters (from original bash script)
    parser.add_argument("--gain", type=int, default=1, help="Gain in dB for spectrogram image")
    parser.add_argument("--highest-freq", type=int, default=20000, help="Highest frequency for spectrogram (Hz)")
    parser.add_argument("--lowest-freq", type=int, default=0, help="Lowest frequency for spectrogram (Hz)")
    parser.add_argument("--gain-scale", default="log", help="Scaling for spectrogram ('log', 'sqrt', etc.)")
    parser.add_argument("--freq-scale", default="lin", help="Frequency scale ('lin', 'log')")
    parser.add_argument("--color-choice", default="plasma", help="Color palette for spectrogram visualization")
    parser.add_argument("--spec-label", default="", help="Spectrogram label (default: None)")
    parser.add_argument("--img-size", default="1080x720", help="Image size for spectrogram (width x height)")
    parser.add_argument("--thumbnail-scale", default="108:72", help="Thumbnail image dimensions (e.g., '108:72')")
    parser.add_argument("--use-ffmpeg", action="store_true", help="Use ffmpeg (if available) instead of scipy to compute spectrogram")
    parser.add_argument("--max-cores", type=int, default=4, help="Maximum number of cores in parallel processing")
    parser.add_argument("--clear", action="store_true", help="Clear existing spectrograms before creating new ones")
    parser.add_argument("--include-audio", action="store_true", help="Include audio player below each spectrogram image")
    parser.add_argument("--dates", nargs='*', default=None, help="Specify specific dates in the format YYYYMMDD (default: all)")
    parser.add_argument("--start-date", default=None, type=str, help="First date to include, in YYYYMMDD format (default: earliest available). Cannot be combined with --dates")
    parser.add_argument("--end-date", default=None, type=str, help="Last date to include, in YYYYMMDD format (default: latest available). Cannot be combined with --dates")
    parser.add_argument("--time-step", default=None, type=int, help="Time step in minutes (default: all)")
    parser.add_argument("--start-time", default='000000', type=str, help="Start time of the day in HHMMSS format (e.g., '050000' for 5 AM)")
    parser.add_argument("--end-time", default='235900', type=str, help="End time of the day in HHMMSS format (e.g., '090000' for 9 AM)")
    parser.add_argument("--recursive", action="store_true", help="Also look for .wav recordings in subfolders of recording_dir (default: only the top level). Spectrograms are written into a matching subfolder structure under the output directory.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory to write the spectrogram images, HTML calendar, and CSS to (default: recording_dir). When set, recording_dir is only read from, never written to.")
    parser.add_argument("--datetime-format", default="%Y%m%d_%H%M%S", help="strptime-compatible format describing how date & time are embedded in each WAV filename, after stripping --filename-prefix (default: AudioMoth's '%%Y%%m%%d_%%H%%M%%S', e.g. 20260304_100000.WAV)")
    parser.add_argument("--filename-prefix", default="", help="Literal prefix before the datetime portion of the filename, e.g. 'SM4_' for SM4_20260304_100000.wav (default: none)")

    # First pass: peek at --config only, so its values can be installed as
    # argparse defaults before the real parse. This is what makes explicit
    # CLI flags win over the config file: argparse only falls back to a
    # default (ours or the built-in one) when a flag isn't passed on argv.
    pre_args, _ = parser.parse_known_args()
    if pre_args.config:
        config_path = pre_args.config.resolve()
        valid_keys = {action.dest for action in parser._actions if action.dest not in ("help", "config")}
        try:
            config = load_yaml_config(config_path, valid_keys)
        except (OSError, ValueError, yaml.YAMLError) as e:
            sys.exit(f"Failed to load config file '{config_path}': {e}")
        parser.set_defaults(**config)

    args = parser.parse_args()

    if args.recording_dir is None:
        sys.exit("recording_dir is required: pass it as a positional argument, or set 'recording_dir' in --config")

    rec_dir = args.recording_dir.resolve()
    out_dir = args.output_dir.resolve() if args.output_dir else rec_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Option to clear existing spectrograms
    if args.clear:
        print(f"Clearing existing spectrograms in {out_dir}...")
        clear_pattern = f"*{args.spec_label}.png"
        existing = out_dir.rglob(clear_pattern) if args.recursive else out_dir.glob(clear_pattern)
        for file in existing:
            file.unlink()

    # Get WAV files and parse their embedded recording date/time
    candidates = rec_dir.rglob("*") if args.recursive else rec_dir.iterdir()
    all_wav_files = [p for p in candidates if p.is_file() and p.suffix.lower() == ".wav"]
    if not all_wav_files:
        sys.exit(
            "No WAV files found"
            if args.recursive
            else "No WAV files found (recordings inside subfolders are only picked up with --recursive)"
        )

    try:
        file_dates = {
            w: parse_recording_datetime(w, args.datetime_format, args.filename_prefix)
            for w in all_wav_files
        }
    except ValueError as e:
        sys.exit(str(e))

    all_wav_files = sorted(all_wav_files, key=lambda w: file_dates[w])

    available_dates = get_available_dates(file_dates)

    # Filter dates based on user input
    if args.dates and (args.start_date or args.end_date):
        sys.exit("--dates cannot be combined with --start-date/--end-date: use either an explicit list or a range")

    if args.dates:
        validate_dates(args.dates, available_dates)
        dates_to_process = args.dates
    elif args.start_date or args.end_date:
        try:
            dates_to_process = filter_dates_by_range(available_dates, args.start_date, args.end_date)
        except ValueError as e:
            sys.exit(str(e))
        if not dates_to_process:
            sys.exit(
                f"No recordings found in the requested date range "
                f"({args.start_date or 'any'} to {args.end_date or 'any'}). "
                f"Available dates: {', '.join(available_dates)}"
            )
    else:
        dates_to_process = available_dates

    print(f"Dates selected: {dates_to_process}")

    # Handle start-time and end-time filter
    if args.start_time and args.end_time:
        start_time = parse_time_string(args.start_time).time()
        end_time = parse_time_string(args.end_time).time()
        wav_files = filter_wav_files_by_time_window(all_wav_files, file_dates, start_time, end_time, dates_to_process)
        print(f"Selected {len(wav_files)} files between {args.start_time} and {args.end_time}.")
    else:
        wav_files = [w for w in all_wav_files if file_dates[w].strftime("%Y%m%d") in dates_to_process]

    # Handle time step filtering
    if args.time_step:
        wav_files = filter_wav_files_by_time_step(wav_files, file_dates, dates_to_process, args.time_step)
        print(f"Selected {len(wav_files)} files based on time step of {args.time_step} minutes.")

    
    if not wav_files:
        sys.exit("No WAV files found for the selected dates and time steps")

    # Mirror the recordings' subfolder structure under the output directory,
    # so files with the same name in different subfolders keep separate PNGs.
    for w in wav_files:
        spectrogram_output_dir(w, rec_dir, out_dir).mkdir(parents=True, exist_ok=True)

    use_ffmpeg = ffmpeg_available() if args.use_ffmpeg else False
    print(f"Using ffmpeg: {use_ffmpeg}")

    if use_ffmpeg:
        if args.max_cores > 1:
            # Use ProcessPoolExecutor to process multiple files concurrently
            with concurrent.futures.ProcessPoolExecutor(max_workers=args.max_cores) as executor:
                # Map the wav files to the process_wav_file function for parallel execution
                futures = [
                    executor.submit(
                        process_wav_file_with_ffmpeg,
                        wav,
                        args,
                        spectrogram_output_dir(wav, rec_dir, out_dir),
                    )
                    for wav in wav_files
                ]

                # Wait for all futures to complete (i.e., all spectrograms processed)
                concurrent.futures.wait(futures)

        else:
            for wav in wav_files:
                print(f"Processing {wav.name}...")
                spectrogram_ffmpeg(
                    wav,
                    args.gain,
                    args.highest_freq,
                    args.lowest_freq,
                    args.gain_scale,
                    args.freq_scale,
                    args.color_choice,
                    args.spec_label,
                    args.img_size,
                    args.thumbnail_scale,
                    spectrogram_output_dir(wav, rec_dir, out_dir),
                )
    else:
        if args.max_cores > 1:
            # Use ProcessPoolExecutor to process multiple files concurrently
            with concurrent.futures.ProcessPoolExecutor(max_workers=args.max_cores) as executor:
                # Map the wav files to the process_wav_file function for parallel execution
                futures = [
                    executor.submit(
                        process_wav_file,
                        wav,
                        args,
                        spectrogram_output_dir(wav, rec_dir, out_dir),
                    )
                    for wav in wav_files
                ]

                # Wait for all futures to complete (i.e., all spectrograms processed)
                concurrent.futures.wait(futures)
        else:
            for wav in wav_files:
                print(f"Processing {wav.name}...")
                spectrogram_scipy(
                    wav,
                    args.highest_freq,
                    args.lowest_freq,
                    args.spec_label,
                    args.img_size,
                    args.thumbnail_scale,
                    spectrogram_output_dir(wav, rec_dir, out_dir),
                )


    cell_size = args.thumbnail_scale.split(':')
    generate_html(wav_files, file_dates, args.spec_label, rec_dir, out_dir, cell_width=cell_size[0], cell_height=cell_size[1], flag_audio=args.include_audio)

    # Create and write the CSS file
    css_path = out_dir / "spectrogram-table.css"
    css_path.write_text(SPECTROGRAM_TABLE_CSS)
    print("spectrogram-table.css written")

    exec_end_time = time.time()

    print(f"Execution time: {exec_end_time - exec_start_time} seconds")


if __name__ == "__main__":
    # Entry point: run the main function
    main()
