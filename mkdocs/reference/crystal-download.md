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

## Usage

Pass any `ase.Atoms` object and click **Download** to save the file:

```python
import marimo as mo
from ase.build import bulk
from marimo_materials import CrystalDownloadWidget

atoms = bulk("Au", "fcc", a=4.08)
dl = mo.ui.anywidget(CrystalDownloadWidget(atoms))
dl
```

Pre-select an output format:

```python
dl = mo.ui.anywidget(CrystalDownloadWidget(atoms, format="vasp"))
dl
```

Pair with a builder widget so the download always reflects the latest structure:

```python
from marimo_materials import BulkBuilderWidget

bulk_w = mo.ui.anywidget(BulkBuilderWidget())
bulk_w
```

```python
atoms = bulk_w.widget.atoms
if atoms is not None:
    mo.ui.anywidget(CrystalDownloadWidget(atoms))
```
