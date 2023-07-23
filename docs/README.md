# Statusbar Converter

A small tool to easily convert timestamp to human-readable time. Just copy the
timestamp and it will automatically show as time in the statusbar: 

![demo](/docs/demo-2.gif)


## Installation

- Download the latest release from [GitHub](https://github.com/mindaugasw/statusbar-converter/releases)  
- Extract zip  
- On macOS you must manually remove quarantine attribute, because the app is not signed:  
  `xattr -d com.apple.quarantine /Applications/Statusbar\ Converter.app/`
- Start the app. A new icon will appear on the statusbar
- To automatically launch the app on boot, go to System Preferences, search for `Login items` and add the app
- _Tip:_ on macOS you can change icon order on the statusbar with Cmd-click


## Building locally

[See documentation for building locally.](/docs/building.md)
