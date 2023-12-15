import os
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, GdkPixbuf
from nwg_hello.tools import eprint


def handle_keyboard(w, event):
    if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
        Gtk.main_quit()


class GreeterWindow(Gtk.Window):
    def __init__(self, sessions, users, monitor, voc, log):
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
            self.combo_session.append(session["name"], session["name"])
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

        self.btn_sleep = builder.get_object("btn-sleep")
        self.btn_sleep.set_property("name", "power-button")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(dir_name, "img", "sleep.svg"), 48, 48)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        self.btn_sleep.set_image(img)
        self.btn_sleep.set_always_show_image(True)
        self.btn_sleep.set_image_position(Gtk.PositionType.TOP)

        self.btn_restart = builder.get_object("btn-restart")
        self.btn_restart.set_property("name", "power-button")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(dir_name, "img", "reboot.svg"), 48, 48)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        self.btn_restart.set_image(img)
        self.btn_restart.set_always_show_image(True)
        self.btn_restart.set_image_position(Gtk.PositionType.TOP)

        self.btn_poweroff = builder.get_object("btn-poweroff")
        self.btn_poweroff.set_property("name", "power-button")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(dir_name, "img", "poweroff.svg"), 48, 48)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        self.btn_poweroff.set_image(img)
        self.btn_poweroff.set_always_show_image(True)
        self.btn_poweroff.set_image_position(Gtk.PositionType.TOP)

        self.window = builder.get_object("main-window")
        self.window.connect('destroy', Gtk.main_quit)
        self.window.connect("key-release-event", handle_keyboard)

        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_interactivity(self.window, True)
        GtkLayerShell.set_monitor(self.window, monitor)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.TOP, 1)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.BOTTOM, 1)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.LEFT, 1)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, 1)
        GtkLayerShell.set_exclusive_zone(self.window, -1)

        self.window.show()
        form_wrapper.set_size_request(monitor.get_geometry().width * 0.37, 0)

    def update_time(self, now):
        self.lbl_clock.set_text(f'{now.strftime("%H:%M:%S")}')
        self.lbl_date.set_text(f'{now.strftime("%A, %d. %B")}')
