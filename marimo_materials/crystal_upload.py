"""CrystalUploadWidget – upload a crystal structure file and read it with ASE.

Usage pattern::

    from marimo_materials import CrystalUploadWidget
    import marimo as mo

    uploader = CrystalUploadWidget()
    widget = mo.ui.anywidget(uploader)
    widget   # renders the upload UI

    # In a dependent cell (re-runs on every upload or kwarg change):
    atoms = uploader.atoms   # ase.Atoms, or None if nothing loaded yet
    print(atoms)

The widget exposes these synced traitlets so marimo can react to them:

    filename        – original filename of the uploaded file
    ase_format      – ASE format string (empty string → auto-detect)
    index           – frame index for trajectory files (default "0");
                      accepts integers as strings ("0", "-1") or slice
                      specs (":") as supported by ase.io.read
    file_content_b64 – base-64-encoded file bytes (written by the JS side)

Any extra ASE read keyword arguments (beyond ``format`` and ``index``) can
be supplied at construction time via ``read_kwargs``::

    uploader = CrystalUploadWidget(read_kwargs={"subtrans_included": False})
"""

from __future__ import annotations

import base64
import json
import os
import tempfile
import warnings
from pathlib import Path
from typing import Any

import anywidget
import traitlets


class CrystalUploadWidget(anywidget.AnyWidget):
    """Upload a crystal structure file and parse it with ASE.

    Parameters
    ----------
    ase_format:
        ASE format string passed to ``ase.io.read`` as the ``format``
        keyword.  Leave empty (the default) to let ASE auto-detect the
        format from the filename extension.
    index:
        Frame selector passed to ``ase.io.read`` as the ``index`` keyword.
        Use ``"0"`` for the first frame, ``"-1"`` for the last, or ``":"``
        to read all frames of a trajectory.  Defaults to ``"0"``.
    read_kwargs:
        Additional keyword arguments forwarded verbatim to
        ``ase.io.read``.  Useful for format-specific options.
    """

    _esm = Path(__file__).parent / "static" / "crystal-upload.js"
    _css = (Path(__file__).parent / "static" / "crystal-shared.css").read_text() + (Path(__file__).parent / "static" / "crystal-upload.css").read_text()

    # Synced with the JS widget
    filename: str = traitlets.Unicode("").tag(sync=True)
    ase_format: str = traitlets.Unicode("").tag(sync=True)
    index: str = traitlets.Unicode("0").tag(sync=True)
    file_content_b64: str = traitlets.Unicode("").tag(sync=True)
    parse_trigger: int = traitlets.Int(0).tag(sync=True)
    parse_error: str = traitlets.Unicode("").tag(sync=True)
    parse_warnings: str = traitlets.Unicode("").tag(sync=True)
    frames_count: int = traitlets.Int(0).tag(sync=True)
    extra_kwargs_json: str = traitlets.Unicode("").tag(sync=True)

    def __init__(
        self,
        *,
        ase_format: str = "",
        index: str = "0",
        read_kwargs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(ase_format=ase_format, index=index, **kwargs)
        self._read_kwargs: dict[str, Any] = read_kwargs or {}
        self._frames: list[Any] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @traitlets.observe("file_content_b64")
    def _on_file_change(self, _change: dict) -> None:  # noqa: ARG002
        """Reset state when a new file is uploaded."""
        self._frames = []
        self.frames_count = 0
        self.parse_error = ""
        self.parse_warnings = ""

    @traitlets.observe("parse_trigger")
    def _on_parse_trigger(self, _change: dict) -> None:  # noqa: ARG002
        """Parse when the user clicks the Parse button."""
        # Clear stale state first so the UI always reflects the current attempt.
        self.parse_error = ""
        self.parse_warnings = ""
        self.frames_count = 0
        self._frames = []
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                self._frames = self._parse()
            self.frames_count = len(self._frames)
            if caught:
                self.parse_warnings = "\n".join(
                    str(w.message) for w in caught
                )
        except Exception as exc:
            self.parse_error = str(exc)

    def _parse(self) -> list[Any]:
        """Decode the uploaded bytes and read them with ASE.

        Returns a list of ``ase.Atoms`` (possibly length 1).
        Raises on any failure, including ASE warnings promoted to errors.
        Does NOT touch any traitlets — all state mutations live in the caller.
        """
        if not self.file_content_b64:
            return []
        import ase.io

        raw = base64.b64decode(self.file_content_b64)

        kwargs: dict[str, Any] = dict(self._read_kwargs)
        if self.ase_format:
            kwargs["format"] = self.ase_format
        if self.extra_kwargs_json.strip():
            try:
                kwargs.update(json.loads(self.extra_kwargs_json))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in extra kwargs: {exc}") from exc

        # index can be "0", "-1", or a slice spec like ":"
        idx: Any = self.index
        try:
            idx = int(idx)
        except ValueError:
            pass  # keep as-is for slice specs

        # Write to a temp file with the correct suffix so ASE can
        # auto-detect the format AND open in the right mode (text vs binary).
        # Using a BytesIO buffer fails for text-based formats like .magres.
        suffix = Path(self.filename).suffix if self.filename else ""
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name
        try:
            result = ase.io.read(tmp_path, index=idx, **kwargs)
        finally:
            os.unlink(tmp_path)

        # Normalise: always return a list of Atoms.
        if not isinstance(result, list):
            result = [result]
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def frames(self) -> list[Any]:
        """All parsed frames as a list of ``ase.Atoms``.

        Returns an empty list until a successful parse.
        Use ``index=":"`` to load every frame of a trajectory.
        """
        return list(self._frames)

    @property
    def atoms(self) -> Any:
        """The first parsed frame (``ase.Atoms``), or ``None``.

        Convenience accessor equivalent to ``widget.frames[0]``.
        Populated by clicking the Parse button in the widget.
        """
        return self._frames[0] if self._frames else None
