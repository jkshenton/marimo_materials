"""Tests for CrystalEditorWidget and its helper functions."""

import json
import pytest

ase = pytest.importorskip("ase", reason="ase not installed")


# ── helpers ───────────────────────────────────────────────────────────────────

def _cu_bulk():
    from ase.build import bulk
    return bulk("Cu", "fcc", a=3.61, cubic=True)


def _h2o():
    from ase.build import molecule
    return molecule("H2O")


def _send_op(editor, name, params=None):
    """Simulate a JS operation-button trigger on *editor* (op-only, no position data).

    Uses the dedicated op_json traitlet so atoms_json is never set to an
    op-only payload (which would crash the JS syncFromModel listener).
    """
    editor.op_json = json.dumps({"name": name, "params": params or {}})
    editor.atoms_trigger += 1


def _send_op_with_state(editor, name, params=None):
    """Simulate the Apply-site-edits + op path: sends position data alongside the op."""
    payload = json.loads(editor.atoms_json)
    payload["_op"] = {"name": name, "params": params or {}}
    editor.atoms_json = json.dumps(payload)
    editor.atoms_trigger += 1


# ── imports ───────────────────────────────────────────────────────────────────

def test_import_from_package():
    from marimo_materials import CrystalEditorWidget
    assert CrystalEditorWidget is not None


# ── _atoms_to_json ────────────────────────────────────────────────────────────

class TestAtomsToJson:
    def _fn(self, atoms):
        from marimo_materials.crystal_editor import _atoms_to_json
        return json.loads(_atoms_to_json(atoms))

    def test_keys_present_periodic(self):
        data = self._fn(_cu_bulk())
        for key in ("symbols", "positions", "scaled_positions", "cellpar", "pbc"):
            assert key in data

    def test_keys_present_molecule(self):
        data = self._fn(_h2o())
        for key in ("symbols", "positions", "scaled_positions", "cellpar", "pbc"):
            assert key in data

    def test_symbols_list(self):
        data = self._fn(_cu_bulk())
        assert isinstance(data["symbols"], list)
        assert all(isinstance(s, str) for s in data["symbols"])

    def test_n_atoms_consistent(self):
        atoms = _cu_bulk()
        data = self._fn(atoms)
        assert len(data["symbols"]) == len(atoms)
        assert len(data["positions"]) == len(atoms)
        assert len(data["scaled_positions"]) == len(atoms)

    def test_cellpar_length(self):
        data = self._fn(_cu_bulk())
        assert len(data["cellpar"]) == 6

    def test_pbc_length(self):
        data = self._fn(_cu_bulk())
        assert len(data["pbc"]) == 3

    def test_pbc_all_true_for_bulk(self):
        data = self._fn(_cu_bulk())
        assert all(data["pbc"])

    def test_pbc_all_false_for_molecule(self):
        data = self._fn(_h2o())
        assert not any(data["pbc"])

    def test_scaled_positions_approx_zero_to_one(self):
        """Fractional coords of a bulk structure should be in [0, 1)."""
        import numpy as np
        data = self._fn(_cu_bulk())
        sp = np.array(data["scaled_positions"])
        assert sp.min() >= -1e-10
        assert sp.max() < 1.0 + 1e-10


# ── _atoms_from_payload ───────────────────────────────────────────────────────

class TestAtomsFromPayload:
    def _fn(self, payload):
        from marimo_materials.crystal_editor import _atoms_from_payload
        return _atoms_from_payload(payload)

    def _roundtrip_payload(self, atoms):
        from marimo_materials.crystal_editor import _atoms_to_json
        return json.loads(_atoms_to_json(atoms))

    def test_cartesian_roundtrip_symbols(self):
        atoms = _cu_bulk()
        out = self._fn(self._roundtrip_payload(atoms))
        assert out.get_chemical_symbols() == atoms.get_chemical_symbols()

    def test_cartesian_roundtrip_positions(self):
        import numpy as np
        atoms = _cu_bulk()
        out = self._fn(self._roundtrip_payload(atoms))
        np.testing.assert_allclose(out.get_positions(), atoms.get_positions(), atol=1e-6)

    def test_fractional_roundtrip(self):
        import numpy as np
        atoms = _cu_bulk()
        payload = self._roundtrip_payload(atoms)
        payload["coords_are_fractional"] = True
        del payload["positions"]
        out = self._fn(payload)
        np.testing.assert_allclose(
            out.get_scaled_positions(), atoms.get_scaled_positions(), atol=1e-6
        )

    def test_pbc_preserved(self):
        atoms = _cu_bulk()
        out = self._fn(self._roundtrip_payload(atoms))
        assert list(out.get_pbc()) == [True, True, True]

    def test_cellpar_preserved(self):
        import numpy as np
        atoms = _cu_bulk()
        out = self._fn(self._roundtrip_payload(atoms))
        np.testing.assert_allclose(
            out.cell.cellpar(), atoms.cell.cellpar(), atol=1e-4
        )


# ── _apply_op ─────────────────────────────────────────────────────────────────

class TestApplyOp:
    def _fn(self, atoms, name, params=None):
        from marimo_materials.crystal_editor import _apply_op
        return _apply_op(atoms.copy(), {"name": name, "params": params or {}})

    def test_wrap(self):
        from ase.build import bulk
        atoms = bulk("Cu", "fcc", a=3.61, cubic=True)
        atoms.positions[0] += atoms.cell[0]  # push an atom outside
        out = self._fn(atoms, "wrap")
        assert len(out) == len(atoms)

    def test_center_vacuum(self):
        atoms = _h2o()
        out = self._fn(atoms, "center", {"vacuum": 5.0, "axis": [2]})
        assert out.cell.cellpar()[2] > atoms.cell.cellpar()[2]

    def test_center_no_args(self):
        """center() with no vacuum and no about should shift atoms, not resize cell."""
        import numpy as np
        atoms = _cu_bulk()
        cell_before = atoms.cell.cellpar().copy()
        out = self._fn(atoms, "center", {"axis": [0, 1, 2]})
        np.testing.assert_allclose(out.cell.cellpar(), cell_before, atol=1e-6)

    def test_center_about_scalar(self):
        """about=scalar is expanded to [v,v,v] and forwarded to ASE without raising."""
        out = self._fn(_cu_bulk(), "center", {"axis": [0, 1, 2], "about": 0.0})
        assert len(out) == len(_cu_bulk())

    def test_center_about_point(self):
        """about=[x,y,z] is forwarded to ASE without raising."""
        out = self._fn(_h2o(), "center", {"axis": [0, 1, 2], "about": [1.0, 2.0, 3.0]})
        assert len(out) == 3

    def test_repeat(self):
        atoms = _cu_bulk()
        n_before = len(atoms)
        out = self._fn(atoms, "repeat", {"rep": [2, 2, 1]})
        assert len(out) == n_before * 4

    def test_repeat_returns_new_atoms(self):
        atoms = _cu_bulk()
        out = self._fn(atoms, "repeat", {"rep": [1, 1, 1]})
        assert len(out) == len(atoms)

    def test_translate(self):
        import numpy as np
        atoms = _cu_bulk()
        pos_before = atoms.get_positions().copy()
        out = self._fn(atoms, "translate", {"displacement": [1.0, 0.0, 0.0]})
        np.testing.assert_allclose(out.get_positions(), pos_before + [1, 0, 0], atol=1e-8)

    def test_scale_cell(self):
        import numpy as np
        atoms = _cu_bulk()
        a_before = atoms.cell.cellpar()[0]
        out = self._fn(atoms, "scale_cell", {"factor": 1.05})
        np.testing.assert_allclose(out.cell.cellpar()[0], a_before * 1.05, rtol=1e-6)

    def test_sort(self):
        from ase import Atoms
        atoms = Atoms("CuAuCu", positions=[[0,0,0],[1,0,0],[2,0,0]])
        out = self._fn(atoms, "sort")
        syms = out.get_chemical_symbols()
        assert syms == sorted(syms)

    def test_set_cell_cellpar(self):
        import numpy as np
        atoms = _cu_bulk()
        new_cellpar = [4.0, 4.0, 4.0, 90.0, 90.0, 90.0]
        out = self._fn(atoms, "set_cell", {"cellpar": new_cellpar, "pbc": [True]*3, "scale_atoms": False})
        np.testing.assert_allclose(out.cell.cellpar()[:3], [4.0, 4.0, 4.0], atol=1e-4)

    def test_set_cell_scale_atoms(self):
        import numpy as np
        atoms = _cu_bulk()
        old_scaled = atoms.get_scaled_positions().copy()
        new_cellpar = [4.0, 4.0, 4.0, 90.0, 90.0, 90.0]
        out = self._fn(atoms, "set_cell", {"cellpar": new_cellpar, "pbc": [True]*3, "scale_atoms": True})
        np.testing.assert_allclose(out.get_scaled_positions(), old_scaled, atol=1e-6)

    def test_set_cell_matrix(self):
        """set_cell with cell_matrix should use the 3x3 matrix directly."""
        import numpy as np
        atoms = _cu_bulk()
        # Slightly stretched orthorhombic matrix
        new_matrix = [[5.0, 0.0, 0.0], [0.0, 5.0, 0.0], [0.0, 0.0, 5.0]]
        out = self._fn(atoms, "set_cell", {"cell_matrix": new_matrix, "pbc": [True]*3, "scale_atoms": False})
        np.testing.assert_allclose(out.cell.tolist(), new_matrix, atol=1e-8)

    def test_set_cell_matrix_nonortho(self):
        """set_cell with a non-orthogonal 3x3 matrix roundtrips correctly."""
        import numpy as np
        atoms = _cu_bulk()
        # Hexagonal-ish cell
        new_matrix = [[4.0, 0.0, 0.0], [-2.0, 3.464, 0.0], [0.0, 0.0, 6.5]]
        out = self._fn(atoms, "set_cell", {"cell_matrix": new_matrix, "pbc": [True]*3, "scale_atoms": False})
        np.testing.assert_allclose(out.cell.tolist(), new_matrix, atol=1e-8)

    def test_delete_atom(self):
        atoms = _cu_bulk()
        n = len(atoms)
        out = self._fn(atoms, "delete_atom", {"index": 0})
        assert len(out) == n - 1

    def test_add_atom_cartesian(self):
        import numpy as np
        atoms = _cu_bulk()
        n = len(atoms)
        out = self._fn(atoms, "add_atom", {"symbol": "Au", "position": [1.0, 1.0, 1.0]})
        assert len(out) == n + 1
        assert out[-1].symbol == "Au"
        np.testing.assert_allclose(out[-1].position, [1.0, 1.0, 1.0], atol=1e-8)

    def test_add_atom_fractional(self):
        import numpy as np
        atoms = _cu_bulk()
        n = len(atoms)
        # fractional (0.5, 0, 0) → Cartesian = 0.5 * cell[0] row
        out = self._fn(atoms, "add_atom", {
            "symbol": "Au", "position": [0.5, 0.0, 0.0], "fractional": True,
        })
        assert len(out) == n + 1
        expected = np.dot([0.5, 0.0, 0.0], atoms.cell)
        np.testing.assert_allclose(out[-1].position, expected, atol=1e-8)

    def test_unknown_op_raises(self):
        from marimo_materials.crystal_editor import _apply_op
        with pytest.raises(ValueError, match="Unknown operation"):
            _apply_op(_cu_bulk(), {"name": "explode", "params": {}})


# ── CrystalEditorWidget ───────────────────────────────────────────────────────

class TestCrystalEditorWidget:
    def _w(self, atoms=None):
        from marimo_materials import CrystalEditorWidget
        return CrystalEditorWidget(atoms)

    # Construction
    def test_init_with_atoms(self):
        w = self._w(_cu_bulk())
        assert w.n_atoms == len(_cu_bulk())
        assert w.error == ""
        assert w.atoms_json != ""

    def test_init_without_atoms(self):
        w = self._w()
        assert w.atoms is None
        assert w.n_atoms == 0
        assert w.atoms_json == ""
        assert w.error == ""

    def test_atoms_property_returns_ase_atoms(self):
        from ase import Atoms
        w = self._w(_cu_bulk())
        assert isinstance(w.atoms, Atoms)

    def test_atoms_property_independent_copy(self):
        """Mutating the returned atoms must not affect widget state."""
        w = self._w(_cu_bulk())
        original_n = w.n_atoms
        w.atoms.positions[0] += 10
        assert w.n_atoms == original_n

    # atoms setter
    def test_atoms_setter_replaces_structure(self):
        w = self._w(_cu_bulk())
        h2o = _h2o()
        w.atoms = h2o
        assert w.n_atoms == len(h2o)
        assert w.error == ""

    def test_atoms_setter_none_resets(self):
        w = self._w(_cu_bulk())
        w.atoms = None
        assert w.atoms is None
        assert w.n_atoms == 0
        assert w.atoms_json == ""

    # atoms_json roundtrip
    def test_atoms_json_contains_scaled_positions(self):
        w = self._w(_cu_bulk())
        data = json.loads(w.atoms_json)
        assert "scaled_positions" in data
        assert len(data["scaled_positions"]) == w.n_atoms

    # atoms_trigger / operations via _send_op helper
    def test_trigger_repeat(self):
        w = self._w(_cu_bulk())
        n_before = w.n_atoms
        _send_op(w, "repeat", {"rep": [2, 2, 1]})
        assert w.error == ""
        assert w.n_atoms == n_before * 4

    def test_trigger_delete_atom(self):
        w = self._w(_cu_bulk())
        n_before = w.n_atoms
        _send_op(w, "delete_atom", {"index": 0})
        assert w.error == ""
        assert w.n_atoms == n_before - 1

    def test_trigger_add_atom_cartesian(self):
        w = self._w(_cu_bulk())
        n_before = w.n_atoms
        _send_op(w, "add_atom", {"symbol": "Au", "position": [0.0, 0.0, 0.0]})
        assert w.error == ""
        assert w.n_atoms == n_before + 1

    def test_trigger_add_atom_fractional(self):
        w = self._w(_cu_bulk())
        n_before = w.n_atoms
        _send_op(w, "add_atom", {"symbol": "Au", "position": [0.5, 0.5, 0.5], "fractional": True})
        assert w.error == ""
        assert w.n_atoms == n_before + 1

    def test_trigger_sort(self):
        from ase import Atoms
        atoms = Atoms("CuAuCu", positions=[[0,0,0],[1,0,0],[2,0,0]])
        w = self._w(atoms)
        _send_op(w, "sort")
        assert w.error == ""
        syms = w.atoms.get_chemical_symbols()
        assert syms == sorted(syms)

    def test_trigger_center(self):
        w = self._w(_h2o())
        c_before = w.atoms.cell.cellpar()[2]
        _send_op(w, "center", {"vacuum": 5.0, "axis": [2]})
        assert w.error == ""
        assert w.atoms.cell.cellpar()[2] > c_before

    def test_trigger_scale_cell(self):
        import numpy as np
        w = self._w(_cu_bulk())
        a_before = w.atoms.cell.cellpar()[0]
        _send_op(w, "scale_cell", {"factor": 1.1})
        assert w.error == ""
        np.testing.assert_allclose(w.atoms.cell.cellpar()[0], a_before * 1.1, rtol=1e-5)

    def test_trigger_translate(self):
        import numpy as np
        w = self._w(_cu_bulk())
        pos_before = w.atoms.get_positions().copy()
        _send_op(w, "translate", {"displacement": [1.0, 0.0, 0.0]})
        assert w.error == ""
        np.testing.assert_allclose(w.atoms.get_positions(), pos_before + [1, 0, 0], atol=1e-6)

    # Fractional mode site edits (simulate JS sending coords_are_fractional)
    def test_fractional_site_edit(self):
        import numpy as np
        w = self._w(_cu_bulk())
        data = json.loads(w.atoms_json)
        sp = data["scaled_positions"]
        sp[0] = [0.5, 0.5, 0.5]
        data["scaled_positions"] = sp
        data["coords_are_fractional"] = True
        del data["positions"]
        w.atoms_json = json.dumps(data)
        w.atoms_trigger += 1
        assert w.error == ""
        expected = np.dot([0.5, 0.5, 0.5], w.atoms.cell)
        np.testing.assert_allclose(w.atoms.get_positions()[0], expected, atol=1e-4)

    # Error handling
    def test_unknown_op_sets_error(self):
        w = self._w(_cu_bulk())
        _send_op(w, "destroy_everything")
        assert w.error != ""

    def test_error_clears_on_next_good_trigger(self):
        w = self._w(_cu_bulk())
        _send_op(w, "destroy_everything")
        assert w.error != ""
        _send_op(w, "wrap")
        assert w.error == ""

    def test_atoms_json_updated_after_op(self):
        w = self._w(_cu_bulk())
        json_before = w.atoms_json
        _send_op(w, "repeat", {"rep": [2, 1, 1]})
        assert w.atoms_json != json_before

    def test_n_atoms_consistent_after_op(self):
        w = self._w(_cu_bulk())
        _send_op(w, "repeat", {"rep": [3, 1, 1]})
        assert w.n_atoms == len(w.atoms)

    def test_trigger_with_empty_atoms_json_is_noop(self):
        w = self._w()
        w.atoms_trigger += 1  # no atoms loaded; should not raise
        assert w.atoms is None
        assert w.error == ""

    def test_repeated_center_wrap_is_stable(self):
        """Applying center+wrap many times must not shift atoms or create overlaps.

        Regression test: previously each op-button click round-tripped positions
        through 6 dp-rounded table DOM inputs, causing atoms near cell boundaries
        to drift and eventually overlap after ~5–10 cycles.
        """
        import numpy as np

        w = self._w(_cu_bulk())
        n_atoms_expected = len(w.atoms)

        for _ in range(20):
            _send_op(w, "center", {"vacuum": None, "axis": [0, 1, 2]})
            assert w.error == ""
            _send_op(w, "wrap")
            assert w.error == ""

        pos_final = w.atoms.get_positions()
        assert len(pos_final) == n_atoms_expected, "atom count changed"

        # Positions should be stable to machine precision (no accumulated drift)
        # Check via fractional coordinates so the test is cell-agnostic
        sc0 = w.atoms.get_scaled_positions()
        # All fractional coords must be in [0, 1)
        assert np.all(sc0 >= 0) and np.all(sc0 < 1), "atoms outside cell after center+wrap cycles"

        # No two atoms should be within 0.5 Å of each other (cubic Cu nn ~2.55 Å)
        from ase.geometry import get_distances
        _, dists = get_distances(pos_final, cell=w.atoms.cell, pbc=w.atoms.pbc)
        np.fill_diagonal(dists, np.inf)
        assert dists.min() > 0.5, f"overlapping atoms found (min dist {dists.min():.4f} Å)"
