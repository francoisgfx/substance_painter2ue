# Substance Painter To Unreal Engine.

A substance Painter plugin which export textures and automatically import them into an 
opened Unreal Editor project. 
It created a connection between SP and UE and sends command to UE to import the textures.

## Installation
- Download the folder substance_painter2ue
- Put the folder in your substance painter plugin folder. It could be one of followings:
    - C:\Users\username\Documents\Adobe\Adobe Substance 3D Painter\plugins
    - path defined by the environement variable 'SUBSTANCE_PAINTER_PLUGINS_PATH'
- Start Substance Painter
- In the Python Menu, check "substance_painter2ue

## Usage
- Open Unreal Engine with the project where you want to import the textures.
- Open Substance Painter, and open your project
- Go to File > Send To > Send To Unreal Engine
(by default, it will send textures to the first unreal editor instance it found on your
computer.)

### Options
In Substance Painter, go to Window > Views > Send To Unreal Engine (a panel will open).

The first combobox let you select the Unreal Editor to send the texture to (in case you 
have more than one Unreal open). It displays the name of the Unreal project, and the ID to
connect to.

The second combobox let you select which export presets to use. Those are hardcoded for now.

'Export path' defines where the texture will be exported on disc before being imported in UE.
This could be any temporary folder. 

'Asset Name' is not use for now.

'UE Content Path' defines where to import the textures in Unreal Content directory. 
Where /Game/ means the 'Content' folder in the Unreal project. You want to always import
the texture in the same folder for your preview to update automatically. 

### Shortcut
You can use Ctrl+Shift+U to do the export.

## Environement Variables
The plugin could be configure through environement variables. 

| Environment Var| Description |
|--|--|
| SP2UE_ASSET_NAME | Name of the current asset |
| SP2UE_EXPORT_PATH| Path where to temporary export textures on disc. If it is not define it will look for SUBSTANCE_PAINTER_TEMP_LOCATION. If neither are defined it will use a temp folder. |
| SP2UE_UE_CONTENT_PATH| Path in the Unreal Content Directory. (ie /Game/ is the content directory) |
| SP2UE_PRESET| Defines the export preset name (not used yet) |

## TODO
- Generate material if it doesn't exists
- Set the spp path to the textures' metadatas in UE (to retrieve original file)
- Better UI
- Getting Output Preset export from python if possible ?
- Using SP2UE_PRESET