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
