# Statusbar Converter

![MAC OS](https://img.shields.io/badge/macOS-000000?style=flat&logo=apple&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-e2643b?style=flat&logo=linux&logoColor=white)
[![GitHub release](https://img.shields.io/github/v/release/mindaugasw/statusbar-converter.svg)](https://github.com/mindaugasw/statusbar-converter/releases)

A small tool for convenient unit conversion: easily convert Unix timestamp to human-readable time,
convert metric-imperial units. Just copy the text and it will automatically show result in the statusbar: 

![demo](/docs/demo-2.gif)

<img src="/docs/screenshot-1.png" width=40% height=40%>


## Installation on macOS

- Download the latest release from [GitHub](https://github.com/mindaugasw/statusbar-converter/releases) and extract
- On macOS you must manually remove quarantine attribute, because the app is not signed:  
  `xattr -d com.apple.quarantine /Applications/Statusbar\ Converter.app/`
- Start the app. A new icon will appear on the statusbar
- _**Tip:**_ icon may be hidden if there are too many icons. On macOS you can reorder icons on the statusbar with Cmd-click and drag.


## Installation on Linux

The app is built for and tested on Ubuntu, Gnome desktop environment.

- Download the latest release from [GitHub](https://github.com/mindaugasw/statusbar-converter/releases) and extract
- Run `sudo apt-get install xsel`
- Start the app. A new icon will appear on the statusbar


## Building app

[See documentation for building app yourself.](/docs/building.md)

## Troubleshooting app

[See documentation for troubleshooting app issues.](/docs/troubleshooting.md)
