from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

env.Append(
    CPPDEFINES=[
        
    ]
)

from os.path import join

from SCons.Script import Import, SConscript

Import("env")

# Note: check if the get_package_dir can get the correct path
SConscript(
    join(env.PioPlatform().get_package_dir("framework-innetra"), "scripts",
         "platformio", "platformio-build.py"), exports="env") 

# import os
# from SCons.Script import DefaultEnvironment

# env = DefaultEnvironment()

# FRAMEWORK_DIR = env.GetProjectOption("framework-innetra")
# assert os.path.isdir(FRAMEWORK_DIR), f"Custom Innetra framework directory does not exist: {FRAMEWORK_DIR}"

# env.Append(
#     CPPPATH=[
#         os.path.join(FRAMEWORK_DIR, "include")
#     ],
#     LIBPATH=[
#         os.path.join(FRAMEWORK_DIR, "lib")
#     ],
#     CPPDEFINES=[
#         "CUSTOM_FRAMEWORK"
#     ]
# )

# # If you have any scripts in your framework, you can add them like this:
# # env.SConscript(os.path.join(FRAMEWORK_DIR, "scripts", "your_script.py"))