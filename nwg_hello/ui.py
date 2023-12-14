import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell
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

        main_box = builder.get_object("main-box")
        form_wrapper = builder.get_object("form-wrapper")
        form_wrapper.set_property("name", "form-wrapper")

        self.lbl_welcome = builder.get_object("lbl-welcome")
        self.lbl_welcome.set_text(f'{voc["welcome"]}')

        self.lbl_clock = builder.get_object("lbl-clock")

        self.lbl_date = builder.get_object("lbl-date")

        self.lbl_session = builder.get_object("lbl-session")
        self.lbl_session.set_property("name", "form-label")
        self.lbl_session.set_text(f'{voc["session"]}:')

        self.lbl_user = builder.get_object("lbl-user")
        self.lbl_user.set_property("name", "form-label")
        self.lbl_user.set_text(f'{voc["user"]}:')

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

        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        try:
            provider.load_from_path("/usr/share/nwg-hello/style.css")
        except Exception as e:
            eprint(f"* {e}", log=log)
        self.window.show()
        form_wrapper.set_size_request(monitor.get_geometry().width * 0.3, 0)
