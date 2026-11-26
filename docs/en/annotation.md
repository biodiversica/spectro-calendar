# Annotation Mode

*English · [Português (Brasil)](../pt-BR/annotation.md)*

`--annotate` turns the calendar into a simple annotation tool. Each cell
receives a checkbox under its thumbnail, and a toolbar at the top of the page
exports the selected recordings as a plain text file:

```bash
spectro-calendar /data/site-1 --include-audio --annotate
```

## Exporting the Selection

The recordings of interest are selected while the calendar is reviewed, and
the button **Export selection (.txt)** downloads the list. No label needs to
be entered, since the exported list itself serves as the annotation. Each
line identifies one selected recording, in the format chosen in the selector
next to the button:

| Format | Example line |
|---|---|
| `filename` (default) | `20260304_100000.WAV` |
| `date & time` | `2026-03-04 10:00:00` |
| `filename + date & time` | `20260304_100000.WAV<TAB>2026-03-04 10:00:00` |

The lines are in chronological order, and the file is named
`annotations_<label>_<YYYYMMDD-HHMMSS>.txt`, where the timestamp is the time
of the export, so that successive exports do not overwrite each other. With
`--recursive`, each filename includes the subfolder it was found in (for
example, `moth-a/20260304_100000.WAV`), since the same name can occur once
per recorder. Calendars generated for different frequency bands
(`--spec-label lf`, `hf`, and so on) export under their own names.

## Selecting a Range

To select several recordings at once, one checkbox is clicked and another is
clicked while holding **Shift**. Every checkbox in the rectangle between the
two is then set to the same state: the times between the two rows, on each
date between the two columns. For example, clicking 01 Mar 05:00 and then
Shift+clicking 03 Mar 07:00 selects 05:00 to 07:00 on 1, 2 and 3 March. All
boxes take the new state of the Shift+clicked box, so the same action over
selected boxes clears the range. Each Shift+click also becomes the starting
corner of the next range. A reminder of this appears when hovering over
**Annotation** at the left of the toolbar.

## Keeping the Selection

Selected cells are highlighted, the toolbar shows the number of selected
recordings, and **Clear selection** clears the whole selection after a
confirmation. The selection is also stored in the browser's local storage,
under a key derived from the page's location, so that it is restored when the
calendar is reloaded or reopened later.

Chrome does not provide local storage to pages opened directly from disk
(`file://`). In Chrome, the selection is therefore kept only while the tab is
open, and should be exported before the tab is closed. Firefox provides local
storage to such pages. Serving the calendar over HTTP makes the selection
persistent in every browser; the server must then be started from a directory
that contains both the output directory and the recordings, so that the audio
players can reach the recordings (for example, `python -m http.server` run in
their common parent directory). All other functions, including the export,
work from `file://` in both browsers.
