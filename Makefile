.PHONY: docs test docs-demos docs-serve docs-build docs-llm docs-gh

install:
	uv venv --allow-existing
	uv pip install -e '.[test,docs]'

test:
	uv pip install -e '.[test]'
	uv run pytest --ignore=tests/test_browser

test-browser:
	uv pip install -e '.[test-browser]'
	uv run playwright install chromium
	uv run pytest tests/test_browser -v

test-all:
	uv pip install -e '.[test-browser]'
	uv run playwright install chromium
	uv run pytest -v

pypi: clean
	uv build
	uv publish

clean:
	rm -rf .ipynb_checkpoints build dist marimo_materials.egg-info

docs: docs-demos
	mkdocs build -f mkdocs.yml
	uv run python scripts/copy_docs_md.py

docs-demos:
	uv run python scripts/export_marimo_demos.py --force

docs-serve:
	uv run python -m http.server --directory site

docs-build: docs-demos
	uv run mkdocs build -f mkdocs.yml
	uv run python scripts/copy_docs_md.py

docs-llm:
	uv run python scripts/copy_docs_md.py

docs-gh: docs-build
	uv run mkdocs gh-deploy -f mkdocs.yml --dirty
