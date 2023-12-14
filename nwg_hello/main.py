#!/usr/bin/env python3
import argparse
import gi
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

from gi.repository import GLib, GtkLayerShell, Gtk, Gdk, GdkPixbuf

dir_name = os.path.dirname(__file__)
log_file = os.path.join(os.environ['HOME'], '.nwg_hello.log')
voc = {}

g_socket = os.getenv("GREETD_SOCK")
client = None

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", help="print Debug messages to stderr")
parser.add_argument("-l", "--log", action="store_true", help=f"save output to '{log_file}' file")
parser.add_argument("-t", "--test", action="store_true", help="Test GUI w/o connecting to daemon")
parser.add_argument("-v", "--version", action="version", version="%(prog)s version {}".format(__version__),
                    help="display Version information")

args = parser.parse_args()

if args.log:
    # clear log file
    if os.path.isfile(log_file):
        os.remove(log_file)
    from datetime import datetime
    now = datetime.now()
    eprint(f'[nwg-hello log {now.strftime("%Y-%m-%d %H:%M:%S")}]', log=True)


# Load settings
settings = load_json("/etc/greetd/nwg-hello.json")
if settings:
    eprint("Loaded settings from: '/etc/greetd/nwg-hello.json'")
# set defaults if key not found
defaults = {
    "session_dirs": ["/usr/share/wayland-sessions", "/usr/share/xsessions"],
    "lang": ""
}
for key in defaults:
    if key not in settings:
        eprint(f"Settings: using default value for '{key}'", log=args.log)
        settings[key] = defaults[key]

if args.debug:
    eprint(f"Configured session_dirs: {settings['session_dirs']}", log=args.log)


# Load vocabulary
voc = load_json(os.path.join(dir_name, "langs", "en_US"))
user_locale = locale.getlocale()[0] if not settings["lang"] else settings["lang"]
# translate if necessary and possible
if user_locale != "en_US" and user_locale in os.listdir(os.path.join(dir_name, "langs")):
    # translated phrases
    loc = load_json(os.path.join(dir_name, "langs", user_locale))
    for key in voc:
        if key in loc:
            voc[key] = loc[key]
    eprint(f"Vocabulary translated into: {user_locale}", log=args.log)


# List users
users = list_users()
if args.debug:
    eprint(f"Found users: {users}", log=args.log)


# List sessions
sessions = list_sessions(settings['session_dirs'])
if args.debug:
    eprint(f"Found valid sessions: {sessions}", log=args.log)


def greetd(json_req):
    req = json.dumps(json_req)
    client.send(len(req).to_bytes(4, "little") + req.encode("utf-8"))
    resp_raw = client.recv(128)
    resp_len = int.from_bytes(resp_raw[0:4], "little")
    resp_trimmed = resp_raw[4:resp_len + 4].decode()
    try:
        return json.loads(resp_trimmed)
    except ValueError:
        return {}


def main():
    win = GreeterWindow(voc)

    if not args.test:
        global client
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(g_socket)

        start = 1
        while True:
            try:
                if start == 1:
                    username = input("user: ")
                    jreq = {"type": "create_session", "username": username}
                    resp = greetd(jreq)
                    print("resp1", resp)
                    start = 2

                if start == 2:
                    password = input("password: ")
                    jreq = {"type": "post_auth_message_response", "response": password}
                    resp = greetd(jreq)
                    print("resp2", resp)
                    if "error_type" in resp and resp["error_type"] == "auth_error":
                        print("auth error - try again")
                        continue
                    else:
                        start = 3

                if start == 3:
                    cmd = input("cmd: ")
                    jreq = {"type": "start_session", "cmd": cmd.split()}
                    resp = greetd(jreq)
                    print("resp3", resp)
                    if "type" in resp and resp["type"] == "success":
                        sys.exit()

            except KeyboardInterrupt as k:
                print("interrupted")
                client.close()
                break
    Gtk.main()


if __name__ == "__main__":
    sys.exit(main())
