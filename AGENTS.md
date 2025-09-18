# Repository Guidelines

## Project Structure & Module Organization
Rust core lives in `src/lib.rs`, exposing the Python extension via PyO3. The Python surface API sits in `rusty_tags/` with `utils.py`, `datastar.py`, `events.py`, and `xtras/` for exploratory helpers. Integration demos and component playgrounds reside in `lab/` and `RustyMonsterUI/`—align updates with patterns documented under `instructions/`. Tests, including performance harnesses, live under `tests/`, while `docs/` holds draft documentation assets.

## Build, Test, and Development Commands
Run `maturin develop` whenever Rust sources change to rebuild the extension in your active virtualenv; switch to `maturin develop --release` for profiling-grade builds. Execute `pytest tests` for the functional suite (the extension must be installed first). Benchmarks such as `python tests/benchmarks/run_all.py` and `python tests/stress_test.py` probe throughput and load—use them sparingly because they are resource intensive. When iterating in notebooks or FastAPI demos, `python lab/FastapiApp.py` bootstraps the reference playground.

## Coding Style & Naming Conventions
Python modules follow PEP 8 with 4-space indents and descriptive snake_case names; ensure new exports are wired through `rusty_tags/__init__.py`. Static typing matters: run `mypy rusty_tags` and, when available, `pyright`. Rust code should pass `cargo fmt` and adhere to idiomatic `snake_case`/`CamelCase`; document any unsafe blocks inline. Keep Datastar signal helpers and Open Props naming consistent with the recipes outlined in `instructions/README.md`.

## Testing Guidelines
Add new pytest files as `tests/test_<feature>.py`, mirroring the parametrized patterns in `tests/test_datastar_basic.py` and `tests/test_boolean_attributes.py`. Validate both HTML rendering and reactive signal paths when introducing components. Benchmarks belong in `tests/benchmarks/` with a guarded `if __name__ == "__main__":` entry point. Always rebuild via `maturin develop` before running the suite to avoid stale binaries.

## Commit & Pull Request Guidelines
Commits use the existing gitmoji-style prefix plus an imperative clause (e.g., `✨ Add signal-aware accordion`). Reference affected modules and mention any instructions synced. Pull requests should summarize behavior changes, link issues, list verification commands, and include screenshots or rendered HTML snippets for UI updates in `lab/` or `RustyMonsterUI/`. Tag maintainers when touching shared tooling or build scripts.
