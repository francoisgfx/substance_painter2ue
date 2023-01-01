"""Substance Painter To Unreal Engine Plugin."""
import os
import tempfile

import substance_painter.event as sp_event
import substance_painter.export as sp_export
import substance_painter.logging as sp_logging
import substance_painter.project as sp_project
import substance_painter.resource as sp_resource
import substance_painter.textureset as sp_textureset
import substance_painter.ui as sp_ui
from PySide2.QtCore import QSettings, Slot

from .sp2ue_ui import Painter2UEAction, Painter2UEWidget
from .unreal import RemoteUECommand


class Painter2UE:
    """Substance Painter To Unreal Engine Plugin."""

    def __init__(self) -> None:
        """Initialize the plugin."""
        # get plugin settings
        self.settings = QSettings("substancepainter2ue", "substancepainter2ue")
        self.set_settings()
        # create action button in 'Send To' submenu
        self.export_action = Painter2UEAction(self.send2ue)
        # create RemoteUECommand instance
        self.remote_ue = RemoteUECommand()
        # create UI
        self.window = Painter2UEWidget(self, self.remote_ue)
        sp_ui.add_dock_widget(self.window)
        # export preset
        self.selected_preset = "Unreal Engine 4 (Packed)"
        # register event callback
        sp_event.DISPATCHER.connect(sp_event.ProjectOpened, self.on_project_opened)

    @Slot()
    def send2ue(self) -> None:
        """Export textures and Send them to Unreal Engine."""
        # Verify if a project is open before trying to export something
        if not sp_project.is_open():
            return

        # Export textures based on a preset in a temp folder
        result = self.export_textures()
        sp_logging.log(
            sp_logging.DBG_INFO, "sp2ue", "Export Status: {0}".format(result.status)
        )
        if result.status != sp_export.ExportStatus.Success:
            raise Exception(result.message)
        sp_logging.info(result.message)

        # for each stack, get the list of exported textures
        for stack in result.textures.items():
            texture_set_name, stack_name = stack[0]
            texture_list = stack[1]
            sp_logging.log(
                sp_logging.DBG_INFO, "sp2ue", "Stack: {0}".format(stack_name)
            )
            sp_logging.log(
                sp_logging.DBG_INFO,
                "sp2ue",
                "Texture Set: {0}".format(texture_set_name),
            )
            sp_logging.log(
                sp_logging.DBG_INFO, "sp2ue", "Textures: {0}".format(texture_list)
            )

            # get the command to send to Unreal
            textures_cmd: list = self.get_unreal_command(texture_list)
            sp_logging.info(str(textures_cmd))
            # send the command to Unreal
            respond = self.remote_ue.run_commands(textures_cmd)
            sp_logging.info(respond)

    def export_textures(self) -> sp_export.TextureExportResult:
        """Export Texutre to temp."""
        # Get the currently active layer stack (paintable)
        stack: sp_textureset.Stack = sp_textureset.get_active_stack()

        # Get the parent Texture Set of this layer stack
        # material = stack.material()

        # Build Export Preset resource URL
        # - Context: name of the library where the resource is located
        # - Name: name of the resource (filename without extension or
        # Substance graph path)
        export_preset: sp_resource.ResourceID = sp_resource.ResourceID(
            context="starter_assets", name=self.selected_preset
        )
        sp_logging.info("Preset: {0}".format(export_preset.url()))

        # Setup the export settings
        # resolution = material.get_resolution()

        # Setup the export path, in this case the textures
        # will be put next to the spp project file on the disk
        # path: str = sp_project.file_path()
        # path = os.path.dirname(path)

        # Build the configuration
        # file:///C:/Program%20Files/Adobe/Adobe%20Substance%203D%20Painter/resources/python-doc/substance_painter/export.html#full-json-config-dict-possibilities
        config = {
            "exportShaderParams": False,
            "exportPath": self.settings.value("export_path"),
            "exportList": [{"rootPath": str(stack)}],
            "exportPresets": [{"name": "default", "maps": []}],
            "defaultExportPreset": export_preset.url(),
            "exportParameters": [{"parameters": {"paddingAlgorithm": "infinite"}}],
        }

        result: sp_export.TextureExportResult = sp_export.export_project_textures(
            config
        )

        return result

    def get_unreal_command(self, textures: list) -> list[str]:
        """Return the command to send to Unreal Engine."""
        cmd: list = []
        unreal_path = self.settings.value("unreal_content_path")

        texture_list_cmd = "texture_files = ["
        for texture in textures:
            texture_list_cmd += '"{0}",'.format(texture)
        texture_list_cmd += "]"
        cmd.append(texture_list_cmd)
        # TODO :
        # - Create material
        # - Set spp source metadata to textures
        cmd += [
            "d = unreal.AutomatedAssetImportData()",
            'd.set_editor_property("destination_path", "{}")'.format(unreal_path),
            'd.set_editor_property("filenames", texture_files)',
            "tex2Ds = unreal.AssetToolsHelpers.get_asset_tools().import_assets_automated(d)",  # noqa
        ]

        return cmd

    def set_settings(self):
        """Get Settings from env var."""
        # asset name
        asset_name = ""
        if os.environ.get("SP2UE_ASSET_NAME"):
            asset_name = os.environ.get("SP2UE_ASSET_NAME")
        elif sp_project.is_open():
            asset_name = sp_project.name()
        else:
            asset_name = ""
        self.settings.setValue("asset_name", asset_name)

        # path where to export
        export_path = ""
        if os.environ.get("SP2UE_EXPORT_PATH"):
            export_path = os.environ.get("SP2UE_EXPORT_PATH")
        elif os.environ.get("SUBSTANCE_PAINTER_TEMP_LOCATION"):
            export_path = os.environ.get("SUBSTANCE_PAINTER_TEMP_LOCATION")
        else:
            export_path = tempfile.gettempdir()
        self.settings.setValue("export_path", export_path)

        # UE content path
        unreal_content_path = ""
        if os.environ.get("SP2UE_UE_CONTENT_PATH"):
            unreal_content_path = os.environ.get("SP2UE_UE_CONTENT_PATH")
        else:
            unreal_content_path = "/Game/{asset_name}/".format(asset_name=asset_name)
        self.settings.setValue("unreal_content_path", unreal_content_path)

        # SP Export Preset
        if os.environ.get("SP2UE_PRESET"):
            self.settings.setValue("export_preset", os.environ.get("SP2UE_PRESET"))
        elif not self.settings.value("export_preset"):
            self.settings.setValue("export_preset", "Unreal Engine 4 (Packed)")

    def on_project_opened(self, e):
        """Execute when project is opened."""
        sp_logging.info("Project `{}` opened.".format(sp_project.name()))
        self.set_settings()
        self.window.update()

    def __del__(self) -> None:
        """Remove all added UI elements."""
        self.remote_ue.stop()
        sp_ui.delete_ui_element(self.window)
        sp_ui.delete_ui_element(self.export_action)
