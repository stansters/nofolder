import importlib
import os
import sys
import types
import unittest


def install_deluge_stubs():
    deluge = types.ModuleType("deluge")

    log_module = types.ModuleType("deluge.log")
    log_module.LOG = types.SimpleNamespace(debug=lambda *args, **kwargs: None)

    plugins_module = types.ModuleType("deluge.plugins")
    init_module = types.ModuleType("deluge.plugins.init")

    class PluginInitBase(object):
        def __init__(self, plugin_name):
            self.plugin_name = plugin_name

    init_module.PluginInitBase = PluginInitBase
    pluginbase_module = types.ModuleType("deluge.plugins.pluginbase")
    pluginbase_module.CorePluginBase = type("CorePluginBase", (object,), {})
    pluginbase_module.GtkPluginBase = type("GtkPluginBase", (object,), {})
    pluginbase_module.Gtk3PluginBase = type("Gtk3PluginBase", (object,), {})
    pluginbase_module.WebPluginBase = type("WebPluginBase", (object,), {})

    component_module = types.ModuleType("deluge.component")
    component_module.get = lambda name: None

    configmanager_module = types.ModuleType("deluge.configmanager")
    configmanager_module.ConfigManager = dict

    core_module = types.ModuleType("deluge.core")
    rpcserver_module = types.ModuleType("deluge.core.rpcserver")
    rpcserver_module.export = lambda func: func

    ui_module = types.ModuleType("deluge.ui")
    client_module = types.ModuleType("deluge.ui.client")
    client_module.client = types.SimpleNamespace(nofolder=types.SimpleNamespace(set_config=lambda *args, **kwargs: None))

    common_module = types.ModuleType("deluge.common")

    sys.modules["deluge"] = deluge
    sys.modules["deluge.log"] = log_module
    sys.modules["deluge.plugins"] = plugins_module
    sys.modules["deluge.plugins.init"] = init_module
    sys.modules["deluge.plugins.pluginbase"] = pluginbase_module
    sys.modules["deluge.component"] = component_module
    sys.modules["deluge.configmanager"] = configmanager_module
    sys.modules["deluge.core"] = core_module
    sys.modules["deluge.core.rpcserver"] = rpcserver_module
    sys.modules["deluge.ui"] = ui_module
    sys.modules["deluge.ui.client"] = client_module
    sys.modules["deluge.common"] = common_module


class CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        install_deluge_stubs()
        importlib.import_module("nofolder")

    def test_get_resource_returns_existing_data_path(self):
        from nofolder.common import get_resource

        config_path = get_resource("config.glade")
        self.assertTrue(os.path.isabs(config_path))
        self.assertTrue(os.path.exists(config_path))
        self.assertTrue(config_path.endswith(os.path.join("nofolder", "data", "config.glade")))

    def test_plugin_init_classes_import_local_modules(self):
        from nofolder import CorePlugin, Gtk3UIPlugin, GtkUIPlugin, WebUIPlugin

        self.assertEqual(CorePlugin("NoFolder")._plugin_cls.__name__, "Core")
        self.assertEqual(GtkUIPlugin("NoFolder")._plugin_cls.__name__, "GtkUI")
        self.assertEqual(Gtk3UIPlugin("NoFolder")._plugin_cls.__name__, "GtkUI")
        self.assertEqual(WebUIPlugin("NoFolder")._plugin_cls.__name__, "WebUI")

    def test_post_torrent_add_handles_deluge2_event_signature(self):
        from nofolder.core import Core

        class TorrentStub:
            def __init__(self):
                self.paused = False
                self.resumed = False

            def pause(self):
                self.paused = True

            def get_status(self, status_keys):
                return {"files": [], "save_path": "/tmp", "name": "archive"}

            def resume(self):
                self.resumed = True

        core = Core()
        core.config = {"dontaddfolder": True, "createfolder": False}
        core.torrents = {"abc123": TorrentStub()}

        core.post_torrent_add("abc123", from_state=True)

        self.assertTrue(core.torrents["abc123"].paused)
        self.assertTrue(core.torrents["abc123"].resumed)


if __name__ == "__main__":
    unittest.main()
