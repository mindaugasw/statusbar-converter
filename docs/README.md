# Statusbar Converter

A small tool to easily convert timestamp to human-readable time. Just copy the
timestamp and it will automatically show as time in the statusbar: 

![demo](/docs/demo-2.gif)

<img src="/docs/screenshot-1.png" width=40% height=40%>


## Installation on macOS

- Download the latest release from [GitHub](https://github.com/mindaugasw/statusbar-converter/releases)
- Extract into `Applications`
- On macOS you must manually remove quarantine attribute, because the app is not signed:  
  `xattr -d com.apple.quarantine /Applications/Statusbar\ Converter.app/`
- Start the app. A new icon will appear on the statusbar
- _Tip:_ on macOS you can change icon order on the statusbar with Cmd-click


## Installation on Linux

- Download the latest release from [GitHub](https://github.com/mindaugasw/statusbar-converter/releases)
- Extract zip
- Run `sudo apt-get install xsel gir1.2-appindicator3-0.1`
- Start the app. A new icon will appear on the statusbar

The app was tested with Ubuntu, Gnome desktop environment.


## Building locally

[See documentation for building locally.](/docs/building.md)
