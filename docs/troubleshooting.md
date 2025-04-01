# Troubleshooting app

App logs can be found in:
- macOS: `/Users/username/Library/Application Support/Statusbar Converter/log.txt`
- Linux: `/home/username/.config/Statusbar Converter/log.txt`
- Logs are written to stdout as well. Can be seen in the terminal, when running app from the terminal 

App can be run in `debug` mode to write more verbose logs. It will write text that was copied and
attempted to parse. `debug` mode can be enabled with:
- `--debug` CLI option when running from the terminal
- `debug: true` configuration option in `config.user.yml`. Configuration file is in the same directory as logs (see above)
