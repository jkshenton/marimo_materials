"""Tests for show_atoms (marimo_materials.atoms_view)."""

import pytest

ase = pytest.importorskip("ase", reason="ase not installed")


# ── minimal marimo stub ───────────────────────────────────────────────────────

class _Table:
    def __init__(self, rows, label=""):
        self.rows = rows
        self.columns = list(rows[0].keys()) if rows else []

class _MdEl:
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return f"MdEl({self.text[:50]!r})"

class _Accordion:
    def __init__(self, sections):
        self.sections = sections   # dict[str, Any]

class _VStack:
    def __init__(self, items):
        self.items = items

class FakeMo:
    """Minimal marimo stub sufficient for show_atoms."""

    def md(self, text):
        return _MdEl(text)

    def vstack(self, items):
        return _VStack(items)

    def accordion(self, sections):
        return _Accordion(sections)

    class ui:
        @staticmethod
        def table(rows, label=""):
            return _Table(rows, label)


_mo = FakeMo()


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def cu_bulk():
    from ase.build import bulk
    return bulk("Cu", "fcc", a=3.61, cubic=True)


@pytest.fixture
def h2o():
    from ase.build import molecule
    return molecule("H2O")


# ── import smoke test ─────────────────────────────────────────────────────────

def test_import():
    from marimo_materials import show_atoms
    assert callable(show_atoms)


# ── None input ────────────────────────────────────────────────────────────────

def test_none_returns_placeholder():
    from marimo_materials import show_atoms
    result = show_atoms(None, _mo)
    assert isinstance(result, _MdEl)
    assert "No structure" in result.text


# ── structure of the returned element ────────────────────────────────────────

class TestReturnStructure:
    def _call(self, atoms, **kw):
        from marimo_materials import show_atoms
        return show_atoms(atoms, _mo, **kw)

    def test_returns_vstack(self, cu_bulk):
        result = self._call(cu_bulk)
        assert isinstance(result, _VStack)

    def test_vstack_has_two_items(self, cu_bulk):
        result = self._call(cu_bulk)
        assert len(result.items) == 2

    def test_first_item_is_summary_md(self, cu_bulk):
        result = self._call(cu_bulk)
        assert isinstance(result.items[0], _MdEl)

    def test_second_item_is_accordion(self, cu_bulk):
        result = self._call(cu_bulk)
        assert isinstance(result.items[1], _Accordion)

    def test_molecule_vstack_has_two_items(self, h2o):
        result = self._call(h2o)
        assert isinstance(result, _VStack)
        assert len(result.items) == 2


# ── summary table content ─────────────────────────────────────────────────────

class TestSummary:
    def _summary_text(self, atoms, **kw):
        from marimo_materials import show_atoms
        result = show_atoms(atoms, _mo, **kw)
        return result.items[0].text

    def test_formula_in_summary(self, cu_bulk):
        text = self._summary_text(cu_bulk)
        assert "Cu4" in text or "Cu" in text

    def test_atom_count_in_summary(self, cu_bulk):
        text = self._summary_text(cu_bulk)
        assert str(len(cu_bulk)) in text

    def test_periodic_yes_for_bulk(self, cu_bulk):
        text = self._summary_text(cu_bulk)
        assert "Yes" in text

    def test_periodic_no_for_molecule(self, h2o):
        text = self._summary_text(h2o)
        assert "No" in text

    def test_cellpar_in_summary_for_bulk(self, cu_bulk):
        text = self._summary_text(cu_bulk)
        assert "3.61" in text

    def test_no_cellpar_in_summary_for_molecule(self, h2o):
        text = self._summary_text(h2o)
        assert "a, b, c" not in text

    def test_title_in_summary(self, cu_bulk):
        text = self._summary_text(cu_bulk, title="myfile.cif")
        assert "myfile.cif" in text

    def test_no_title_when_omitted(self, cu_bulk):
        text = self._summary_text(cu_bulk)
        assert "###" not in text

    def test_frames_shown_when_gt_1(self, cu_bulk):
        text = self._summary_text(cu_bulk, frames_count=10)
        assert "10" in text
        assert "Frames" in text

    def test_frames_not_shown_when_1(self, cu_bulk):
        text = self._summary_text(cu_bulk, frames_count=1)
        assert "Frames" not in text

    def test_frames_not_shown_when_none(self, cu_bulk):
        text = self._summary_text(cu_bulk, frames_count=None)
        assert "Frames" not in text

    def test_pbc_axes_shown_for_bulk(self, cu_bulk):
        text = self._summary_text(cu_bulk)
        assert "PBC axes" in text


# ── Sites accordion section ───────────────────────────────────────────────────

class TestSitesSection:
    def _accordion(self, atoms, **kw):
        from marimo_materials import show_atoms
        result = show_atoms(atoms, _mo, **kw)
        return result.items[1]

    def test_sites_key_present(self, cu_bulk):
        acc = self._accordion(cu_bulk)
        assert "Sites" in acc.sections

    def test_sites_row_count(self, cu_bulk):
        acc = self._accordion(cu_bulk)
        table = acc.sections["Sites"]
        assert len(table.rows) == len(cu_bulk)

    def test_sites_has_cartesian_cols(self, cu_bulk):
        acc = self._accordion(cu_bulk)
        table = acc.sections["Sites"]
        assert "x (Å)" in table.columns
        assert "y (Å)" in table.columns
        assert "z (Å)" in table.columns

    def test_sites_has_fractional_cols_for_periodic(self, cu_bulk):
        acc = self._accordion(cu_bulk)
        table = acc.sections["Sites"]
        assert "x_frac" in table.columns
        assert "y_frac" in table.columns
        assert "z_frac" in table.columns

    def test_sites_no_fractional_cols_for_molecule(self, h2o):
        acc = self._accordion(h2o)
        table = acc.sections["Sites"]
        assert "x_frac" not in table.columns

    def test_sites_symbol_column(self, cu_bulk):
        acc = self._accordion(cu_bulk)
        table = acc.sections["Sites"]
        assert "Symbol" in table.columns

    def test_sites_index_column(self, cu_bulk):
        acc = self._accordion(cu_bulk)
        table = acc.sections["Sites"]
        assert "#" in table.columns


# ── Arrays accordion section ──────────────────────────────────────────────────

class TestArraysSection:
    def test_arrays_absent_when_no_extras(self, cu_bulk):
        from marimo_materials import show_atoms
        result = show_atoms(cu_bulk, _mo)
        acc = result.items[1]
        assert "Arrays" not in acc.sections

    def test_arrays_present_with_magmoms(self, cu_bulk):
        from marimo_materials import show_atoms
        cu_bulk.set_initial_magnetic_moments([1.0] * len(cu_bulk))
        result = show_atoms(cu_bulk, _mo)
        acc = result.items[1]
        assert "Arrays" in acc.sections

    def test_arrays_row_count_matches_n_atoms(self, cu_bulk):
        from marimo_materials import show_atoms
        cu_bulk.set_initial_magnetic_moments([1.0] * len(cu_bulk))
        result = show_atoms(cu_bulk, _mo)
        table = result.items[1].sections["Arrays"]
        assert len(table.rows) == len(cu_bulk)

    def test_arrays_scalar_value_rounded(self, cu_bulk):
        from marimo_materials import show_atoms
        cu_bulk.set_initial_magnetic_moments([1.23456789] * len(cu_bulk))
        result = show_atoms(cu_bulk, _mo)
        table = result.items[1].sections["Arrays"]
        # ASE stores magmoms as 'initial_magmoms' in arrays
        col = next(k for k in table.columns if "magmom" in k)
        val = table.rows[0][col]
        assert isinstance(val, float)
        assert abs(val - 1.234568) < 1e-5

    def test_arrays_vector_column_naming(self):
        """Force array (3-vector) should be split into force[0], force[1], force[2]."""
        import numpy as np
        from ase.build import bulk
        from marimo_materials import show_atoms

        atoms = bulk("Cu", "fcc", a=3.61, cubic=True)
        forces = np.zeros((len(atoms), 3))
        forces[:, 2] = 0.5
        atoms.arrays["forces"] = forces
        result = show_atoms(atoms, _mo)
        table = result.items[1].sections["Arrays"]
        assert "forces[0]" in table.columns
        assert "forces[1]" in table.columns
        assert "forces[2]" in table.columns


# ── Info accordion section ────────────────────────────────────────────────────

class TestInfoSection:
    def test_info_absent_when_empty(self, cu_bulk):
        from marimo_materials import show_atoms
        cu_bulk.info.clear()
        result = show_atoms(cu_bulk, _mo)
        acc = result.items[1]
        assert "Info" not in acc.sections

    def test_info_present_when_populated(self, cu_bulk):
        from marimo_materials import show_atoms
        cu_bulk.info["energy"] = -3.72
        result = show_atoms(cu_bulk, _mo)
        acc = result.items[1]
        assert "Info" in acc.sections

    def test_info_row_count(self, cu_bulk):
        from marimo_materials import show_atoms
        cu_bulk.info = {"energy": -3.72, "stress": "isotropic"}
        result = show_atoms(cu_bulk, _mo)
        table = result.items[1].sections["Info"]
        assert len(table.rows) == 2

    def test_info_key_value_columns(self, cu_bulk):
        from marimo_materials import show_atoms
        cu_bulk.info = {"k": "v"}
        result = show_atoms(cu_bulk, _mo)
        table = result.items[1].sections["Info"]
        assert "Key" in table.columns
        assert "Value" in table.columns

    def test_info_values_are_strings(self, cu_bulk):
        from marimo_materials import show_atoms
        cu_bulk.info = {"energy": -3.72}
        result = show_atoms(cu_bulk, _mo)
        table = result.items[1].sections["Info"]
        row = table.rows[0]
        assert isinstance(row["Key"], str)
        assert isinstance(row["Value"], str)
