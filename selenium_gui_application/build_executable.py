import PyInstaller.__main__
import os
import shutil
import sys
import site # To find site-packages

def get_absolute_path(relative_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(base_dir, relative_path))

def find_pyqt5_plugin_path(plugin_name="platforms/qwindows.dll"):
    '''Attempts to find the path to a PyQt5 plugin.'''
    try:
        # Get all site-packages directories
        site_packages_dirs = site.getsitepackages()
        if site.ENABLE_USER_SITE and os.path.exists(site.getusersitepackages()):
             site_packages_dirs.append(site.getusersitepackages())

        for sp_dir in site_packages_dirs:
            # Common PyQt5 paths, Qt5 might be under PyQt5 or PyQt5/Qt5
            potential_paths = [
                os.path.join(sp_dir, "PyQt5", "Qt5", "plugins", plugin_name),
                os.path.join(sp_dir, "PyQt5", "Qt", "plugins", plugin_name), # Older structure sometimes
                os.path.join(sp_dir, "qt5_applications", "Qt", "plugins", plugin_name), # Anaconda-like
                os.path.join(sp_dir, "PyQt5", "plugins", plugin_name) # If plugins dir is directly under PyQt5
            ]
            for path_attempt in potential_paths:
                if os.path.exists(path_attempt):
                    print(f"Found PyQt5 plugin at: {path_attempt}")
                    return path_attempt
        print(f"WARNING: Could not automatically find PyQt5 plugin: {plugin_name}")
        return None
    except Exception as e:
        print(f"WARNING: Error finding PyQt5 plugin path for {plugin_name}: {e}")
        return None

APP_NAME = "element_finder_app"
SCRIPT_FILE = os.path.join("src", "gui_app.py")
SRC_DIR_PATH = get_absolute_path("src")
DARK_THEME_CSS_SOURCE = get_absolute_path(os.path.join("src", "resources", "styles", "dark_theme.css"))
DARK_THEME_CSS_DEST_IN_BUNDLE = os.path.join("resources", "styles")

script_abs_path = get_absolute_path(SCRIPT_FILE)
if not os.path.exists(script_abs_path):
    print(f"ERROR: Main script '{script_abs_path}' not found.")
    sys.exit(1)
if not os.path.exists(DARK_THEME_CSS_SOURCE):
    print(f"ERROR: CSS file '{DARK_THEME_CSS_SOURCE}' not found.")
    sys.exit(1)

print("============================================================")
print(f"{APP_NAME} - PyInstaller Builder (Updated v3 - Qt Platform Fix)")
print("============================================================")

dist_dir = get_absolute_path("dist")
build_dir = get_absolute_path("build")
spec_file_generated_name = get_absolute_path(f"{APP_NAME}.spec")

if os.path.exists(dist_dir):
    print(f"Cleaning up old '{dist_dir}' directory...")
    shutil.rmtree(dist_dir)
if os.path.exists(build_dir):
    print(f"Cleaning up old '{build_dir}' directory...")
    shutil.rmtree(build_dir)
if os.path.exists(spec_file_generated_name):
    print(f"Cleaning up old '{spec_file_generated_name}' file...")
    os.remove(spec_file_generated_name)

pyinstaller_args = [
    script_abs_path,
    '--name={}'.format(APP_NAME),
    '--onefile',
    '--console', # Keep console for debugging
    '--paths={}'.format(SRC_DIR_PATH),
    '--add-data={}{}{}'.format(DARK_THEME_CSS_SOURCE, os.pathsep, DARK_THEME_CSS_DEST_IN_BUNDLE),
]

# Add qwindows.dll
qwindows_dll_path = find_pyqt5_plugin_path("platforms/qwindows.dll")
if qwindows_dll_path:
    # PyInstaller uses ';' as path separator on Windows for --add-binary source;destination
    pyinstaller_args.append(f'--add-binary={qwindows_dll_path};platforms') 
else:
    print("CRITICAL WARNING: qwindows.dll not found. GUI will likely fail to start.")
    print("Please ensure PyQt5 is installed correctly and the path can be found.")

# Optional: Add other common plugins if needed later (imageformats, styles, etc.)
# Example for image formats:
# imageformats_dir = find_pyqt5_plugin_path("imageformats") # This would be a directory
# if imageformats_dir:
# pyinstaller_args.append(f'--add-binary={imageformats_dir};imageformats')

icon_path_win = get_absolute_path(os.path.join("src", "resources", "app.ico"))
if sys.platform.startswith('win') and os.path.exists(icon_path_win):
    pyinstaller_args.append('--icon={}'.format(icon_path_win))
else:
    if sys.platform.startswith('win'):
        print(f"Note: Windows Icon file not found at '{icon_path_win}', building without custom icon.")

print("\nRunning PyInstaller with arguments:")
for arg in pyinstaller_args:
    print(f"  {arg}")
print("\nThis may take a few minutes...\n")

try:
    PyInstaller.__main__.run(pyinstaller_args)
    print("\n============================================================")
    print("PyInstaller build process completed.")
    final_exe_path = os.path.join(dist_dir, f"{APP_NAME}.exe" if sys.platform.startswith('win') else APP_NAME)
    print(f"Executable should be in: {final_exe_path}")
    if not os.path.exists(final_exe_path):
        print(f"ERROR: Expected executable not found at {final_exe_path} after build!")
    print("============================================================")
except Exception as e:
    print("\n============================================================")
    print(f"AN ERROR OCCURRED DURING PYINSTALLER EXECUTION: {e}")
    print("============================================================")
    sys.exit(1)
else:
    final_exe_path = os.path.join(dist_dir, f"{APP_NAME}.exe" if sys.platform.startswith('win') else APP_NAME)
    if not os.path.exists(final_exe_path):
        print(f"POST-BUILD ERROR: PyInstaller reported success, but executable not found at {final_exe_path}!")
        sys.exit(1)
