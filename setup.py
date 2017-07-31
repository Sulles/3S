from cx_Freeze import setup, Executable

additional_mods = ['numpy.core._methods', 'numpy.lib.format']
setup(name='3S',
      version='0.1',
      description='Solar System Simulator',
      options = {'build_exe': {'includes':additional_mods}},
      executables = [Executable("Main.py")])
