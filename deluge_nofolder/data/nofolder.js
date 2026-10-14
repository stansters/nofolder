/*
Script: nofolder.js
    The client-side javascript code for the NoFolder plugin.

Copyright:
    (C) KennyWuLee 2009 <krischer.till@gmail.com>
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, write to:
        The Free Software Foundation, Inc.,
        51 Franklin Street, Fifth Floor
        Boston, MA  02110-1301, USA.

    In addition, as a special exception, the copyright holders give
    permission to link the code of portions of this program with the OpenSSL
    library.
    You must obey the GNU General Public License in all respects for all of
    the code used other than OpenSSL. If you modify file(s) with this
    exception, you may extend this exception to your version of the file(s),
    but you are not obligated to do so. If you do not wish to do so, delete
    this exception statement from your version. If you delete this exception
    statement from all source files in the program, then also delete it here.
*/

Ext.ns('Deluge.ux.preferences');

Deluge.ux.preferences.NoFolderPage = Ext.extend(Ext.form.FormPanel, {
    title: _('NoFolder'),
    border: false,
    bodyStyle: 'padding: 10px',
    defaults: {
        xtype: 'checkbox',
        labelSeparator: '',
    },

    initComponent: function () {
        Deluge.ux.preferences.NoFolderPage.superclass.initComponent.call(this);
        this.add({
            name: 'dontaddfolder',
            boxLabel: _("Don't add torrentname to path"),
        });
        this.add({
            name: 'createfolder',
            boxLabel: _('Create folder for single files'),
        });
        this.on('show', this.onPreferencesShow, this);
    },

    getPluginClient: function () {
        return deluge.client.nofolder || deluge.client.deluge_nofolder;
    },

    onPreferencesShow: function () {
        var pluginClient = this.getPluginClient();
        if (!pluginClient || !pluginClient.get_config) {
            return;
        }
        pluginClient.get_config({
            success: function (config) {
                this.getForm().setValues({
                    dontaddfolder: !!config.dontaddfolder,
                    createfolder: !!config.createfolder,
                });
            },
            scope: this,
        });
    },

    onApply: function () {
        var pluginClient = this.getPluginClient();
        if (!pluginClient || !pluginClient.set_config) {
            return;
        }
        var form = this.getForm();
        pluginClient.set_config({
            dontaddfolder: form.findField('dontaddfolder').checked,
            createfolder: form.findField('createfolder').checked,
        });
    },
});

Deluge.plugins.NoFolderPlugin = Ext.extend(Deluge.Plugin, {
    name: 'NoFolder',

    onDisable: function () {
        deluge.preferences.un('apply', this.onApply, this);
        deluge.preferences.removePage(this.prefsPage);
    },

    onEnable: function () {
        this.prefsPage = deluge.preferences.addPage(
            new Deluge.ux.preferences.NoFolderPage()
        );
        deluge.preferences.on('apply', this.onApply, this);
    },

    onApply: function () {
        if (this.prefsPage) {
            this.prefsPage.onApply();
        }
    },
});

Deluge.registerPlugin('NoFolder', Deluge.plugins.NoFolderPlugin);
