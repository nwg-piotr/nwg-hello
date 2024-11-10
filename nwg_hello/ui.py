import os
import gi
import sys

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, GdkPixbuf
from nwg_hello.tools import eprint, greetd, launch, save_json


def p_icon_path(icon_name):
    # allow user-defined icons
    if os.path.isfile(f"/usr/share/nwg-hello/{icon_name}.svg"):
        return f"/usr/share/nwg-hello/{icon_name}.svg"
    else:
        return f"/usr/share/nwg-hello/{icon_name}-default.svg"


class GreeterWindow(Gtk.Window):
    def __init__(self, client, settings, sessions, x_sessions, users, monitor, voc, cache, log, test):
        eprint(f"Creating GreeterWindow on {monitor}", log=log)

        self.settings = settings
        self.voc = voc
        self.log = log
        self.client = client
        self.sessions = sessions
        self.x_sessions = x_sessions  # contains session execs, not names
        self.test = test
        self.cache = cache  # store cache with all user sessions for later

        dir_name = os.path.dirname(__file__)

        Gtk.Window.__init__(self)

        builder = Gtk.Builder()
        if self.settings["template-name"] and os.path.isfile(
                os.path.join("/etc/nwg-hello", self.settings["template-name"])):
            # use custom template if name configured (must be placed in /etc/nwg-hello/)
            builder.add_from_file(
                os.path.join(os.path.join("/etc/nwg-hello", self.settings["template-name"])))
        else:
            # use built-in template
            # (/usr/lib/python3.xx/site-packages/nwg_hello-x.y.z-py3.xx.egg/nwg_hello/template.glade)
            builder.add_from_file(os.path.join(dir_name, "template.glade"))

        form_wrapper = builder.get_object("form-wrapper")
        form_wrapper.set_property("name", "form-wrapper")

        lbl_welcome = builder.get_object("lbl-welcome")
        lbl_welcome.set_text(f'{voc["welcome"]}')
        lbl_welcome.set_property("name", "welcome-label")

        self.lbl_clock = builder.get_object("lbl-clock")
        self.lbl_clock.set_property("name", "clock-label")

        self.lbl_date = builder.get_object("lbl-date")
        self.lbl_date.set_property("name", "date-label")

        lbl_session = builder.get_object("lbl-session")
        lbl_session.set_property("name", "form-label")
        lbl_session.set_text(f'{voc["session"]}:')

        self.combo_session = builder.get_object("combo-session")
        self.combo_session.set_property("name", "form-combo")
        for session in sessions:
            self.combo_session.append(session["exec"], session["name"])
        if settings["custom_sessions"]:
            for item in settings["custom_sessions"]:
                self.combo_session.append(item["exec"], item["name"])
        if ("user" and "sessions") in self.cache and \
                self.cache["user"] in self.cache["sessions"]:
            # preselect the session stored in cache for the last user
            self.combo_session.set_active_id(self.cache["sessions"][self.cache["user"]])
        else:
            self.combo_session.set_active_id(sessions[0]["name"])
        self.combo_session.connect("changed", self.on_session_changed)

        lbl_user = builder.get_object("lbl-user")
        lbl_user.set_property("name", "form-label")
        lbl_user.set_text(f'{voc["user"]}:')

        self.combo_user = builder.get_object("combo-user")
        self.combo_user.set_property("name", "form-combo")
        for user in users:
            self.combo_user.append(user, user)
        if "user" in self.cache and self.cache["user"]:
            # preselect the user stored in cache
            self.combo_user.set_active_id(self.cache["user"])
        else:
            # or the 1st user
            self.combo_user.set_active_id(users[0])
        self.combo_user.connect("changed", self.on_user_changed)

        lbl_password = builder.get_object("lbl-password")
        lbl_password.set_property("name", "form-label")
        lbl_password.set_text(f'{voc["password"]}:')

        self.entry_password = builder.get_object("entry-password")
        self.entry_password.set_property("name", "password-entry")
        self.entry_password.set_visibility(False)
        self.entry_password.connect("button-press-event", self.clear_message_label)

        cb_show_password = builder.get_object("cb-show-password")
        cb_show_password.set_label(voc["show-password"])
        cb_show_password.connect("toggled", self.on_password_cb)

        self.lbl_message = builder.get_object("lbl-message")
        self.lbl_message.set_text("")

        btn_login = builder.get_object("btn-login")
        btn_login.set_property("name", "login-button")
        btn_login.set_label(voc["login"])
        btn_login.connect("clicked", self.login)

        btn_sleep = builder.get_object("btn-sleep")
        btn_sleep.set_property("name", "power-button")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(p_icon_path("sleep")), 48, 48)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        btn_sleep.set_image(img)
        btn_sleep.set_always_show_image(True)
        btn_sleep.set_image_position(Gtk.PositionType.TOP)
        btn_sleep.set_label(voc["sleep"])
        btn_sleep.connect("clicked", launch, settings["cmd-sleep"], self.log)

        btn_restart = builder.get_object("btn-restart")
        btn_restart.set_property("name", "power-button")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(p_icon_path("reboot")), 48, 48)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        btn_restart.set_image(img)
        btn_restart.set_always_show_image(True)
        btn_restart.set_image_position(Gtk.PositionType.TOP)
        btn_restart.set_label(voc["reboot"])
        btn_restart.connect("clicked", launch, settings["cmd-reboot"], self.log)

        btn_poweroff = builder.get_object("btn-poweroff")
        btn_poweroff.set_property("name", "power-button")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(p_icon_path("poweroff")), 48, 48)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        btn_poweroff.set_image(img)
        btn_poweroff.set_always_show_image(True)
        btn_poweroff.set_image_position(Gtk.PositionType.TOP)
        btn_poweroff.set_label(voc["power-off"])
        btn_poweroff.connect("clicked", launch, settings["cmd-poweroff"], self.log)

        self.window = builder.get_object("main-window")
        self.window.connect('destroy', Gtk.main_quit)
        self.window.connect("key-release-event", self.handle_keyboard)

        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.set_monitor(self.window, monitor)

        if self.settings["layer"].upper() == "BACKGROUND":
            GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.BACKGROUND)
        elif self.settings["layer"].upper() == "BOTTOM":
            GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.BOTTOM)
        elif self.settings["layer"].upper() == "TOP":
            GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.TOP)
        else:
            GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.OVERLAY)

        if self.settings["keyboard-mode"].upper() == "NONE":
            GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.NONE)
        elif self.settings["keyboard-mode"].upper() == "ON_DEMAND" or self.settings[
            "keyboard-mode"].upper() == "ON-DEMAND":
            GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.ON_DEMAND)
        else:
            GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.EXCLUSIVE)

        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_exclusive_zone(self.window, -1)
        GtkLayerShell.set_namespace(self.window, "nwg-hello")

        self.window.show()

        form_wrapper.set_size_request(monitor.get_geometry().width * 0.37, 0)
        self.entry_password.grab_focus()

    def handle_keyboard(self, w, event):
        if event.type == Gdk.EventType.KEY_RELEASE:
            if self.test and event.keyval == Gdk.KEY_Escape:
                Gtk.main_quit()
            elif event.keyval == Gdk.KEY_Return:
                self.login(None)

        return True

    def update_time(self, now, time_format, date_format):
        self.lbl_clock.set_text(f'{now.strftime(time_format)}')
        self.lbl_date.set_text(f'{now.strftime(date_format)}')

    def on_session_changed(self, combo):
        self.entry_password.grab_focus()
        self.clear_message_label()

    def on_user_changed(self, combo):
        selected_user = self.combo_user.get_active_id()
        if "sessions" in self.cache and selected_user in self.cache["sessions"]:
            # preselect user session if available in cache
            self.combo_session.set_active_id(self.cache["sessions"][selected_user])
        self.entry_password.grab_focus()
        self.clear_message_label()

    def clear_message_label(self, *args):
        print("clear_message_label")
        self.lbl_message.set_text("")

    def on_password_cb(self, widget):
        self.entry_password.set_visibility(widget.get_active())

    def login(self, btn):
        if not self.entry_password.get_text():
            eprint("Login: passwd empty, cancelling", log=self.log)
            self.lbl_message.set_text(self.voc["password-empty"])
            return
        if self.client:
            try:
                jreq = {"type": "cancel_session"}
                resp = greetd(self.client, jreq, log=self.log)
            except:
                pass

            user = self.combo_user.get_active_id()
            password = self.entry_password.get_text()
            cmd = self.combo_session.get_active_id()
            eprint(f"user: {user}", log=self.log)
            eprint(f"password: {'*' * len(password)}", log=self.log)
            eprint(f"cmd: {cmd}", log=self.log)
            eprint(f"env vars: {self.settings['env-vars']}", log=self.log)

            jreq = {"type": "create_session", "username": user}
            try:
                resp = greetd(self.client, jreq, log=self.log)
            except Exception as e:
                eprint(e, log=self.log)

            jreq = {"type": "post_auth_message_response", "response": password}
            resp = greetd(self.client, jreq, log=self.log)
            if "error_type" in resp and resp["error_type"] == "auth_error":
                self.lbl_message.set_text(self.voc["login-failed"])
                self.entry_password.set_text("")
            else:
                # ensure the sessions dict exists in cache
                if "sessions" not in self.cache:
                    self.cache["sessions"] = {}

                # store last used session name and username if both available
                if self.combo_user.get_active_id():
                    self.cache["user"] = self.combo_user.get_active_id()
                if self.combo_session.get_active_id():
                    self.cache["sessions"][self.cache["user"]] = self.combo_session.get_active_id()
                if self.cache["user"] and self.cache["sessions"][self.cache["user"]]:
                    eprint(f"Saving cache: {self.cache}", log=self.log)
                    # this file belongs to the 'greeter' user
                    try:
                        save_json(self.cache, "/var/cache/nwg-hello/cache.json", log=self.log)
                        eprint("Cache saved", log=self.log)
                    except Exception as e:
                        eprint(f"Error saving cache: {e}", log=self.log)

                if cmd in self.x_sessions:
                    jreq = {"type": "start_session", "cmd": ["startx", "/usr/bin/env"] + cmd.split(),
                            "env": self.settings["env-vars"]}
                else:
                    jreq = {"type": "start_session", "cmd": cmd.split(), "env": self.settings["env-vars"]}

                resp = greetd(self.client, jreq, log=self.log)
                if "type" in resp and resp["type"] == "success":
                    sys.exit()


class EmptyWindow(Gtk.Window):
    def __init__(self, settings, monitor, log, test):
        eprint(f"Creating EmptyWindow on {monitor}", log=log)

        self.test = test

        Gtk.Window.__init__(self)

        self.connect('destroy', Gtk.main_quit)
        self.connect("key-release-event", self.handle_keyboard)

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_monitor(self, monitor)

        if settings["layer"].upper() == "BACKGROUND":
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.BACKGROUND)
        elif settings["layer"].upper() == "BOTTOM":
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.BOTTOM)
        elif settings["layer"].upper() == "TOP":
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        else:
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)

        if settings["keyboard-mode"].upper() == "NONE":
            GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.NONE)
        elif settings["keyboard-mode"].upper() == "ON_DEMAND":
            GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        else:
            GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)

        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_exclusive_zone(self, -1)
        GtkLayerShell.set_namespace(self, "nwg-hello")

        self.show()

    def handle_keyboard(self, w, event):
        if event.type == Gdk.EventType.KEY_RELEASE:
            if self.test and event.keyval == Gdk.KEY_Escape:
                Gtk.main_quit()

        return True
