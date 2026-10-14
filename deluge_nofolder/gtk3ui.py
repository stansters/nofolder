from deluge.plugins.pluginbase import Gtk3PluginBase

from .gtkprefs import GtkPrefsMixin


class Gtk3UI(Gtk3PluginBase, GtkPrefsMixin):
    pass
