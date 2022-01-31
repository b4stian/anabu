#!/usr/bin/env python3

# ------------------------------------------------
# imports


import logging
from tkinter import Tk, filedialog, messagebox
import csv
import os

# ------------------------------------------------
# variables

# path to file
py_path = os.path.abspath(os.curdir)

# paths to look for settings files (csv)
settings_try_paths = (f"{py_path}/standard_settings.csv", "anabu/standard_settings.csv")

# property: ["name of property in csv", "default value if not found", "type of value"]
# TODO Double-check target values
settings_dict = {
    "operator": ["operator", "undefined", str],
    "sample_name": ["sample_name", "undefined", str],
    "photo_file": ["photo_file", "undefined", str],
    "target_Make": ["target_Make", None, str],
    "target_model": ["target_Model", None, str],
    "target_BrightnessValue": ["target_BrightnessValue", None, int],
    "target_ExifImageWidth": ["target_ExifImageWidth", None, int],
    "target_ExifImageHeight": ["target_ExifImageHeight", None, int],
    "target_FocalLength": ["target_FocalLength", None, float],
    "target_ExposureTime": ["target_ExposureTime", None, float],
    "target_FNumber": ["target_FNumber", None, float],
    "target_LensModel": ["target_LensModel", None, str],
    "target_ISOSpeedRatings": ["target_ISOSpeedRatings", None, int],
    "target_WhiteBalance": ["target_WhiteBalance", None, int],
    "target_MeteringMode": ["target_MeteringMode", None, int],
    "target_DigitalZoomRatio": ["target_DigitalZoomRatio", None, float],
    "target_MeteringMode": ["target_MeteringMode", None, str],
    "target_FocalLengthIn35mmFilm": ["target_FocalLengthIn35mmFilm", None, float],
    "automask": ["automask", True, bool],
    "mask_file": ["mask_file", None, str],
    "mask_correction_x": ["mask_correction_x", 0, int],
    "mask_correction_y": ["mask_correction_y", 0, int],
    "mask_rotation_clockwise": ["mask_rotation_clockwise", 0, float],
    "binarize_threshold": ["binarize_threshold", 150, int],
    "crop_masked_photo": ["crop_masked_photo", True, bool],
    "create_ppt": ["create_ppt", True, bool],
}

# ------------------------------------------------
# function/class definitions


def set_up_logging():
    """logging setup"""
    logging.basicConfig(
        handlers=[
            logging.FileHandler("log/logfile.log", mode="w"),
            logging.StreamHandler(),
        ],
        format=("%(levelname)s (%(asctime)s): %(message)s"),
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
        # force=True,
    )


def set_up_tkinter():
    """set up tkinter"""
    root = Tk()
    # hides small tkinter window
    root.withdraw()
    # make opened windows will be active above all windows
    root.attributes("-topmost", True)


class settings:
    """Object with user settings from scv file"""

    def __init__(self, filename: str, expected_settings: dict):
        """Read csv file with user settings and set them as attributes."""
        logging.info(f"Trying to read user settings from {filename}.")
        # get list of dicts from csv file
        property_list = []
        try:
            with open(filename, "r") as csvfile:
                csvreader = csv.DictReader(
                    csvfile,
                    delimiter=",",
                    skipinitialspace=True,
                    quoting=csv.QUOTE_MINIMAL,
                )
                property_list = list(csvreader)
            logging.info(f"Contents of {filename} read successfully.")
        except:
            logging.info(f"{filename} could not be opened.")
        # check if expected properties were in csv file and set them
        for num, property in enumerate(expected_settings.values()):
            corresponding_key = list(expected_settings.keys())[num]
            propertyitem = next(
                (item for item in property_list if item["property"] == property[0]),
                None,
            )
            if propertyitem:
                if propertyitem["value"] in ["None", "", '""', "''", "-", "---"]:
                    setattr(self, corresponding_key, None)
                    logging.info(
                        f'Setting for "{property[0]}" found. Value set to "{None}".'
                    )
                else:
                    # set datatype
                    try:
                        attr_type = property[2](propertyitem["value"])
                        setattr(self, corresponding_key, attr_type)
                        logging.info(
                            f"Setting for \"{property[0]}\" found. Value set to \"{propertyitem['value']}\"."
                        )
                    except:
                        setattr(self, corresponding_key, property[1])
                        logging.warning(
                            f"Setting for \"{property[0]}\" found: \"{propertyitem['value']}\",\n"
                            f'\tbut could not be converted to expected type "{property[2]}". Setting to default value of "{property[1]}".'
                        )
            else:
                setattr(self, corresponding_key, property[1])
                logging.warning(
                    f'Setting for "{property[0]}" expected but not found. Setting to default value of "{property[1]}".'
                )
        logging.info(f"All user settings read from {filename}.")


def set_settings_path(*paths):
    """Returns the path for the settings file. First by trying arguments, then by opening file dialog."""
    logging.info("Trying to set the path to the settings file.")
    for path in paths:
        try:
            csvfile = open(path, "r")
            csvfile.close()
            logging.info(f'File found: "{path}".')
            return path
        except:
            logging.info(f'Could not find "{path}".')
    logging.info("Trying to select correct csv file with settings via file dialog.")
    dialog_path = filedialog.askopenfilename(
        filetypes=[("CSV files", ".csv")],
        title="Select file containing the settings",
    )
    try:
        csvfile = open(dialog_path, "r")
        csvfile.close()
        logging.info(f'Selected file with dialog: "{dialog_path}".')
        return dialog_path
    except:
        logging.exception(
            "Correct csv file with settings not defined via dialog. Exiting."
        )
        raise Exception(
            "Correct csv file with settings not defined via dialog. Exiting."
        )


def run_interface() -> None:
    """Execute the interface functions."""
    # set_up_logging() needs to be executed individually at the very start
    set_up_tkinter()
    settings_path = set_settings_path(*settings_try_paths)
    user_settings = settings(settings_path, settings_dict)


# ------------------------------------------------
# executions

# This construction is needed so that python.el doesn't ignore it.
is_main = __name__ == "__main__"

if is_main:
    set_up_logging()
    run_interface()
