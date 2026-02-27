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
