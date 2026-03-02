# Agents

`marimo_materials` ships a small roster of AnyWidget "agents" that surface different
input modalities (sliders, speech, paint, etc.) across notebook runtimes. This
page is a quick lookup so you can see what exists and which traitlets each agent
syncs back to Python.

## Quick reference

| Agent | Module/Class | Core traitlets | One-liner |
| --- | --- | --- | --- |
| BulkBuilderWidget | `marimo_materials.crystal_builder.BulkBuilderWidget` | `symbol`, `crystalstructure`, `cubic`, `supercell`, `error`, `n_atoms` | Build bulk crystals via `ase.build.bulk`; `.atoms` → `ase.Atoms` |
| SurfaceBuilderWidget | `marimo_materials.crystal_builder.SurfaceBuilderWidget` | `symbol`, `facet`, `layers`, `vacuum`, `supercell_a`, `supercell_b`, `orthogonal`, `error`, `n_atoms` | Build surface slabs via ASE facet builders; `.atoms` → `ase.Atoms` |
| NanoparticleBuilderWidget | `marimo_materials.crystal_builder.NanoparticleBuilderWidget` | `symbol`, `shape`, `noshells`, `p`, `q`, `r`, `oct_length`, `cutoff`, `error`, `n_atoms` | Build nanoparticles (Icosahedron/Decahedron/Octahedron) via `ase.cluster`; `.atoms` → `ase.Atoms` |
| MoleculeBuilderWidget | `marimo_materials.crystal_builder.MoleculeBuilderWidget` | `name`, `vacuum`, `error`, `n_atoms` | Build gas-phase molecules from ASE's G2 database; `.atoms` → `ase.Atoms` |
| CrystalDownloadWidget | `marimo_materials.crystal_download.CrystalDownloadWidget` | `format`, `formula`, `n_atoms`, `filename`, `file_content`, `error` | Serialise an `ase.Atoms` to CIF/POSCAR/XYZ/etc. and trigger a browser download |

## Patterns to remember

- All agents inherit from `anywidget.AnyWidget`, so `widget.observe(handler)`
  remains the standard way to react to state changes.
- Constructors tend to validate bounds, lengths, or choice counts; let the
  raised `ValueError/TraitError` guide you instead of duplicating the logic.
- Several widgets expose helper methods (e.g., `Paint.get_pil()`,
  `EdgeDraw.get_adjacency_matrix()`)—lean on those rather than re-implementing
  conversions.
- Check `marimo_materials/__init__.py` for the names that are re-exported at the
  package root so you can keep imports consistent.
- The repo standardizes on [`uv`](https://github.com/astral-sh/uv) for Python
  workflows (`uv pip install -e .` etc.) and the standard library's `pathlib`
  for filesystem paths—mirror those choices in new agents to keep the codebase
  consistent.
- When styling widgets, support both light and dark themes by defining
  component-specific CSS variables (see Matrix/SortableList). Scope your
  defaults to the widget root, mark `color-scheme: light dark`, and provide
  overrides that respond to `.dark`, `.dark-theme`, or `[data-theme="dark"]`
  ancestors so notebook-level theme toggles work instantly.
- When adding a new widget, remember to update the docs gallery
  (`mkdocs/index.md`), the README gallery (`readme.md`), and the LLM context
  file (`mkdocs/llms.txt`). Add a screenshot to `mkdocs/assets/gallery/` and
  reference it from the gallery locations to keep them in sync.
- Each widget has a demo marimo notebook in the `demos/` folder (e.g.,
  `demos/colorpicker.py`). When adding a new widget, create a corresponding
  demo notebook. Run demos with `marimo edit demos/<widget>.py`.
- **Always run `uv run marimo check demos/<notebook>.py`** after editing a demo
  notebook to verify it parses correctly and has no cell dependency issues.
- Dumber is better. Prefer obvious, direct code over clever abstractions—someone
  new to the project should be able to read the code top-to-bottom and grok it
  without needing to look up framework magic or trace through indirection.
- **Do not modify `package-lock.json`** unless intentionally updating JS
  dependencies. If it shows up in `git diff`, revert it with
  `git checkout package-lock.json`.
