#!/usr/bin/env python3
import argparse
import os.path
import time

from datetime import datetime
import locale
import socket
from nwg_hello.tools import *
from nwg_hello.ui import *
from nwg_hello.__about__ import __version__

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

try:
    gi.require_version('GtkLayerShell', '0.1')
except ValueError:

    raise RuntimeError('\n\n' +
                       'If you haven\'t installed GTK Layer Shell, you need to point Python to the\n' +
                       'library by setting GI_TYPELIB_PATH and LD_LIBRARY_PATH to <build-dir>/src/.\n' +
                       'For example you might need to run:\n\n' +
                       'GI_TYPELIB_PATH=build/src LD_LIBRARY_PATH=build/src python3 ' + ' '.join(sys.argv))

from gi.repository import GLib, GtkLayerShell, Gtk, Gdk

dir_name = os.path.dirname(__file__)

log_file = os.path.join(temp_dir(), 'nwg-hello.log')
voc = {}
windows = []

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", help="print Debug messages to stderr")
parser.add_argument("-l", "--log", action="store_true", help=f"save output to '{log_file}' file")
parser.add_argument("-t", "--test", action="store_true", help="Test GUI w/o connecting to daemon")
parser.add_argument("-v", "--version", action="version", version="%(prog)s version {}".format(__version__),
                    help="display Version information")

args = parser.parse_args()

if args.log:
    args.debug = True

if args.log and os.getenv("USER") == "greeter":
    now = datetime.now()
    eprint(f'[nwg-hello log {now.strftime("%Y-%m-%d %H:%M:%S")}]', log=True)

# Load settings
settings_path = "/etc/nwg-hello/nwg-hello.json" if os.path.isfile(
    "/etc/nwg-hello/nwg-hello.json") else "/etc/nwg-hello/nwg-hello-default.json"
settings = load_json(settings_path)
if settings and args.debug:
    eprint(f"Loaded settings from: '{settings_path}'", log=args.log)
# set defaults if key not found
defaults = {
    "session_dirs": [
        "/usr/share/wayland-sessions",
        "/usr/share/xsessions"
    ],
    "gtk-theme": "Adwaita",
    "gtk-icon-theme": "",
    "gtk-cursor-theme": "",
    "prefer-dark-theme": True,
    "template-name": "",
    "custom_sessions": [],
    "monitor_nums": [],
    "form_on_monitors": [],
    "delay_secs": 1,
    "lang": "",
    "cmd-sleep": "systemctl suspend",
    "cmd-reboot": "systemctl reboot",
    "cmd-poweroff": "systemctl poweroff",
    "env-vars": []
}
for key in defaults:
    if key not in settings:
        eprint(f"Settings: using default value for '{key}'", log=args.log)
        settings[key] = defaults[key]

# load cache (the file has been preinstalled and belongs to the 'greeter' user)
cache = load_json("/var/cache/nwg-hello/cache.json")
if args.debug:
    eprint(f"Loaded cache: {cache}", log=args.log)

if args.debug:
    eprint(f"Config session_dirs: {settings['session_dirs']}", log=args.log)
    if settings["custom_sessions"]:
        eprint(f"Config custom_sessions: {settings['custom_sessions']}", log=args.log)
    if settings['lang']:
        eprint(f"Config lang: {settings['lang']}", log=args.log)

if not args.test:
    eprint("Attempting to connect the client:", log=args.log)
    try:
        g_socket = os.getenv("GREETD_SOCK")
        eprint(f"socket = '{g_socket}'", log=args.log)
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        eprint(f"client = '{client}'", log=args.log)
        client.connect(g_socket)
    except Exception as e:
        eprint(f"Could not connect: {e}", log=args.log)
        args.test = True
else:
    eprint(f"Testing, skipped client connection", log=args.log)
    client = None

# Load vocabulary
if os.path.isfile("/etc/nwg-hello/en_US"):
    # allow user-defined basic lang file in /etc/nwg-hello #19
    voc = load_json("/etc/nwg-hello/en_US")
else:
    # load predefined basic lang file
    voc = load_json(os.path.join(dir_name, "langs", "en_US"))

user_locale = locale.getlocale()[0] if not settings["lang"] else settings["lang"]
# translate if necessary (and if we have a translation)
if user_locale != "en_US" and user_locale in os.listdir(os.path.join(dir_name, "langs")):
    # translated phrases
    if os.path.isfile(os.path.join("/etc/nwg-hello", user_locale)):
        # allow user-defined lang files in /etc/nwg-hello #19
        loc = load_json(os.path.join("/etc/nwg-hello", user_locale))
    else:
        # load predefined lang file
        loc = load_json(os.path.join(dir_name, "langs", user_locale))
    for key in voc:
        if key in loc:
            voc[key] = loc[key]
    if args.debug:
        eprint(f"Vocabulary translated into: '{user_locale}'", log=args.log)

# List users
users = list_users(log=args.log)
if args.debug:
    eprint(f"Found users: {users}", log=args.log)

# List sessions
sessions, x_sessions = list_sessions(settings['session_dirs'])
if args.debug:
    eprint(f"Found valid sessions: {sessions}", log=args.log)
    eprint(f"X11 sessions: {x_sessions}", log=args.log)


def set_clock():
    _now = datetime.now()
    for win in windows:
        win.update_time(_now)
    return False


def move_clock():
    _now = datetime.now()
    for win in windows:
        win.update_time(_now)
    return True


def emulate_mouse_event():
    # In order to focus the window -> password form entry, we need to perform some mouse event.
    # Although I tried hard, nothing worked well on Hyprland 0.43.0, so we'll only do it for sway.
    if os.getenv('SWAYSOCK'):
        subprocess.Popen("swaymsg seat - cursor release button1", shell=True)

    return False


def main():
    # Some monitors take longer to startup; we can just time.sleep() here, as we're not yet on the GTK loop.
    if settings["delay_secs"] > 0:
        time.sleep(settings["delay_secs"])

    # Load css
    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    try:
        style_path = "/etc/nwg-hello/nwg-hello.css" if os.path.isfile(
            "/etc/nwg-hello/nwg-hello.css") else "/etc/nwg-hello/nwg-hello-default.css"
        provider.load_from_path(style_path)
        if args.debug:
            eprint(f"Loaded style from: '{style_path}'", log=args.log)
    except Exception as e:
        eprint(f"* {e}", log=args.log)

    gtk_settings = Gtk.Settings.get_default()
    gtk_settings.set_property("gtk-application-prefer-dark-theme", True)
    if settings["gtk-theme"]:
        gtk_settings.set_property("gtk-theme-name", settings["gtk-theme"])
    if settings["gtk-icon-theme"]:
        gtk_settings.set_property("gtk-icon-theme-name", settings["gtk-icon-theme"])
    if settings["gtk-cursor-theme"]:
        gtk_settings.set_property("gtk-cursor-theme-name", settings["gtk-cursor-theme"])

    # Create UI for selected or all monitors
    global windows
    display = Gdk.Display.get_default()
    for i in reversed(range(display.get_n_monitors())):
        if not settings["monitor_nums"] or i in settings["monitor_nums"]:
            monitor = display.get_monitor(i)
            if not settings["form_on_monitors"] or i in settings["form_on_monitors"]:
                win = GreeterWindow(client, settings, sessions, x_sessions, users, monitor, voc, cache, args.log, args.test)
                windows.append(win)
            else:
                win = EmptyWindow(monitor, args.log, args.test)

    GLib.timeout_add(0, set_clock)
    GLib.timeout_add(500, move_clock)

    GLib.timeout_add(1000, emulate_mouse_event)

    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
