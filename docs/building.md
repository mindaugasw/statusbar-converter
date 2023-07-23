# Building locally

Install `python3.10`

> If you want to build `x86_64` architecture app on Apple Silicon, you need Python
> with `universal2` support from [python.org](https://www.python.org/downloads/release/python-31011/).
> Python from Homebrew will support only your current architecture.

Create virtualenv with:
- `./builder.sh install arm64 python3.10` (`arm64` native)
- `./builder.sh install x86_64 python3.10` (`x86_64` native)
- `./builder.sh install x86_64 python3.10-intel64` (building `x86_64` on `arm64`)

Run app:
- `source .venv-arm64/bin/activate`
- `python start.py`

Build distributable:
- `./builder.sh build arm64`
