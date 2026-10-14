from deluge.log import LOG as log
from deluge.ui.client import client
import deluge.component as component

from .common import get_resource


def get_client_api():
    plugin_client = getattr(client, "nofolder", None)
    if plugin_client is None:
        plugin_client = getattr(client, "deluge_nofolder", None)
    return plugin_client


class GtkPrefsMixin(object):
    def enable(self):
        self.builder = self._load_builder()
        self.preferences = component.get("Preferences")
        self.plugin_manager = component.get("PluginManager")
        self._page_widget = self.builder.get_object("prefs_box")

        self.preferences.add_page("NoFolder", self._page_widget)
        self.plugin_manager.register_hook("on_apply_prefs", self.on_apply_prefs)
        self.plugin_manager.register_hook("on_show_prefs", self.on_show_prefs)

    def disable(self):
        if hasattr(self, "preferences"):
            self.preferences.remove_page("NoFolder")
        if hasattr(self, "plugin_manager"):
            self.plugin_manager.deregister_hook("on_apply_prefs", self.on_apply_prefs)
            self.plugin_manager.deregister_hook("on_show_prefs", self.on_show_prefs)

    def _load_builder(self):
        from gi.repository import Gtk

        return Gtk.Builder.new_from_file(get_resource("config.ui"))

    def on_apply_prefs(self):
        log.debug("applying prefs for NoFolder")
        config = {
            "dontaddfolder": self.builder.get_object("dontaddfolder_checkbutton").get_active(),
            "createfolder": self.builder.get_object("createfolder_checkbutton").get_active(),
        }
        plugin_client = get_client_api()
        if plugin_client is not None:
            plugin_client.set_config(config)

    def on_show_prefs(self):
        plugin_client = get_client_api()
        if plugin_client is not None:
            plugin_client.get_config().addCallback(self.cb_get_config)

    def cb_get_config(self, config):
        self.builder.get_object("dontaddfolder_checkbutton").set_active(
            bool(config.get("dontaddfolder", False))
        )
        self.builder.get_object("createfolder_checkbutton").set_active(
            bool(config.get("createfolder", False))
        )
