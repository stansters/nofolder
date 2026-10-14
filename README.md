# nofolder
Deluge 2.x plugin

This plugin has two functionalities:

- "don't add torrent name to path":
This is similar to the feature in rutorrent. It does not create a folder for torrents with multiple files, but puts them all into the Download folder. (unfortunately this causes the name of the torrent to get messed up in the torrent list.)

- "create folder for single files":
This is basically the opposite of the first feature. It forces deluge to create a folder with the same name as the torrent, even for torrents with just one file in them.

download from:

https://github.com/stansters/nofolder/releases

## Deluge 2.x usage

This fork targets Deluge 2.x on Python 3.

### Build and install

Build the plugin egg:

`python3 setup.py bdist_egg`

The built egg is created in `dist/`. Copy the `.egg` file into your Deluge plugin directory and restart Deluge.

### Enable and configure

1. Enable **NoFolder** in Deluge Plugins.
2. In the GTK desktop client, open **Preferences -> Plugins -> NoFolder**.
3. Configure:
   - **Don't add torrentname to path** (`dontaddfolder`)
   - **Create folder for single files** (`createfolder`)

Safe defaults are enabled for Deluge 2.x compatibility: both options are `False` until you explicitly turn them on.

### Web UI

The web plugin now provides a **NoFolder** preferences page integrated into Deluge Web preferences for the same two settings.

# forum
http://forum.deluge-torrent.org/viewtopic.php?f=9&t=51839
