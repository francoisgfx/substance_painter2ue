"""
Unreal Engine Communication functions.

borrowed from Epic Game BlenderTools
https://github.com/EpicGames/BlenderTools/tree/main/send2ue
"""
import time

from .remote_execution import RemoteExecution


class RemoteUECommand:
    """Send python command to UE through network."""

    def __init__(self) -> None:
        """Init RemoteUECommand."""
        # start a connection to the engine that lets you send python-commands.md strings
        self.remote_exec: RemoteExecution = RemoteExecution()
        self.remote_exec.start()
        self.unreal_response: str = ""
        time.sleep(1.5)  # wait a few secondes to let it find some nodes.
        nodes: list = self.available_nodes()
        self.selected_node: dict = nodes[0] if len(nodes) > 0 else {}

    def run_commands(self, commands: list[str]) -> str:
        """
        Run a list of python commands and returns the result of the output.

        :param list commands: A formatted string of python commands that will be run
                            by unreal engine.
        :return str: The stdout produced by the remote python command.
        """
        # wrap the commands in a try except so that all exceptions can be logged
        # in the output
        commands = (
            ["try:"]
            + self._add_indent(commands, "\t")
            + ["except Exception as error:", "\tprint(error)"]
        )

        # send over the python code as a string and run it
        self._run_unreal_python_commands(commands)

        return self._get_response()

    def _get_response(self) -> str:
        """
        Get the stdout produced by the remote python call.

        :return str: The stdout produced by the remote python command.
        """
        if self._unreal_response:
            full_output = []
            output = self._unreal_response.get("output")
            if output:
                full_output.append(
                    "\n".join(
                        [line["output"] for line in output if line["type"] != "Warning"]
                    )
                )

            result = self._unreal_response.get("result")
            if result != "None":
                full_output.append(result)

            return "\n".join(full_output)
        return ""

    def _add_indent(self, commands: list[str], indent: str) -> list[str]:
        """
        Add an indent to the list of python commands.

        :param list commands: A list of python commands that will be run
                              by unreal engine.
        :param str indent: A str of tab characters.
        :return str: A list of python commands that will be run by unreal engine.
        """
        indented_line: list = []
        for command in commands:
            for line in command.split("\n"):
                indented_line.append(f"{indent}{line}")

        return indented_line

    def _run_unreal_python_commands(
        self,
        commands: list[str],
        failed_connection_attempts: int = 0,
    ) -> None:
        """
        Send python commands to the first found Unreal Editor.

        :param list commands: A list of python commands that will be run
                                by unreal engine.
        :param int failed_connection_attempts: A counter that keeps track of how many
                                            times an editor connection attempt was made.
        """
        try:

            # create first connection
            if not self.remote_exec.has_command_connection():
                time.sleep(0.2)
                if not self.selected_node:
                    if len(self.remote_exec.available_nodes) > 0:
                        self.selected_node = self.remote_exec.available_nodes[0]
                    else:
                        raise ConnectionError(
                            "Could not find an open Unreal Editor instance!"
                        )
                self.remote_exec.open_command_connection(
                    self.selected_node.get("node_id")
                )

            # if a connection is made
            if self.remote_exec.has_command_connection():
                # run the import commands and save the response in unreal_response
                cmd_str = "\n".join(commands).replace("\\", "/")
                self._unreal_response = self.remote_exec.run_command(
                    cmd_str, unattended=False
                )

            # otherwise make an other attempt to connect to the engine
            else:
                if failed_connection_attempts < 50:
                    self._run_unreal_python_commands(
                        commands, failed_connection_attempts + 1
                    )
                else:
                    raise ConnectionError(
                        "Could not find an open Unreal Editor instance!"
                    )

        # catch all errors
        except Exception:
            raise ConnectionError("Could not find an open Unreal Editor instance!")

    def stop(self) -> None:
        """Stop remote connection."""
        self.remote_exec.stop()

    def available_nodes(self) -> list:
        """Get the list of found Unreal instances."""
        return self.remote_exec.remote_nodes
