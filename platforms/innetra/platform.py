import os
import sys
from platformio.public import PlatformBase

IS_WINDOWS = sys.platform.startswith("win")
class InnetraPlatform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        print("entering the Configuring default packages\n")
        if 'spine' in variables.get("pioframework", []) or 'talamo' in variables.get("pioframework", []) or 'combine' in variables.get("pioframework", []):  
            print("entering the Custom framework detected: ", self.packages, "\n")
            for p in self.packages:
                print("self.pacakges")
                if p in ['spine_tools-0.1.0-rc0']:
                    self.packages[p]['optional'] = False
                    print("spine")

        return super().configure_default_packages(variables, targets)

    def get_boards(self, id_=None):
        result = super().get_boards(id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key in result:
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        upload_protocols = board.manifest.get("upload", {}).get("protocols", [])
        if "tools" not in debug:
            debug["tools"] = {}

        # Add your custom debug tools here
        tools = ("jlink", "qemu", "renode", "ftdi")  # Add other tools as needed
        for tool in tools:
            if tool in ("qemu", "renode"):
                if not debug.get("%s_machine" % tool):
                    continue
            elif (tool not in upload_protocols or tool in debug["tools"]):
                continue
            if tool == "jlink":
                assert debug.get("jlink_device"), (
                    "Missed J-Link Device ID for %s" % board.id)
                debug["tools"][tool] = {
                    "server": {
                        "package": "tool-jlink",
                        "arguments": [
                            "-singlerun",
                            "-if", "JTAG",
                            "-select", "USB",
                            "-jtagconf", "-1,-1",
                            "-device", debug.get("jlink_device"),
                            "-port", "2331"
                        ],
                        "executable": ("JLinkGDBServerCL.exe"
                                       if IS_WINDOWS else
                                       "JLinkGDBServer")
                    },
                    "onboard": tool in debug.get("onboard_tools", [])
                }

            # Add configurations for other tools (qemu, renode, ftdi, etc.)

        board.manifest["debug"] = debug
        return board

    def configure_debug_session(self, debug_config):
        if debug_config.speed:
            server_executable = (debug_config.server or {}).get("executable", "").lower()
            if "openocd" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-c", "adapter speed %s" % debug_config.speed]
                )
            elif "jlink" in server_executable:
                debug_config.server["arguments"].extend(
                    ["-speed", debug_config.speed]
                )
 # type: ignore