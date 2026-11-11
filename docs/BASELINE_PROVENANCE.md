# Archived v0.3 baseline provenance

The files in this commit come from the working v0.3 source package generated on November 11, 2026, before repository initialization. They are kept as editable, text-based references; the source manuals and inspiration systems are **not** redistributable assets and were not imported.

## Layout

- `tests/test_causal_thread.py`, `tests/test_v02.py`, `tests/test_interpretation.py`: original **107** behavioral tests.
- `tests/original_tables.json`: six original d12 tables, retained beside the test that checks them.
- `schemas/`: original campaign and interpretation JSON Schemas.
- `examples/`: checkpoint, post-migration save, review trace and deterministic reproduction script.
- `docs/CAUSAL_THREAD_CORE_v0.3.md`: editable v0.3 rules manuscript.
- `.github/workflows/python-tests.yml`: stdlib-based regression checks on Python 3.11 and 3.13.

The original tests and fixtures were checked locally after mirroring this directory layout: **117 passed** when the separate v0.4 advisory tests were also present. The baseline branch itself should produce **107 tests**.

The technical core remains a prototype. These tests verify structured consistency and reference behavior, not balance, narrative truth, or rights clearance.
