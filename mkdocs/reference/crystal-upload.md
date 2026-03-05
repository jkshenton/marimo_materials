# CrystalUploadWidget API

::: marimo_materials.crystal_upload.CrystalUploadWidget

## Synced traitlets

| Traitlet | Type | Direction | Notes |
| --- | --- | --- | --- |
| `filename` | `str` | JS → Python | Original filename of the uploaded file. |
| `ase_format` | `str` | Python ↔ JS | ASE format string; empty string = auto-detect. |
| `index` | `str` | Python ↔ JS | Frame index / slice for trajectory files (e.g. `"0"`, `"-1"`, `":"`). |
| `file_content_b64` | `str` | JS → Python | Base-64-encoded bytes of the uploaded file. |
| `parse_trigger` | `int` | JS → Python | Incremented each time a new file is uploaded, triggering a parse. |
| `parse_warnings` | `str` | Python → JS | Non-fatal warnings collected during ASE parsing; empty on success. |

## Read-back property

| Property | Returns | Notes |
| --- | --- | --- |
| `atoms` | `ase.Atoms \| None` | Successfully parsed structure, or `None` if no file has been uploaded. |

## Usage

Render the upload widget:

```python
import marimo as mo
from marimo_materials import CrystalUploadWidget

uploader = CrystalUploadWidget()
widget = mo.ui.anywidget(uploader)
widget
```

React to the uploaded structure in a downstream cell:

```python
from marimo_materials import CrystalViewer, show_atoms

atoms = uploader.atoms   # ase.Atoms, or None before a file is uploaded
if atoms is None:
    mo.md("_Upload a structure file (CIF, POSCAR, XYZ, …) above._")
else:
    cv = CrystalViewer(height="400px")
    cv.from_ase(atoms)
    mo.vstack([show_atoms(atoms, mo), cv.weas])
```

For multi-frame trajectory files, set the frame index before or after uploading:

```python
uploader.index = "-1"   # last frame; use ":" to load all frames
```
