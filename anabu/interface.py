#!/usr/bin/env python3

# ------------------------------------------------
# TODO
#
# - Add __repr__ to classes.
# - Add option to specify folder or saving results
# - Add possibility to specify folder and image type for batch evaluation

# This construction is needed so that python.el doesn't ignore it.
is_main = __name__ == "__main__"

# ------------------------------------------------
# imports

import csv
from datetime import datetime
import logging
import os
from tkinter import Tk, filedialog, messagebox  # FIXME messagebox needed in this file?
from shutil import copy2

# ------------------------------------------------
# variables

# date string for filenames
date_string = (
    str(datetime.now().year)
    + "-"
    + str(datetime.now().month)
    + "-"
    + str(datetime.now().day)
    + "_"
)

# path to this file
py_path = os.path.abspath(os.curdir)

# paths to look for settings files (csv)
settings_try_paths = (f"{py_path}/standard_settings.csv", "anabu/standard_settings.csv")

# property: ["name of property in csv", "default value if not found", "type of value", "explanation of variable"]
# TODO Double-check target values
settings_dict = {
    "operator": {
        "variable": "operator",
        "default_value": "undefined",
        "type": str,
        "parameter": "operator who conducted the analysis",
    },
    "sample_name": {
        "variable": "sample_name",
        "default_value": "undefined",
        "type": str,
        "parameter": "name of the analyzed sample",
    },
    "photo_file": {
        "variable": "photo_file",
        "default_value": "undefined",
        "type": str,
        "parameter": "path to the photo file (open dialog if not found)",
    },
    "target_Make": {
        "variable": "target_Make",
        "default_value": None,
        "type": str,
        "parameter": "requirement for camera maker",
    },
    "target_model": {
        "variable": "target_Model",
        "default_value": None,
        "type": str,
        "parameter": "requirement for camera model",
    },
    "target_BrightnessValue": {
        "variable": "target_BrightnessValue",
        "default_value": None,
        "type": int,
        "parameter": "requirement for brightness value of photo",
    },
    "target_ExifImageWidth": {
        "variable": "target_ExifImageWidth",
        "default_value": None,
        "type": int,
        "parameter": "requirement for photo width in pixels",
    },
    "target_ExifImageHeight": {
        "variable": "target_ExifImageHeight",
        "default_value": None,
        "type": int,
        "parameter": "requirement for photo height in pixels",
    },
    "target_FocalLength": {
        "variable": "target_FocalLength",
        "default_value": None,
        "type": float,
        "parameter": "requirement for focal length",
    },
    "target_ExposureTime": {
        "variable": "target_ExposureTime",
        "default_value": None,
        "type": float,
        "parameter": "requirement for exposure time",
    },
    "target_FNumber": {
        "variable": "target_FNumber",
        "default_value": None,
        "type": float,
        "parameter": "requirement for f number",
    },
    "target_LensModel": {
        "variable": "target_LensModel",
        "default_value": None,
        "type": str,
        "parameter": "requirement for lens model",
    },
    "target_ISOSpeedRatings": {
        "variable": "target_ISOSpeedRatings",
        "default_value": None,
        "type": int,
        "parameter": "rquirement for ISO value",
    },
    "target_WhiteBalance": {
        "variable": "target_WhiteBalance",
        "default_value": None,
        "type": int,
        "parameter": "requirement for white balance",
    },
    "target_MeteringMode": {
        "variable": "target_MeteringMode",
        "default_value": None,
        "type": int,
        "parameter": "requirement for metering mode",
    },
    "target_DigitalZoomRatio": {
        "variable": "target_DigitalZoomRatio",
        "default_value": None,
        "type": float,
        "parameter": "requirement for digital zoom ratio",
    },
    "target_FocalLengthIn35mmFilm": {
        "variable": "target_FocalLengthIn35mmFilm",
        "default_value": None,
        "type": float,
        "parameter": "requirement for focal length equivalent for 35 mm film",
    },
    "automask": {
        "variable": "automask",
        "default_value": True,
        "type": bool,
        "parameter": "use automask",
    },
    "mask_file": {
        "variable": "mask_file",
        "default_value": None,
        "type": str,
        "parameter": "path to mask file (open dialog if not found)",
    },
    "mask_correction_x": {
        "variable": "mask_correction_x",
        "default_value": 0,
        "type": int,
        "parameter": "correction for horizontal mask position in pixels",
    },
    "mask_correction_y": {
        "variable": "mask_correction_y",
        "default_value": 0,
        "type": int,
        "parameter": "correction for vertical mask position in pixels",
    },
    "mask_rotation_clockwise": {
        "variable": "mask_rotation_clockwise",
        "default_value": 0,
        "type": float,
        "parameter": "correction for rotation of mask file in degrees",
    },
    "binarize_threshold": {
        "variable": "binarize_threshold",
        "default_value": 150,
        "type": int,
        "parameter": "threshold for photo binarization (0-254)",
    },
    "crop_masked_photo": {
        "variable": "crop_masked_photo",
        "default_value": True,
        "type": bool,
        "parameter": "auto-crop photo to non-masked area?",
    },
    "create_ppt": {
        "variable": "create_ppt",
        "default_value": True,
        "type": bool,
        "parameter": "auto-create pptx file with results?",
    },
}

# ------------------------------------------------
# function/class definitions


def set_up_logging() -> None:
    """logging setup"""
    log_filename = "log/logfile.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    logging.basicConfig(
        handlers=[
            logging.FileHandler(log_filename, mode="w"),
            logging.StreamHandler(), # to print to terminal
        ],
        format=("%(levelname)s (%(asctime)s): %(message)s"),
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
        # force=True,
    )


def set_up_tkinter() -> None:
    """set up tkinter"""
    root = Tk()
    # hides small tkinter window
    root.withdraw()
    # make opened windows will be active above all windows
    root.attributes("-topmost", True)


class Results:
    """Object to store and export all results."""

    def __init__(self) -> None:
        """
        Initializes an empty object to save all results as attributes with dictionaries as the values.
        The attribute "attribute_list" holds all set results.
        """
        self.attribute_list = []

    def add_result(self, variable: str, parameter: str, value) -> None:
        """Adds results entries (3-item lists) to attribute 'results_data'."""
        if type("variable") == str and type("parameter") == str:
            setattr(
                self,
                variable,
                {"variable": variable, "parameter": parameter, "value": value},
            )
            self.__dict__["attribute_list"].append(variable)
        else:
            logging.warning(
                f'The first two parameters "variable" and "parameter" need to be strings.\n'
                f"Could not add result."
            )

    def settings_to_results(self, settings) -> None:
        """Saves the currently set settings to results object (for documentation)."""
        try:
            for attribute in settings.__dict__["attribute_list"]:
                self.add_result(
                    settings.__dict__[attribute]["variable"],
                    "user settings: " + settings.__dict__[attribute]["parameter"],
                    settings.__dict__[attribute]["value"],
                )
            logging.info(f"All settings added to results.")
        except:
                logging.warning(f"Settings could not be added to results.")

    def export_csv(self, path:str) -> None:
        """Saves a CSV file with all results."""
        csv_header = ["variable", "parameter", "value"]
        with open(path, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(csv_header)
            for attribute in self.__dict__["attribute_list"]:
                writer.writerow(
                    [
                        self.__dict__[attribute]["variable"],
                        self.__dict__[attribute]["parameter"],
                        self.__dict__[attribute]["value"]
                        if self.__dict__[attribute]["value"]
                        else "not set",
                    ]
                )
        logging.info(f'CSV file with results saved: "{path}".')


class Settings:
    """Object with user settings from csv file"""

    def __init__(self, filename: str, expected_settings: dict) -> None:
        """Read csv file with user settings and set them as attributes."""
        logging.info(f"Trying to read user settings from {filename}.")
        # This list holds the set attributes.
        self.attribute_list = []
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
                (
                    item
                    for item in property_list
                    if item["property"] == property["variable"]
                ),
                None,
            )
            if propertyitem:
                if propertyitem["value"] in ["None", "", '""', "''", "-", "---"]:
                    self.set_sett_attribute(
                        corresponding_key,
                        {
                            "variable": property["variable"],
                            "parameter": property["parameter"],
                            "value": None,
                        },
                    )
                    logging.info(
                        f'Setting for "{property["variable"]}" found. Value set to "{None}".'
                    )
                else:
                    # set datatype
                    try:
                        attr_type = property["type"](propertyitem["value"])
                        self.set_sett_attribute(
                            corresponding_key,
                            {
                                "variable": property["variable"],
                                "parameter": property["parameter"],
                                "value": attr_type,
                            },
                        )
                        logging.info(
                            f'Setting for "{property["variable"]}" found. '
                            f"Value set to \"{propertyitem['value']}\"."
                        )
                    except:
                        self.set_sett_attribute(
                            corresponding_key,
                            {
                                "variable": property["variable"],
                                "parameter": property["parameter"],
                                "value": property["default_value"],
                            },
                        )
                        logging.warning(
                            f"Setting for \"{property['variable']}\" found: \"{propertyitem['value']}\",\n"
                            f'\tbut could not be converted to expected type "{property["type"]}". '
                            f'Setting to default value of "{property["default_value"]}".'
                        )
            else:
                self.set_sett_attribute(
                    corresponding_key,
                    {
                        "variable": property["variable"],
                        "parameter": property["parameter"],
                        "value": property["default_value"],
                    },
                )
                logging.warning(
                    f'Setting for "{property["variable"]}" expected but not found. Setting to default value of "{property["default_value"]}".'
                )
        logging.info(f"All user settings read from {filename}.")

    def set_sett_attribute(self, attribute: str, value: dict) -> None:
        """
        Sets a setting as an attribute of the object
        and adds to list of attributes "attribute_list".
        """
        setattr(self, attribute, value)
        self.__dict__["attribute_list"].append(attribute)

    @staticmethod
    def set_settings_path(*paths) -> None:
        """
        Returns the path for the settings file.
        First by trying arguments, then by opening file dialog.
        """
        logging.info("Trying to set the path to the settings file.")
        for path in paths:
            try:
                csvfile = open(path, "r")
                csvfile.close()
                logging.info(f'File found: "{path}".')
                return path
            except FileNotFoundError:
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
        except Exception:
            logging.exception(
                "Correct csv file with settings not defined via dialog. Exiting."
            )
            raise Exception(
                "Correct csv file with settings not defined via dialog. Exiting."
            )

    @staticmethod
    def create_default_settings_csv(expected_settings: dict, path: str) -> None:
        """Creates a csv file with default settings for the user to modify."""
        csv_header = ["property", "value", "explanation"]
        with open(path, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC, delimiter=",")
            writer.writerow(csv_header)
            for entry in expected_settings.values():
                writer.writerow(
                    [entry["variable"], entry["default_value"], entry["parameter"]]
                )
        logging.info(f'CSV file with default values created: "{path}".')


def get_folder(path: str) -> str:
    """Returns path stripped of the file extension."""
    return os.path.splitext(path)[0]


# FIXME finalize/test function
def end_analysis(path:str) -> None:
    """Function to be called at the end. Copies logfile to path."""
    logging.info("----------------------------------")
    logging.info("Evaluation completed successfully!")
    logging.info("----------------------------------")
    copy2("log/logfile.log", path)


def run_interface() -> None:
    """Execute the interface functions."""
    # set_up_logging() needs to be executed individually at the very start
    set_up_tkinter()
    results_list = Results()
    settings_path = Settings.set_settings_path(*settings_try_paths)
    user_settings = Settings(settings_path, settings_dict)
    results_list.settings_to_results(user_settings)


# ------------------------------------------------
# executions

set_up_logging()
run_interface()

if is_main:
    pass
