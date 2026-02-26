# marimo_materials

> Interactive [AnyWidgets](https://anywidget.dev/) for computational materials science notebook environments.

This project is a domain-specific widget library for materials scientists working in notebook environments (Jupyter, Marimo, VSCode, Colab, etc.). It provides interactive UI components tailored to common workflows in computational materials science — visualising crystal structures, monitoring DFT convergence, and more.

## Acknowledgements

This project is based on [wigglystuff](https://github.com/koaning/wigglystuff) by [@koaning](https://github.com/koaning), used and adapted here under the [MIT License](https://github.com/koaning/wigglystuff/blob/main/LICENSE). The scaffold, build system, and anywidget integration patterns are all drawn from that project. Go star it.

## Installation

```bash
uv pip install marimo_materials
# or
pip install marimo_materials
```

## Widgets

> 🚧 This library is in early development. Widgets will be added here as they are built.

## Development

Install all dependencies (Python + JS tooling):

```bash
make install
npm install
```

Run the JS bundler in watch mode while developing:

```bash
npm run dev
```

Run tests:

```bash
make test
```

Preview the docs locally:

```bash
make docs-serve
```

## How It Works

Each widget is a Python class with [traitlets](https://traitlets.readthedocs.io/) that sync bidirectionally with a JavaScript frontend via anywidget. The Python traits are the public API; the JS is purely the renderer. This means widgets work anywhere anywidget is supported — Jupyter, Marimo, Shiny for Python, Solara, VS Code, and Google Colab.

## License

MIT — see [LICENSE](LICENSE).

Original wigglystuff code copyright © [koaning](https://github.com/koaning), MIT License.