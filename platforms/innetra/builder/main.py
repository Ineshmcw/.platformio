import sys
from platform import system
from os import makedirs
from os.path import isdir, join
import os


from SCons.Script import (ARGUMENTS, COMMAND_LINE_TARGETS, AlwaysBuild,
                          Builder, Default, DefaultEnvironment)

# Environment Setup
# Creates a default environment - env is the SCons environment object.
# Gets the platform and board configuration - platform and board_config are specific to the PlatformIO project.
env = DefaultEnvironment()
platform = env.PioPlatform()
board_config = env.BoardConfig()

    # Add your default framework logic here
HOME = os.path.expanduser("~")
FRAMEWORK_DIR = HOME + "/.platformio/packages/framework-innetra"
FRAMEWORK_DIR = env.GetProjectOption("custom_innetra_framework", default=FRAMEWORK_DIR)

print(f"FRAMEWORK_DIR: {FRAMEWORK_DIR}")

assert os.path.isdir(FRAMEWORK_DIR), f"Custom Innetra framework directory does not exist: {FRAMEWORK_DIR}"



env.Replace(
    AR="ar",
    AS="as",
    CC="gcc",
    CXX="g++",
    OBJCOPY="objcopy",
    RANLIB="ranlib",
    SIZETOOL="size",
    ARFLAGS=["rc"],
    SIZEPRINTCMD='$SIZETOOL -d $SOURCES',
    PROGSUFFIX=".elf"
)


# Note: copied directly from the sifive platform
# Allow user to override via pre:script
if env.get("PROGNAME", "program") == "program":
    env.Replace(PROGNAME="bin/t1/debug/app")


# # ElfToHex converts ELF files to Intel HEX format using objcopy.
# env.Append(
#     BUILDERS=dict(
#         ElfToHex=Builder(
#             action=env.VerboseAction(" ".join([
#                 "$OBJCOPY",
#                 "-O",
#                 "ihex",
#                 "$SOURCES",
#                 "$TARGET"
#             ]), "Building $TARGET"),
#             suffix=".hex"
#         )
#     )
# )



pioframework = env.get("PIOFRAMEWORK", [])


# Note: copied directly from the sifive platform
# if not pioframework:
#     env.SConscript("frameworks/_bare.py", exports="env")



#
# Target: Build executable and linkable firmware
#

# Note: Need to write our own platformio build pre script
# Note: need to check if the get_package_dir can get the correct path : apprenetly it doesnt work, 
# so currently i am bypassing this using the FRAMEWORK_DIR variable

if "spine" in pioframework :
    pre_build_script = os.path.join(FRAMEWORK_DIR, "scripts", "platformio", "platformio-build-pre.py")
if "talamo" in pioframework :
    pre_build_script = os.path.join(FRAMEWORK_DIR, "scripts", "platformio", "python-platformio-build-pre.py")
if "combine" in pioframework :
    pre_build_script = os.path.join(FRAMEWORK_DIR, "scripts", "platformio", "combine-platformio-build-pre.py")
print("pioframework: ", pioframework)

if "spine" in pioframework or "talamo" in pioframework or "combine" in pioframework:
    print("enter the custom framework",pre_build_script)
    env.SConscript(
        pre_build_script, 
        exports={"env": env}
    )


# Note:
# The env.BuildProgram() function call is a crucial part of the PlatformIO build process. 
# it's a method that's typically added to the SCons environment (env) by PlatformIO or custom platform.
# Its main purpose is to compile and link the project's source files into
#  an ELF (Executable and Linkable Format) file, which is the main output of our build process. 
# Stll need to understand this better about compile and link
target_elf = None
print("COMMAND_LINE_TARGETS: ", COMMAND_LINE_TARGETS)
if "nobuild" in COMMAND_LINE_TARGETS:
    target_elf = join("$BUILD_DIR", "${PROGNAME}.elf")
    target_hex = join("$BUILD_DIR", "${PROGNAME}.hex")
else:
    target_elf = env.BuildProgram() # this will call the custom build program present in the platformio-build-pre.py script
    # target_hex = env.ElfToHex(join("$BUILD_DIR", "${PROGNAME}"), target_elf)
    # env.Depends(target_hex, "checkprogsize")

# AlwaysBuild(env.Alias("nobuild", target_hex))
# target_buildprog = env.Alias("buildprog", target_hex, target_hex)


#
# Target: Print binary size
#

# target_size = env.Alias(
#     "size", target_elf,
#     env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"))
# AlwaysBuild(target_size)






#
# # Target: Upload by default .bin file
# #
# # Note: copied directly from the sifive platform and currently not used/worried about this section
# # ----------------------------------------------------------------------------------------------------------------------------------------------
# # ----------------------------------------------------------------------------------------------------------------------------------------------
# upload_protocol = env.subst("$UPLOAD_PROTOCOL")
# debug_tools = board_config.get("debug.tools", {})
# upload_actions = []
# upload_target = target_elf

# if upload_protocol.startswith("jlink"):

#     def _jlink_cmd_script(env, source):
#         build_dir = env.subst("$BUILD_DIR")
#         if not isdir(build_dir):
#             makedirs(build_dir)
#         script_path = join(build_dir, "upload.jlink")
#         commands = [
#             "h",
#             "loadfile %s" % source,
#             "r",
#             "q"
#         ]
#         with open(script_path, "w") as fp:
#             fp.write("\n".join(commands))
#         return script_path

#     env.Replace(
#         __jlink_cmd_script=_jlink_cmd_script,
#         UPLOADER="JLink.exe" if system() == "Windows" else "JLinkExe",
#         UPLOADERFLAGS=[
#             "-device", env.BoardConfig().get("debug", {}).get("jlink_device"),
#             "-speed", env.GetProjectOption("debug_speed", "4000"),
#             "-if", "JTAG",
#             "-jtagconf", "-1,-1",
#             "-autoconnect", "1",
#             "-NoGui", "1"
#         ],
#         UPLOADCMD='$UPLOADER $UPLOADERFLAGS -CommanderScript "${__jlink_cmd_script(__env__, SOURCE)}"'
#     )
#     upload_target = target_hex
#     upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

# elif upload_protocol in debug_tools:
#     if upload_protocol == "renode":
#         uploader = "renode"
#         tool_args = [arg for arg in debug_tools.get(upload_protocol).get(
#             "server").get("arguments", []) if arg != "--disable-xwt"]
#         tool_args.extend([
#             "-e", "sysbus LoadELF @$SOURCE",
#             "-e", "start"
#         ])
#     else:
#         uploader = "openocd"
#         tool_args = [
#             "-c",
#             "debug_level %d" % (2 if int(ARGUMENTS.get("PIOVERBOSE", 0)) else 1),
#             "-s", platform.get_package_dir("tool-openocd-riscv") or ""
#         ]
#         tool_args.extend(
#             debug_tools.get(upload_protocol).get("server").get("arguments", []))
#         if env.GetProjectOption("debug_speed"):
#             tool_args.extend(
#                 ["-c", "adapter_khz %s" % env.GetProjectOption("debug_speed")]
#             )
#         tool_args.extend([
#             "-c", "program {$SOURCE} %s verify; shutdown;" %
#             board_config.get("upload").get("flash_start", "")
#         ])
#     env.Replace(
#         UPLOADER=uploader,
#         UPLOADERFLAGS=tool_args,
#         UPLOADCMD="$UPLOADER $UPLOADERFLAGS"
#     )
#     upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

# # custom upload tool
# elif upload_protocol == "custom":
#     upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

# else:
#     sys.stderr.write("Warning! Unknown upload protocol %s\n" % upload_protocol)

# AlwaysBuild(env.Alias("upload", upload_target, upload_actions))

# # ----------------------------------------------------------------------------------------------------------------------------------------------
# # ----------------------------------------------------------------------------------------------------------------------------------------------


print("\n\nend of the program\n\n")


#
# Setup default targets
#

# Default([target_buildprog, target_size])







# env.Append(
#     CPPPATH=[
#         os.path.join(FRAMEWORK_DIR, "include")
#     ],
#     LIBPATH=[
#         os.path.join(FRAMEWORK_DIR, "lib"),
#         os.path.join(FRAMEWORK_DIR, "drivers"),
#         os.path.join(FRAMEWORK_DIR, "core"),
#         os.path.join(FRAMEWORK_DIR, "soc"),
#         os.path.join(FRAMEWORK_DIR, "tools"),
#         os.path.join(FRAMEWORK_DIR, "utils")
#     ],
# )


# def generate_build_command(source, target, env):
#     return f"make -C {env.subst('$PROJECT_DIR')} FRAMEWORK_DIR={FRAMEWORK_DIR}"





# env.AddPostAction(
#     target_elf,
#     env.VerboseAction(generate_build_command, "Building project")
# )

# AlwaysBuild(target_buildprog)

# Default(target_bin)