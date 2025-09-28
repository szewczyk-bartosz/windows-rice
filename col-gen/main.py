import sys
import winreg
import os
import pywal
import shutil
from pathlib import Path
import ctypes
import argparse
import builtins
from string import Template

original_print = builtins.print

def printWithExtraEndline(*args, **kwargs):
    original_print(*args, **kwargs, end=kwargs.get("end", "\n") + "\n")

builtins.print = printWithExtraEndline


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TODO: write desc")

    parser.add_argument("image_path", type=str, help="Path to image used to generate the colour scheme")

    parser.add_argument("--add_center", action="store_true")
    parser.add_argument("--solid_bar", action="store_true")
    parser.add_argument("--skip_wallpaper", action="store_true")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = ".glzr"
    home_dir = os.path.expanduser("~")
    conf_dir = os.path.join(home_dir, target_dir)
    glazewm_config_dir = os.path.join(conf_dir, "glazewm")
    zebar_config_dir = os.path.join(conf_dir, "zebar")


    # Create a backup of the config
    backup_dir = os.path.join(home_dir, ".bsbarbackup")

    if os.path.exists(backup_dir):
        print("Removing previous backup...\n")
        shutil.rmtree(backup_dir)
    
    print("New backup created\n")
    shutil.copytree(conf_dir, backup_dir)

    # Select subfolder for the config files
    # By default, we get a no center non-solid bar
    # The solidness of the bar needs to be changed in the style (UNIMPLEMENTED)
    templates_dir = os.path.join(script_dir, "templates")
    glazewm_dir = os.path.join(templates_dir, "glazewm")
    zebar_dir = os.path.join(templates_dir, "zebar")
    subfolder_dir = os.path.join(zebar_dir, "nocenter")
    if args.add_center:
        print("Adding center")
        subfolder_dir = os.path.join(zebar_dir, "full")
    if args.solid_bar:
        print("Unimplemented...")
        exit(-2)

    if os.path.exists(subfolder_dir):
        print("Config subdir found at", subfolder_dir)
        zebar_settings = os.path.join(subfolder_dir, "settings.json")
        zebar_json = os.path.join(subfolder_dir, "bsBar.zebar.json")
        zebar_html = os.path.join(subfolder_dir, "bsBar.html")
        zebar_styles = os.path.join(zebar_dir, "styles.css")
        zebar_normal = os.path.join(zebar_dir, "normalize.css")
        
        
        print("Checking availability of config files...")
        print(f"settings: {os.path.exists(zebar_settings)}")
        print(f"zebarjson: {os.path.exists(zebar_json)}")
        print(f"html: {os.path.exists(zebar_html)}")
        print(f"styles: {os.path.exists(zebar_styles)}")
        print(f"normalisation: {os.path.exists(zebar_normal)}")
    else:
        print("Config subdir not found, exitting...")
        exit(-1)

    # Generate colour palette

    imgpath = pywal.image.get(args.image_path)
    pywal_output = pywal.colors.get(imgpath)
    palette = pywal_output["colors"]
    print(palette)

    # Populate colors dictionary
    colors = {
        "window_border": '"' + palette["color11"] + '"',
        "bar_subsection": palette["color10"] + ";",
        "active_workspace_bg": palette["color5"] + ";",
        "inactive_workspace_bg": palette["color11"] + ";",
        "active_workspace_border": palette["color7"] + ";",
        "inactive_workspace_border": palette["color7"] + ";",
        "text_color": palette["color7"] + ";",
        "color7": palette["color7"],
        "color8": palette["color8"],
        "color9": palette["color9"],
        "color10": palette["color10"],
        "color1": palette["color1"],
        "color15": palette["color15"]
    }

    # Set up the temp directory
    
    tmp_dir = os.path.join(script_dir, ".tmp")

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    
    os.makedirs(tmp_dir)
    os.makedirs(os.path.join(tmp_dir, "glazewm"))
    os.makedirs(os.path.join(tmp_dir, "zebar"))
    os.makedirs(os.path.join(tmp_dir, "zebar", "starter"))

    # Populate temp directory

    # GlazeWM
    with open(os.path.join(glazewm_dir, "config.yaml"), "r") as file:
        template = Template(file.read())
    
    glazeConfigReady = template.safe_substitute(colors)

    with open(os.path.join(tmp_dir, "glazewm", "config.yaml"), "w") as file:
              file.write(glazeConfigReady)

    # Zebar
    # Only 1 file requires substitution, the styles.css
    with open(zebar_styles, "r") as file:
         template = Template(file.read())
    
    zebarStylesReady = template.safe_substitute(colors)

    tmpzebarbase = os.path.join(tmp_dir, "zebar")
    tmpzebarstarter = os.path.join(tmpzebarbase, "starter")
    with open(os.path.join(tmpzebarstarter, "styles.css"), "w") as file:
         file.write(zebarStylesReady)
    
    shutil.copy(zebar_normal, tmpzebarstarter)
    shutil.copy(zebar_settings, tmpzebarbase)

    shutil.copy(zebar_json, tmpzebarstarter)
    shutil.copy(zebar_html, tmpzebarstarter)


    # Flow only does not need to go into tmp
    roaming_dir = os.getenv("APPDATA")
    flowThemePath = os.path.join(roaming_dir, "FlowLauncher", "Themes")
    themeName = "bsTheme.xaml"

    flowThemeTemplate = os.path.join(script_dir, "templates", "bsTheme.xaml")

    with open(flowThemeTemplate, "r") as file:
         template = Template(file.read())
    
    readyFlowStyle = template.safe_substitute(colors)

    with open(os.path.join(flowThemePath, themeName), "w") as file:
         file.write(readyFlowStyle)






    if not args.skip_wallpaper:
        # set wallpaper
        ctypes.windll.user32.SystemParametersInfoW(20, 0, imgpath, 3)
        reg_key = r"Control Panel\Desktop"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_SET_VALUE) as key:
             winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, imgpath)
    


    if os.path.exists(conf_dir):
         shutil.rmtree(conf_dir)
         print("deleted old config")
    
    shutil.copytree(tmp_dir, conf_dir)
    print("populated config")

    #shutil.rmtree(tmp_dir)
    #print("removed temporary")
