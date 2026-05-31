# Building app

Install `python3.10`

Additional packages needed to build the app:  
- macOS: `brew install just create-dmg`
  - `create-dmg` is optional, to create dmg image
- Linux: `sudo apt-get install just libx11-dev libxcomposite-dev`

Create virtual env with:
- `just venv-install` 

Run app:
- `just run`
  - `just run --help` to see available command-line options
- Or to run manually:
  - `source .venv/bin/activate`
  - `python -m src`

Build distributable:
- `just build`

Run distributable from the command line:
- `just run-dist`

See all available commands:
- `just`
