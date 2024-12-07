# Building locally

Install `python3.10`

> On macOS, if you want to build `x86_64` architecture app on Apple Silicon, you need Python
> with `universal2` support from [python.org](https://www.python.org/downloads/release/python-31011/).
> Python from Homebrew will support only your current architecture.

Create virtualenv with:
- `./builder.sh install arm64 python3.10` (`arm64` native on macOS)
- `./builder.sh install x86_64 python3.10` (`x86_64` native on macOS/Linux)
- `./builder.sh install x86_64 python3.10-intel64` (building `x86_64` on `arm64` on macOS)
- Or see `Makefile`

Run app:
- `source .venv-macos-arm64/bin/activate`
- `python -m src`
  - `--help` to see available command-line options

Build distributable:
- `./builder.sh build arm64`

To run distributable from the command line:
- macOS: `/Applications/Statusbar\ Converter.app/Contents/MacOS/Statusbar\ Converter`
- Linux: `./Statusbar\ Converter`
