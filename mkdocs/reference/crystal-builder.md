# Crystal Builder Widgets API

Four widgets, one per structure type. All share the same read-back pattern:

```python
atoms = widget.widget.atoms   # ase.Atoms, or None on failure
```

---

## BulkBuilderWidget

::: marimo_materials.crystal_builder.BulkBuilderWidget

### Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `symbol` | `str` | Element symbol or formula (e.g. `"Cu"`, `"NaCl"`). |
| `crystalstructure` | `str` | Structure type; empty = ASE auto-detect. |
| `cubic` | `bool` | Request a cubic unit cell. |
| `supercell` | `list[int]` | `[na, nb, nc]` repeat counts. |
| `error` | `str` | Empty on success, error message on failure. |
| `n_atoms` | `int` | Atom count of last successful build; 0 on failure. |

---

## SurfaceBuilderWidget

::: marimo_materials.crystal_builder.SurfaceBuilderWidget

### Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `symbol` | `str` | Element symbol. |
| `facet` | `str` | Miller index string, e.g. `"111"`. |
| `layers` | `int` | Number of atomic layers. |
| `vacuum` | `float` | Vacuum thickness in Å. |
| `supercell_a` | `int` | In-plane repeat along **a**. |
| `supercell_b` | `int` | In-plane repeat along **b**. |
| `orthogonal` | `bool` | Request an orthogonal slab. |
| `error` | `str` | Empty on success; error message on failure. |
| `n_atoms` | `int` | Atom count; 0 on failure. |

---

## NanoparticleBuilderWidget

::: marimo_materials.crystal_builder.NanoparticleBuilderWidget

### Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `symbol` | `str` | Element symbol. |
| `shape` | `str` | `"Icosahedron"`, `"Decahedron"`, or `"Octahedron"`. |
| `noshells` | `int` | Number of shells (Icosahedron). |
| `p` | `int` | p parameter (Decahedron). |
| `q` | `int` | q parameter (Decahedron). |
| `r` | `int` | r parameter (Decahedron). |
| `oct_length` | `int` | Edge length in atoms (Octahedron). |
| `cutoff` | `int` | Corner cutoff (Octahedron). |
| `error` | `str` | Empty on success; error message on failure. |
| `n_atoms` | `int` | Atom count; 0 on failure. |

---

## MoleculeBuilderWidget

::: marimo_materials.crystal_builder.MoleculeBuilderWidget

### Synced traitlets

| Traitlet | Type | Notes |
| --- | --- | --- |
| `name` | `str` | Molecule name from ASE's G2 database (e.g. `"H2O"`, `"CH4"`). |
| `vacuum` | `float` | Vacuum padding in Å. |
| `error` | `str` | Empty on success; error message on failure. |
| `n_atoms` | `int` | Atom count; 0 on failure. |
