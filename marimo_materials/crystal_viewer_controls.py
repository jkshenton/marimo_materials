"""Factory functions for marimo UI controls for CrystalViewer.

Marimo's reactivity graph works at the *variable* level, so UI elements must
be individual named variables in a cell's return tuple – not buried inside a
class instance or dict.  These helpers follow that pattern:

1. Call :func:`make_viewer_controls` and unpack all controls into named
   variables in one cell::

       from marimo_materials.crystal_viewer_controls import make_viewer_controls

       (
           model_style_ctrl,
           color_type_ctrl,
           show_bonded_ctrl,
           boundary_ctrl,
           hide_long_bonds_ctrl,
           show_hydrogen_bonds_ctrl,
       ) = make_viewer_controls(mo)

2. In a *dependent* cell, build the viewer and display the panel::

       from marimo_materials import CrystalViewer
       from marimo_materials.crystal_viewer_controls import (
           viewer_controls_panel,
           viewer_controls_to_kwargs,
       )

       cv = CrystalViewer(
           **viewer_controls_to_kwargs(
               model_style_ctrl, color_type_ctrl, show_bonded_ctrl,
               boundary_ctrl, hide_long_bonds_ctrl, show_hydrogen_bonds_ctrl,
           ),
           height="520px",
       )

       viewer_controls_panel(
           mo,
           model_style_ctrl, color_type_ctrl, show_bonded_ctrl,
           boundary_ctrl, hide_long_bonds_ctrl, show_hydrogen_bonds_ctrl,
       )
"""

from __future__ import annotations


def make_viewer_controls(
    mo,
    *,
    model_style: str = "Polyhedra",
    color_type: str = "VESTA",
    show_bonded_atoms: bool = True,
    boundary_expansion: float = 0.1,
    hide_long_bonds: bool = True,
    show_hydrogen_bonds: bool = False,
) -> tuple:
    """Create individual marimo UI controls for :class:`~marimo_materials.CrystalViewer`.

    Returns a 6-tuple that should be unpacked into named variables so that
    marimo can track each control as a reactive dependency::

        (
            model_style_ctrl,
            color_type_ctrl,
            show_bonded_ctrl,
            boundary_ctrl,
            hide_long_bonds_ctrl,
            show_hydrogen_bonds_ctrl,
        ) = make_viewer_controls(mo)

    Args:
        mo: The ``marimo`` module (pass the ``mo`` variable from your cell).
        model_style: Initial model-style label
            (``"Ball"``, ``"Ball+Stick"``, ``"Polyhedra"``, ``"Stick"``,
            or ``"Line"``).
        color_type: Initial colour scheme
            (``"JMOL"``, ``"VESTA"``, or ``"CPK"``).
        show_bonded_atoms: Show atoms bonded across cell boundaries.
        boundary_expansion: Fractional expansion applied symmetrically to all
            three cell axes.  ``0.1`` → ``[[-0.1, 1.1], …]``.
        hide_long_bonds: Hide bonds longer than the weas threshold.
        show_hydrogen_bonds: Show hydrogen bonds.

    Returns:
        ``(model_style_ctrl, color_type_ctrl, show_bonded_ctrl,
        boundary_ctrl, hide_long_bonds_ctrl, show_hydrogen_bonds_ctrl)``
    """
    model_style_ctrl = mo.ui.dropdown(
        options={
            "Ball": 0,
            "Ball+Stick": 1,
            "Polyhedra": 2,
            "Stick": 3,
            "Line": 4,
        },
        value=model_style,
        label="Model style",
    )
    color_type_ctrl = mo.ui.dropdown(
        options=["JMOL", "VESTA", "CPK"],
        value=color_type,
        label="Colour scheme",
    )
    show_bonded_ctrl = mo.ui.checkbox(
        show_bonded_atoms,
        label="Show bonded atoms",
    )
    boundary_ctrl = mo.ui.slider(
        start=0.0,
        stop=0.5,
        step=0.05,
        value=boundary_expansion,
        label="Boundary expansion",
        show_value=True,
    )
    hide_long_bonds_ctrl = mo.ui.checkbox(
        hide_long_bonds,
        label="Hide long bonds",
    )
    show_hydrogen_bonds_ctrl = mo.ui.checkbox(
        show_hydrogen_bonds,
        label="Show H-bonds",
    )
    return (
        model_style_ctrl,
        color_type_ctrl,
        show_bonded_ctrl,
        boundary_ctrl,
        hide_long_bonds_ctrl,
        show_hydrogen_bonds_ctrl,
    )


def viewer_controls_to_kwargs(
    model_style_ctrl,
    color_type_ctrl,
    show_bonded_ctrl,
    boundary_ctrl,
    hide_long_bonds_ctrl,
    show_hydrogen_bonds_ctrl,
) -> dict:
    """Build keyword arguments for :class:`~marimo_materials.CrystalViewer`
    from the controls returned by :func:`make_viewer_controls`.

    Pass with ``**viewer_controls_to_kwargs(...)``::

        cv = CrystalViewer(**viewer_controls_to_kwargs(
            model_style_ctrl, color_type_ctrl, show_bonded_ctrl,
            boundary_ctrl, hide_long_bonds_ctrl, show_hydrogen_bonds_ctrl,
        ))

    The ``boundary_ctrl`` slider value is expanded symmetrically into three
    ``[lo, hi]`` ranges (e.g. ``0.1`` → ``[[-0.1, 1.1], …]``).
    """
    exp = float(boundary_ctrl.value)
    lo, hi = -exp, 1.0 + exp
    return {
        "model_style": model_style_ctrl.value,
        "color_type": color_type_ctrl.value,
        "show_bonded_atoms": show_bonded_ctrl.value,
        "boundary": [[lo, hi], [lo, hi], [lo, hi]],
        "hide_long_bonds": hide_long_bonds_ctrl.value,
        "show_hydrogen_bonds": show_hydrogen_bonds_ctrl.value,
    }


def viewer_controls_panel(
    mo,
    model_style_ctrl,
    color_type_ctrl,
    show_bonded_ctrl,
    boundary_ctrl,
    hide_long_bonds_ctrl,
    show_hydrogen_bonds_ctrl,
):
    """Arrange controls into a two-row panel and return it for rendering.

    Row 1: model style / colour scheme / boundary expansion.
    Row 2: bonded-atom / long-bond / H-bond toggles.

    Render it as the last expression in a cell::

        viewer_controls_panel(mo, model_style_ctrl, ...)
    """
    return mo.vstack(
        [
            mo.hstack(
                [model_style_ctrl, color_type_ctrl, boundary_ctrl],
                justify="start",
                gap=1,
            ),
            mo.hstack(
                [show_bonded_ctrl, hide_long_bonds_ctrl, show_hydrogen_bonds_ctrl],
                justify="start",
                gap=1,
            ),
        ],
        gap=0.5,
    )
