import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


def handle_keyboard(w, event):
    if event.type == Gdk.EventType.KEY_RELEASE and event.keyval == Gdk.KEY_Escape:
        Gtk.main_quit()


class GreeterWindow(Gtk.Window):
    def __init__(self, voc):
        dir_name = os.path.dirname(__file__)
        Gtk.Window.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(dir_name, "template.glade"))

        self.lbl_welcome = builder.get_object("lbl-welcome")
        self.lbl_welcome.set_text(f'{voc["welcome"]}')

        self.lbl_clock = builder.get_object("lbl-clock")

        self.lbl_date = builder.get_object("lbl-date")

        self.lbl_session = builder.get_object("lbl-session")
        self.lbl_session.set_text(f'{voc["session"]}:')

        self.window = builder.get_object("main-window")
        self.window.connect('destroy', Gtk.main_quit)
        self.window.connect("key-release-event", handle_keyboard)
        self.window.show()
