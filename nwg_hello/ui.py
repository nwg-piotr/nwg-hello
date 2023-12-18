import os
import gi
import sys

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, GdkPixbuf, GLib
from nwg_hello.tools import eprint, greetd


def handle_keyboard(w, event):
    if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
        Gtk.main_quit()
        return True


def p_icon_path(icon_name):
    # allow user-defined icons
    if os.path.isfile(f"/usr/share/nwg-hello/{icon_name}.svg"):
        return f"/usr/share/nwg-hello/{icon_name}.svg"
    else:
        return f"/usr/share/nwg-hello/{icon_name}-default.svg"


class GreeterWindow(Gtk.Window):
    def __init__(self, client, settings, sessions, users, monitor, voc, log, test):
        eprint(f"Creating GreeterWindow on {monitor}", log=log)

        self.voc = voc
        self.log = log
        self.client = client
        self.sessions = sessions
        self.x_sessions = []

        for item in self.sessions:
            if item["X"]:
                self.x_sessions.append(item["exec"])

        dir_name = os.path.dirname(__file__)
        Gtk.Window.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(dir_name, "template.glade"))

        form_wrapper = builder.get_object("form-wrapper")
        form_wrapper.set_property("name", "form-wrapper")

        self.lbl_welcome = builder.get_object("lbl-welcome")
        self.lbl_welcome.set_text(f'{voc["welcome"]}')
        self.lbl_welcome.set_property("name", "welcome-label")

        self.lbl_clock = builder.get_object("lbl-clock")
        self.lbl_clock.set_property("name", "clock-label")

        self.lbl_date = builder.get_object("lbl-date")
        self.lbl_date.set_property("name", "date-label")

        self.lbl_session = builder.get_object("lbl-session")
        self.lbl_session.set_property("name", "form-label")
        self.lbl_session.set_text(f'{voc["session"]}:')

        self.combo_session = builder.get_object("combo-session")
        self.combo_session.set_property("name", "form-combo")
        for session in sessions:
            self.combo_session.append(session["exec"], session["name"])
        if settings["custom_sessions"]:
            for item in settings["custom_sessions"]:
                self.combo_session.append(item["exec"], item["name"])
        self.combo_session.set_active_id(sessions[0]["name"])

        self.lbl_user = builder.get_object("lbl-user")
        self.lbl_user.set_property("name", "form-label")
        self.lbl_user.set_text(f'{voc["user"]}:')

        self.combo_user = builder.get_object("combo-user")
        self.combo_user.set_property("name", "form-combo")
        for user in users:
            self.combo_user.append(user, user)
        self.combo_user.set_active_id(users[0])

        self.lbl_password = builder.get_object("lbl-password")
        self.lbl_password.set_property("name", "form-label")
        self.lbl_password.set_text(f'{voc["password"]}:')

        self.entry_password = builder.get_object("entry-password")
        self.entry_password.set_property("name", "password-entry")

        self.cb_show_password = builder.get_object("cb-show-password")
        self.cb_show_password.set_label(voc["show-password"])

        self.lbl_message = builder.get_object("lbl-message")
        self.lbl_message.set_text("")

        self.btn_login = builder.get_object("btn-login")
        self.btn_login.set_property("name", "login-button")
        self.btn_login.set_label(voc["login"])
        self.btn_login.connect("clicked", self.on_login_btn)

        self.btn_sleep = builder.get_object("btn-sleep")
        self.btn_sleep.set_property("name", "power-button")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(p_icon_path("sleep")), 48, 48)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        self.btn_sleep.set_image(img)
        self.btn_sleep.set_always_show_image(True)
        self.btn_sleep.set_image_position(Gtk.PositionType.TOP)
        self.btn_sleep.set_label(voc["sleep"])

        self.btn_restart = builder.get_object("btn-restart")
        self.btn_restart.set_property("name", "power-button")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(p_icon_path("reboot")), 48, 48)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        self.btn_restart.set_image(img)
        self.btn_restart.set_always_show_image(True)
        self.btn_restart.set_image_position(Gtk.PositionType.TOP)
        self.btn_restart.set_label(voc["reboot"])

        self.btn_poweroff = builder.get_object("btn-poweroff")
        self.btn_poweroff.set_property("name", "power-button")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(p_icon_path("poweroff")), 48, 48)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        self.btn_poweroff.set_image(img)
        self.btn_poweroff.set_always_show_image(True)
        self.btn_poweroff.set_image_position(Gtk.PositionType.TOP)
        self.btn_poweroff.set_label(voc["power-off"])

        self.window = builder.get_object("main-window")
        self.window.connect('destroy', Gtk.main_quit)
        if test:
            self.window.connect("key-release-event", handle_keyboard)

        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.set_monitor(self.window, monitor)
        GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.ON_DEMAND)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_exclusive_zone(self.window, -1)

        self.window.show()
        form_wrapper.set_size_request(monitor.get_geometry().width * 0.37, 0)
        self.entry_password.grab_focus()

    def update_time(self, now):
        self.lbl_clock.set_text(f'{now.strftime("%H:%M:%S")}')
        self.lbl_date.set_text(f'{now.strftime("%A, %d. %B")}')

    def on_user_changed(self, combo):
        self.entry_password.grab_focus()

    def on_login_btn(self, btn):
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
            eprint(f"password: {password}", log=self.log)
            eprint(f"cmd: {cmd}", log=self.log)

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
                if cmd in self.x_sessions:
                    jreq = {"type": "start_session", "cmd": cmd.split(), "env": ['DISPLAY=localhost:0.0']}
                else:
                    jreq = {"type": "start_session", "cmd": cmd.split()}
                resp = greetd(self.client, jreq, log=self.log)
                if "type" in resp and resp["type"] == "success":
                    sys.exit()

        # if "type" in resp and resp["type"] == "success":
        #     sys.exit(0)
