#
# gtkui.py
#
# Copyright (C) 2009 KennyWuLee <krischer.till@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

try:
    from gi.repository import Gtk
except ImportError:
    Gtk = None

from deluge.log import LOG as log
from deluge.ui.client import client
try:
    from deluge.plugins.pluginbase import Gtk3PluginBase as GtkPluginBase
except ImportError:
    from deluge.plugins.pluginbase import GtkPluginBase
import deluge.component as component
import deluge.common

from .common import get_resource


def _get_client_api():
    plugin_client = getattr(client, "nofolder", None)
    if plugin_client is None:
        plugin_client = getattr(client, "deluge_nofolder", None)
    return plugin_client


class GtkUI(GtkPluginBase):
    def enable(self):
        if Gtk is None:
            raise RuntimeError("NoFolder requires GTK 3 for Deluge 2.x")
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_resource("config.glade"))
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

    def on_apply_prefs(self):
        log.debug("applying prefs for NoFolder")
        config = {
            "dontaddfolder": self.builder.get_object("dontaddfolder_checkbutton").get_active(),
            "createfolder": self.builder.get_object("createfolder_checkbutton").get_active()
        }
        plugin_client = _get_client_api()
        if plugin_client is not None:
            plugin_client.set_config(config)

    def on_show_prefs(self):
        plugin_client = _get_client_api()
        if plugin_client is not None:
            plugin_client.get_config().addCallback(self.cb_get_config)

    def cb_get_config(self, config):
        "callback for on show_prefs"
        self.builder.get_object("dontaddfolder_checkbutton").set_active(bool(config.get("dontaddfolder", False)))
        self.builder.get_object("createfolder_checkbutton").set_active(bool(config.get("createfolder", False)))
