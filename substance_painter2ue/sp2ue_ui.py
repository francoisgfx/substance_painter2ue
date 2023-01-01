"""Substance Painter To Unreal Engine UI."""
import os

import substance_painter.ui as sp_ui
from PySide2 import QtGui, QtWidgets
from PySide2.QtCore import QSettings

from .unreal import RemoteUECommand


class Painter2UEAction(QtWidgets.QAction):
    """Send To UE Action Menu."""

    def __init__(self, trigger) -> None:
        """Set action."""
        super().__init__()
        iconPath = get_icon("ue")
        self.setIcon(QtGui.QIcon(iconPath)),
        self.setText("Send To Unreal Engine")
        self.triggered.connect(trigger)

        # Add this widget to the existing File menu of the application
        sp_ui.add_action(sp_ui.ApplicationMenu.SendTo, self)

        # set shortcut
        self.setShortcut(QtGui.QKeySequence("Ctrl+Shift+u"))


class Painter2UEWidget(QtWidgets.QWidget):
    """UI for the Substance Painter to UE plugin."""

    def __init__(self, painter2ue, remote_ue: RemoteUECommand) -> None:
        """Init UI as dockable QWidget."""
        super().__init__()
        self.remote_ue = remote_ue
        self.painter2ue = painter2ue

        self.setWindowTitle("Send To Unreal Engine")
        self.settings = QSettings("substancepainter2ue", "substancepainter2ue")
        main_vlay = QtWidgets.QVBoxLayout()
        self.setLayout(main_vlay)

        # UE Nodes Selector
        ue_node_vlay = QtWidgets.QVBoxLayout()
        ue_node_vlay.addWidget(QtWidgets.QLabel("Select the Unreal Editor to send to:"))
        ue_node_hlay = QtWidgets.QHBoxLayout()
        ue_node_vlay.addLayout(ue_node_hlay)
        main_vlay.addLayout(ue_node_vlay)
        # combo box
        self.node_selector = QtWidgets.QComboBox()
        self.set_nodes_list()
        self.node_selector.activated.connect(self.on_node_change)
        ue_node_hlay.addWidget(self.node_selector)
        # refresh btn
        refresh_btn = QtWidgets.QToolButton()
        refresh_btn.clicked.connect(self.set_nodes_list())
        refresh_icon = get_icon("refresh")
        refresh_btn.setIcon(QtGui.QIcon(refresh_icon))
        ue_node_hlay.addWidget(refresh_btn)

        # Presets Selector
        preset_lay = QtWidgets.QVBoxLayout()
        preset_lay.addWidget(QtWidgets.QLabel("Select the export preset:"))
        self.preset_selector = QtWidgets.QComboBox()
        # TODO:
        # Can we get the preset list dynamically ?
        self.preset_selector.addItem("Unreal Engine 4 (Packed)")
        self.preset_selector.addItem("Unreal Engine 4 SSS (Packed)")
        self.preset_selector.activated.connect(self.on_preset_change)
        preset_lay.addWidget(self.preset_selector)
        main_vlay.addLayout(preset_lay)

        # Export Path
        export_path_lay = QtWidgets.QHBoxLayout()
        export_path_lay.addWidget(QtWidgets.QLabel("Export path:"))
        self.folder_path_edit = QtWidgets.QLineEdit()
        self.folder_path_edit.setText(self.settings.value("export_path"))
        self.folder_path_edit.textChanged.connect(self.on_path_changed)
        export_path_lay.addWidget(self.folder_path_edit)
        browse_btn = QtWidgets.QToolButton()
        browse_btn.clicked.connect(self.on_browse_clicked)
        export_path_lay.addWidget(browse_btn)
        main_vlay.addLayout(export_path_lay)

        # Asset Name
        asset_name_lay = QtWidgets.QHBoxLayout()
        asset_name_lay.addWidget(QtWidgets.QLabel("Asset Name:"))
        self.asset_name_edit = QtWidgets.QLineEdit()
        self.asset_name_edit.setText(self.settings.value("asset_name"))
        self.asset_name_edit.textChanged.connect(self.on_asset_name_changed)
        asset_name_lay.addWidget(self.asset_name_edit)
        main_vlay.addLayout(asset_name_lay)

        # UE Content Path
        ue_content_lay = QtWidgets.QHBoxLayout()
        ue_content_lay.addWidget(QtWidgets.QLabel("UE Content Path:"))
        self.ue_content_edit = QtWidgets.QLineEdit()
        self.ue_content_edit.setText(self.settings.value("unreal_content_path"))
        self.ue_content_edit.textChanged.connect(self.on_ue_content_changed)
        ue_content_lay.addWidget(self.ue_content_edit)
        main_vlay.addLayout(ue_content_lay)

        # Export
        export_btn = QtWidgets.QPushButton("Send to UE")
        ue_icon = get_icon("ue")
        export_btn.setIcon(QtGui.QIcon(ue_icon))
        export_btn.clicked.connect(painter2ue.send2ue)
        main_vlay.addWidget(export_btn)

        # Vertical Spacer
        main_vlay.addStretch()

    def set_nodes_list(self):
        """Set the list of all available Unreal Editor in combobox."""
        self.node_selector.clear()
        nodes = self.remote_ue.available_nodes()
        if len(nodes) == 0:
            self.node_selector.addItem("No Unreal found.")
        else:
            idx = 0
            for node in nodes:
                self.node_selector.addItem(
                    "Project: {0} - ({1})".format(
                        node.get("project_name"), node.get("node_id")
                    )
                )
                self.node_selector.setItemData(idx, node)
            # first node will be selected by default
            self.remote_ue.selected_node = nodes[0]

    def on_node_change(self, index):
        """Set the selected node to the RemoteUnrealCommand."""
        self.remote_ue.selected_node = self.node_selector.currentData()

    def on_preset_change(self, index):
        """Set the export preset."""
        self.painter2ue.selected_preset = self.preset_selector.currentText()

    def on_browse_clicked(self) -> None:
        """Browse folder to select export path."""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder_path:
            self.settings.setValue("export_path", folder_path)
            self.folder_path_edit.setText(folder_path)

    def on_path_changed(self, text: str) -> None:
        """Export path was changed in text edit.

        :param text: new text value
        :type text: str
        """
        self.settings.setValue("export_path", text)

    def on_asset_name_changed(self, text: str) -> None:
        """Asset Name was changed in text edit.

        :param text: new text value
        :type text: str
        """
        self.settings.setValue("asset_name", text)

    def on_ue_content_changed(self, text: str) -> None:
        """UE Content path was changed in text edit.

        :param text: new text value
        :type text: str
        """
        self.settings.setValue("unreal_content_path", text)

    def update(self) -> None:
        """Update UI."""
        self.folder_path_edit.setText(self.settings.value("export_path"))
        self.asset_name_edit.setText(self.settings.value("asset_name"))
        self.ue_content_edit.setText(self.settings.value("unreal_content_path"))


def get_icon(icon_name: str) -> str:
    """Get icon path.

    :param icon_name: filename of the icon (without extension)
    :type icon_name: str
    :return: absolute path to the icon
    :rtype: str
    """
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "icons", "{}.svg".format(icon_name)
    )
