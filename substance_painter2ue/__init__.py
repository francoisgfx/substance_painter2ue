"""Module to export texture to Unreal Engine."""

from .sp2ue import Painter2UE

# reference to the plugin instance
PAINTER2UE_PLUGIN = None


def start_plugin() -> None:
    """Initialize the plugin by substance painter."""
    global PAINTER2UE_PLUGIN
    PAINTER2UE_PLUGIN = Painter2UE()


def close_plugin() -> None:
    """Delete the plugin when substance painter close plugin."""
    global PAINTER2UE_PLUGIN
    del PAINTER2UE_PLUGIN


if __name__ == "__main__":
    start_plugin()
