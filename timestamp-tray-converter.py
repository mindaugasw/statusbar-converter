import os, gi, thread, re, time, datetime
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator

# Selection monitoring tutorial: https://askubuntu.com/a/1167129/1152277
# AppIndicator tutorial: https://fosspost.org/custom-system-tray-icon-indicator-linux/
# AppIndicator usage examples: https://www.programcreek.com/python/example/103466/gi.repository.AppIndicator3

# App configuration:
TRAY_APP_ID = "timestamp-tray-converter"
CLIPNOTIFY_PATH = os.path.dirname(__file__) + "/clipnotify/clipnotify"
TRAY_ICON = "clock-app" # can choose from /usr/share/icons
TIMESTAMP_REGEX = "^\d{9,11}$" # will be used to determine if selection is a timestamp
CLEAR_ON_SELECTION_CHANGE = False # whether to keep label text until new timestamp is detected, or clear label immediately on selection change
LABEL_EMPTY = "" # string that will be used to clear label text
TIME_FRACTIONAL_FORMAT = "%.1f" # how many decimal places to print in for relative time

# Time string formatting
# Structure: [max time diff in seconds, string format]
#
# Format is chosen based on time difference (in seconds). Each sub-array is checked
# if time diff is less than 1st element. If yes, 2nd element is used as format.
# If no format matches, last one is used as default.
#
# Supported format options:
# - all strftime() formatting
# - timestamp
# - relText - units for relative time (s/min/h/days/months/years)
# - relNumber - relative time number
# - relNumberDec - relative time number, formatted against TIME_FRACTIONAL_FORMAT
# - relIn - if timestamp is in the future, will be "in ". Otherwise empty.
# - relAgo - if timestamp is in the past, will be " ago". Otherwise empty.
FORMATS = [
    # up to 60 s, e.g. "1619295908 - 59 s ago"
    [60, "{timestamp} - {relIn}{relNumber} {relText}{relAgo}"],
    
    # up to 10 min, e.g. "1619295908 - 5.5 min ago"
    [600, "{timestamp} - {relIn}{relNumberDec} {relText}{relAgo}"],

    # up to 1 h, e.g. "1619295908 - 29 min ago (15:10)"
    [3600, "{timestamp} - {relIn}{relNumber} {relText}{relAgo} (%H:%M)"],
    
    # up to 1 day, e.g. "1619295908 - 5.5 h ago (12:00)"
    [86400, "{timestamp} - {relIn}{relNumberDec} {relText}{relAgo} (%H:%M)"],

    # up to 1 month, e.g. "1619295908 - 5.5 days ago (5th 12:00)"
    [2678400, "{timestamp} - {relIn}{relNumberDec} {relText}{relAgo} (%d{dayOrdinal} %H:%M)"],

    # up to 1 year, e.g. "1619295908 - 9.2 months ago"
    [31536000, "{timestamp} - {relIn}{relNumberDec} {relText}{relAgo}"],

    # up to 75 years, e.g. "1619295908 - 5.8 years ago ('15)"
    [2365200000, "{timestamp} - {relIn}{relNumberDec} {relText}{relAgo} ('%y)"],

    # up to many years, e.g. "1619295908 - 420 years ago"
    # default
    [2365200000, "{timestamp} - {relIn}{relNumberDec} {relText}{relAgo}"],
]


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

    # Copy current timestamp
    # TODO

    # Refresh - update "time ago" text for last copied timestamp
    refresh_command = gtk.MenuItem("Refresh last timestamp")
    refresh_command.connect("activate", refresh)
    menu.append(refresh_command)

    # Clear command
    clear_command = gtk.MenuItem("Clear")
    clear_command.connect("activate", clear)
    menu.append(clear_command)
    
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
            
            labelText = formatTimestamp(selection)
            indicator.set_label(labelText, "")

# Get data for showing relative time
# Automatically chooses second/minute/day/month/year units
# and returns numeric difference, numeric difference as float, and
# unit name as string (s/min/h/days/months/years)
#
# Returns [int diff, float diff, string unitName]
def getRelativeTime(timestamp):
    diff = abs(int(time.time()) - timestamp)
    print(diff)

    if diff < 60: # up to 60 seconds, return seconds
        return [diff, float(diff), "s"]
    elif diff < 3600: # up to 60 minutes, show minutes
        return [diff / 60, diff / 60.0, "min"]
    elif diff < 86400: # up to 1 day, show hours
        return [diff / 3600, diff / 3600.0, "h"]
    elif diff < 2678400: # up to 1 month, show days
        return [diff / 86400, diff / 86400.0, "days"]
    elif diff < 31536000: # up to 1 year, show months
        return [diff / 2678400, diff / 2678400.0, "months"]
    else: # show years
        return [diff / 31536000, diff / 31536000.0, "years"]

# Get day ordinal number (st/nd/rd/th) for given timestamp
def getDayOrdinal(timestamp):
    day = datetime.datetime.fromtimestamp(timestamp).day

    if day == 1 or day == 21 or day == 31:
        return "st"
    elif day == 2 or day == 22:
        return "nd"
    elif day == 3 or day == 23:
        return "rd"
    else:
        return "th"

# The main method for all formatting stuff: get timestamp, return ready-to-print string
def formatTimestamp(timestamp):
    timestamp = int(timestamp)

    relNumber, relNumberDec, relText = getRelativeTime(timestamp)
    relNumberDec = TIME_FRACTIONAL_FORMAT % relNumberDec

    if (timestamp - time.time() < 0):
        relIn = ""
        relAgo = " ago"
    else:
        relIn = "in "
        relAgo = ""

    diff = abs(int(time.time()) - timestamp)

    chosenFormat = None
    for f in FORMATS:
        if (diff < f[0]):
            chosenFormat = f[1]
            break

    # if no format matched, use the last one
    if chosenFormat == None:
        chosenFormat = FORMATS[-1][1]


    text = chosenFormat.format(
        timestamp = timestamp,
        relIn = relIn,
        relAgo = relAgo,
        relNumber = relNumber,
        relNumberDec = relNumberDec,
        relText = relText,
        dayOrdinal = getDayOrdinal(timestamp))
    text = datetime.datetime.fromtimestamp(timestamp).strftime(text)

    return text

if __name__ == "__main__":
    main()
