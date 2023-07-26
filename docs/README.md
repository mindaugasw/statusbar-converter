# Statusbar Converter

A small tool to easily convert timestamp to human-readable time. Just copy the
timestamp and it will automatically show as time in the statusbar: 

![demo](/docs/demo-2.gif)


## Installation on macOS

- Download the latest release from [GitHub](https://github.com/mindaugasw/statusbar-converter/releases)
- Extract zip into `Applications`
- On macOS you must manually remove quarantine attribute, because the app is not signed:  
  `xattr -d com.apple.quarantine /Applications/Statusbar\ Converter.app/`
- Start the app. A new icon will appear on the statusbar
- To automatically launch the app on boot, go to System Preferences, search for `Login items` and add the app
- _Tip:_ on macOS you can change icon order on the statusbar with Cmd-click


## Installation on Linux

- Run `sudo apt-get install xsel gir1.2-appindicator3-0.1`
- Download the latest release from [GitHub](https://github.com/mindaugasw/statusbar-converter/releases)
- Extract zip
- Start the app. A new icon will appear on the statusbar
- To automatically launch the app on boot, open `Startup Applications Preferences` and add the app


## Building locally

[See documentation for building locally.](/docs/building.md)
