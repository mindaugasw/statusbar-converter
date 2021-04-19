#!/usr/bin/python

import os, gi, thread, re, time, datetime
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator

# Selection monitoring tutorial: https://askubuntu.com/a/1167129/1152277
# AppIndicator tutorial: https://fosspost.org/custom-system-tray-icon-indicator-linux/
# AppIndicator usage examples: https://www.programcreek.com/python/example/103466/gi.repository.AppIndicator3

# App configuration:
TRAY_ICON = "clock-app" # can choose from /usr/share/icons
TIMESTAMP_REGEX = "^\d{9,11}$" # will be used to determine if selection is a timestamp
CLEAR_ON_SELECTION_CHANGE = False # whether to keep label text until new timestamp is detected, or clear label immediately on selection change
LABEL_EMPTY = "" # string that will be used to clear label text
USE_RELATIVE_TIME = True # whether print relative time or full datetime
RELATIVE_FRACTIONAL_FORMAT = "%.1f" # how many decimal places to print in relative mode
RELATIVE_SHOW_TIME = True # if enabled, will also print exact time timestamps 1-24h in the past/future
DATETIME_FORMAT = "%Y-%m-%d   %H:%M:%S" # datetime string format when using datetime mode

TRAY_APP_ID = "timestamp-tray-converter"
CLIPNOTIFY_PATH = os.path.dirname(__file__) + "/clipnotify/clipnotify"

global indicator
global lastTimestamp

lastTimestamp = int(time.time())

def main():
    if not os.path.isfile(CLIPNOTIFY_PATH):
        print("Error: clipnotify not found at \"%s\". Did you run \"make\"?" % CLIPNOTIFY_PATH)
        return

    global indicator
    indicator = appindicator.Indicator.new(TRAY_APP_ID, TRAY_ICON, appindicator.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_label(LABEL_EMPTY, "")
    indicator.set_menu(menu())
    thread.start_new_thread(selectionMonitor, ())
    gtk.main()

# Defines tray icon menu items
def menu():
    menu = gtk.Menu()

    # Clear command
    clear_command = gtk.MenuItem("Clear")
    clear_command.connect("activate", clear)
    menu.append(clear_command)

    # Refresh - update "time ago" text for last copied timestamp
    refresh_command = gtk.MenuItem("Refresh last timestamp")
    refresh_command.connect("activate", refresh)
    menu.append(refresh_command)

    # Exit command
    exit_command = gtk.MenuItem('Exit')
    exit_command.connect('activate', quit)
    menu.append(exit_command)

    menu.show_all()
    return menu

# clear label text. Can be used if app is configured to not clear automatically
def clear(_):
    indicator.set_label(LABEL_EMPTY, "")

# update "time ago" text for last copied timestamp
def refresh(_):
    if USE_RELATIVE_TIME:
        showRelativeTime(lastTimestamp)
    else:
        showDatetime(lastTimestamp)

def quit(_):
  gtk.main_quit()

# monitor selection changes and update label
def selectionMonitor():
    while True:
        os.popen(CLIPNOTIFY_PATH) # wait for selection to change, to avoid manual polling
        selection = os.popen("xsel -o").read()
        # selection = ""
        # print selection

        selection = selection.strip()
        regexResult = re.match(TIMESTAMP_REGEX, selection)
        
        if regexResult == None:
            if CLEAR_ON_SELECTION_CHANGE:
                indicator.set_label(LABEL_EMPTY, "")
            continue
        else:
            global lastTimestamp
            lastTimestamp = selection

            if USE_RELATIVE_TIME:
                showRelativeTime(selection)
            else:
                showDatetime(selection)

def showDatetime(timestamp):
    datetimeText = datetime.datetime.fromtimestamp(float(timestamp)).strftime(DATETIME_FORMAT)
    labelText = "%s - %s" % (timestamp, datetimeText)
    indicator.set_label(labelText, "")

def showRelativeTime(timestamp):
    diffSigned = int(time.time()) - int(timestamp)
    diff = abs(diffSigned)

    timeText = ""

    if diff < 60: # up to 60 seconds, show seconds
        diffText = str(diff) + " s"
    elif diff < 600: # up to 10 minutes, show minutes (fractional)
        diffText = str(RELATIVE_FRACTIONAL_FORMAT % (diff / 60.0)) + " min"
    elif diff < 3600: # up to 60 minutes, show minutes
        if RELATIVE_SHOW_TIME:
            timeText = datetime.datetime.fromtimestamp(float(timestamp)).strftime(" (%H:%M)")
        diffText = str(diff / 60) + " min"
    elif diff < 86400: # up to 1 day, show hours (fractional)
        if RELATIVE_SHOW_TIME:
            timeText = datetime.datetime.fromtimestamp(float(timestamp)).strftime(" (%H:%M)")
        diffText = str(RELATIVE_FRACTIONAL_FORMAT % (diff / 3600.0)) + " h"
    elif diff < 2678400: # up to 1 month, show days (fractional)
        diffText = str(RELATIVE_FRACTIONAL_FORMAT % (diff / 86400.0)) + " days"
    elif diff < 31536000: # up to 1 year, show months (fractional)
        diffText = str(RELATIVE_FRACTIONAL_FORMAT % (diff / 2678400.0)) + " months"
    elif diff < 315360000: # up to 10 years, show years (fractional)
        diffText = str(RELATIVE_FRACTIONAL_FORMAT % (diff / 31536000.0)) + " years"
    else: # show years
        diffText = str(diff / 31536000) + " years"

    if diffSigned > 0:
        labelFormat = "{0} - {1} ago{2}"
    else:
        labelFormat = "{0} - in {1}{2}"

    labelText = labelFormat.format(timestamp, diffText, timeText)
    indicator.set_label(labelText, "")

if __name__ == "__main__":
    main()
