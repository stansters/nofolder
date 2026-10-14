import importlib
import os
import sys
import types
import unittest
import xml.etree.ElementTree as ET


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def purge_modules(prefixes):
    for module_name in list(sys.modules):
        if any(
            module_name == prefix or module_name.startswith(prefix + ".")
            for prefix in prefixes
        ):
            sys.modules.pop(module_name, None)


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
    client_module.client = types.SimpleNamespace(
        nofolder=types.SimpleNamespace(
            set_config=lambda *args, **kwargs: None,
            get_config=lambda *args, **kwargs: None,
        ),
        deluge_nofolder=types.SimpleNamespace(
            set_config=lambda *args, **kwargs: None,
            get_config=lambda *args, **kwargs: None,
        ),
    )

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


def install_gtk_stubs():
    class WidgetStub:
        def __init__(self):
            self.active = False

        def get_active(self):
            return self.active

        def set_active(self, value):
            self.active = bool(value)

    class BuilderStub:
        def __init__(self, path=None):
            self.loaded_files = []
            if path is not None:
                self.loaded_files.append(path)
            self.objects = {
                "prefs_box": object(),
                "dontaddfolder_checkbutton": WidgetStub(),
                "createfolder_checkbutton": WidgetStub(),
            }

        @classmethod
        def new_from_file(cls, path):
            return cls(path=path)

        def get_object(self, name):
            return self.objects[name]

    gtk_module = types.SimpleNamespace(Builder=BuilderStub)
    gi_module = types.ModuleType("gi")
    gi_repository_module = types.ModuleType("gi.repository")
    gi_repository_module.Gtk = gtk_module
    gi_module.repository = gi_repository_module
    sys.modules["gi"] = gi_module
    sys.modules["gi.repository"] = gi_repository_module


class CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        install_deluge_stubs()
        install_gtk_stubs()
        purge_modules(["deluge_nofolder", "nofolder"])
        importlib.import_module("deluge_nofolder")

    def setUp(self):
        purge_modules(["deluge_nofolder", "nofolder"])

    def test_namespaced_package_imports(self):
        module = importlib.import_module("deluge_nofolder")
        self.assertEqual(module.__name__, "deluge_nofolder")

        with self.assertRaises(ModuleNotFoundError):
            importlib.import_module("nofolder")

    def test_get_resource_returns_existing_data_path(self):
        from deluge_nofolder.common import get_resource

        config_path = get_resource("config.ui")
        self.assertTrue(os.path.isabs(config_path))
        self.assertTrue(os.path.exists(config_path))
        self.assertTrue(
            config_path.endswith(
                os.path.join("deluge_nofolder", "data", "config.ui")
            )
        )
        self.assertFalse(
            os.path.exists(
                os.path.join(REPO_ROOT, "deluge_nofolder", "data", "config.glade")
            )
        )

    def test_plugin_init_classes_import_local_modules(self):
        from deluge_nofolder import CorePlugin, Gtk3UIPlugin, GtkUIPlugin, WebUIPlugin

        self.assertEqual(CorePlugin("NoFolder")._plugin_cls.__name__, "Core")
        self.assertEqual(GtkUIPlugin("NoFolder")._plugin_cls.__name__, "GtkUI")
        self.assertEqual(Gtk3UIPlugin("NoFolder")._plugin_cls.__name__, "Gtk3UI")
        self.assertEqual(WebUIPlugin("NoFolder")._plugin_cls.__name__, "WebUI")

    def test_setup_registers_namespaced_entry_points(self):
        setup_path = os.path.join(REPO_ROOT, "setup.py")
        with open(setup_path, "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn('__package_name__ = "deluge_nofolder"', content)
        self.assertIn("[deluge.plugin.core]", content)
        self.assertIn("[deluge.plugin.gtk3ui]", content)
        self.assertIn("[deluge.plugin.webui]", content)
        self.assertIn("[deluge.plugin.gtkui]", content)

    def test_default_preferences_are_safe(self):
        from deluge_nofolder.core import DEFAULT_PREFS

        self.assertEqual(
            DEFAULT_PREFS, {"dontaddfolder": False, "createfolder": False}
        )

    def test_post_torrent_add_is_noop_when_disabled(self):
        from deluge_nofolder.core import Core

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
        core.config = {"dontaddfolder": False, "createfolder": False}
        torrent = TorrentStub()
        core.torrents = {"abc123": torrent}

        core.post_torrent_add("abc123", from_state=True)

        self.assertFalse(torrent.paused)
        self.assertFalse(torrent.resumed)

    def test_post_torrent_add_handles_missing_torrent(self):
        from deluge_nofolder.core import Core

        core = Core()
        core.config = {"dontaddfolder": True, "createfolder": False}
        core.torrents = {}
        core.post_torrent_add("missing")

    def test_post_torrent_add_handles_empty_files(self):
        from deluge_nofolder.core import Core

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

    def test_gtk3_preferences_lifecycle(self):
        from deluge_nofolder import gtk3ui, gtkprefs

        class DeferredStub:
            def __init__(self, result):
                self.result = result

            def addCallback(self, callback):
                callback(self.result)

        class PluginClientStub:
            def __init__(self):
                self.saved_config = None

            def set_config(self, config):
                self.saved_config = config

            def get_config(self):
                return DeferredStub(
                    {"dontaddfolder": True, "createfolder": False}
                )

        class PreferencesStub:
            def __init__(self):
                self.added = []
                self.removed = []

            def add_page(self, name, widget):
                self.added.append((name, widget))

            def remove_page(self, name):
                self.removed.append(name)

        class PluginManagerStub:
            def __init__(self):
                self.registered = []
                self.deregistered = []

            def register_hook(self, hook, callback):
                self.registered.append((hook, callback.__name__))

            def deregister_hook(self, hook, callback):
                self.deregistered.append((hook, callback.__name__))

        plugin_client = PluginClientStub()
        gtkprefs.client = types.SimpleNamespace(deluge_nofolder=plugin_client)

        prefs = PreferencesStub()
        plugin_manager = PluginManagerStub()
        gtkprefs.component = types.SimpleNamespace(
            get=lambda name: {
                "Preferences": prefs,
                "PluginManager": plugin_manager,
            }[name]
        )

        plugin = gtk3ui.Gtk3UI()
        plugin.enable()

        self.assertEqual(prefs.added[0][0], "NoFolder")
        self.assertTrue(
            plugin.builder.loaded_files[0].endswith(
                os.path.join("deluge_nofolder", "data", "config.ui")
            )
        )
        self.assertEqual(
            {hook for hook, _ in plugin_manager.registered},
            {"on_apply_prefs", "on_show_prefs"},
        )

        plugin.on_show_prefs()
        self.assertTrue(
            plugin.builder.get_object("dontaddfolder_checkbutton").get_active()
        )
        self.assertFalse(
            plugin.builder.get_object("createfolder_checkbutton").get_active()
        )

        plugin.builder.get_object("dontaddfolder_checkbutton").set_active(False)
        plugin.builder.get_object("createfolder_checkbutton").set_active(True)
        plugin.on_apply_prefs()

        self.assertEqual(
            plugin_client.saved_config,
            {"dontaddfolder": False, "createfolder": True},
        )

        plugin.disable()
        self.assertEqual(prefs.removed, ["NoFolder"])
        self.assertEqual(
            {hook for hook, _ in plugin_manager.deregistered},
            {"on_apply_prefs", "on_show_prefs"},
        )

    def test_gtk_ui_xml_is_well_formed(self):
        from deluge_nofolder.common import get_resource

        ET.parse(get_resource("config.ui"))

    def test_web_ui_script_includes_preferences_page(self):
        from deluge_nofolder.common import get_resource

        with open(get_resource("nofolder.js"), "r", encoding="utf-8") as handle:
            content = handle.read()

        self.assertIn("NoFolderPage", content)
        self.assertIn("deluge.preferences.addPage", content)
        self.assertIn("pluginClient.get_config", content)
        self.assertIn("pluginClient.set_config", content)


if __name__ == "__main__":
    unittest.main()
