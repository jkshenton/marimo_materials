# CrystalDownloadWidget API

::: marimo_materials.crystal_download.CrystalDownloadWidget

## Synced traitlets

| Traitlet | Type | Direction | Notes |
| --- | --- | --- | --- |
| `format` | `str` | Python ↔ JS | Selected file format. Default `"cif"`. |
| `formula` | `str` | Python → JS | Chemical formula shown in the UI. |
| `n_atoms` | `int` | Python → JS | Atom count shown in the UI. |
| `filename` | `str` | Python → JS | Suggested download filename. |
| `file_content` | `str` | Python → JS | Serialised file content sent to the browser for download. |
| `error` | `str` | Python → JS | Error message; empty on success. |

## Supported formats

`cif`, `vasp` (POSCAR), `xyz`, `extxyz`, `json` (ASE JSON), `lammps-data`, `pdb`
