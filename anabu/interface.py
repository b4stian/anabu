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

try:
    import analysis
    import photo
except:
    from anabu import analysis
    from anabu import photo

import csv
import glob
import logging
import os
import sys
from collections.abc import Generator, Iterable
from datetime import datetime
from shutil import copy2

import PySimpleGUI as sg

# ------------------------------------------------
# variables

# version number of anabu
VERSION = "1.1"

# activate GUI
GUI = True

# ignore settings csv file
IGNORE_SETTINGS_FILE = False

# date string for filenames
date_string = (
    str(datetime.now().year)
    + "-"
    + str(datetime.now().month)
    + "-"
    + str(datetime.now().day)
    + "_"
)

# filename for log
log_file = "log/logfile.log"

# path to this file
py_path = os.path.abspath(os.curdir)

# paths to look for settings files (csv)
settings_try_paths = (f"{py_path}/standard_settings.csv", "anabu/standard_settings.csv")

# files to ignore in batch evaluation
files_ignore = {
    "_automask",
    "_binarized",
    "_binary_mask",
    "_circle_numbers",
    "_circled",
    "_cropped_mask",
    "_cropped_photo",
    "_holes",
    "_labels",
    "_masked_cropped",
    "_maskedrg",
    "_maskview",
    "_pinholes",
    "_pinholes_resized",
    "_scale_axes",
    "_distribution_plot",
    "_cropped_scaled_photo",
}

# property: ["name of property in csv", "default value if not found", "type of value", "explanation of variable"]
# TODO Double-check target values
settings_dict = {
    "operator": {
        "variable": "operator",
        "default_value": "undefined operator",
        "type": str,
        "parameter": "operator who conducted the analysis",
    },
    "sample_name": {
        "variable": "sample_name",
        "default_value": None,
        "type": str,
        "parameter": "name of the analyzed sample (not for batch)",
    },
    "photo_file": {
        "variable": "photo_file",
        "default_value": None,
        "type": str,
        "parameter": "path to the photo file (open dialog if not found)",
    },
    "batch_evaluation": {
        "variable": "batch_evaluation",
        "default_value": False,
        "type": bool,
        "parameter": "batch evaluate all photos in photo_folder",
    },
    "photo_folder": {
        "variable": "photo_folder",
        "default_value": None,
        "type": str,
        "parameter": "folder for batch batch evaluation",
    },
    "target_Make": {
        "variable": "target_Make",
        "default_value": "SONY",
        "type": str,
        "parameter": "requirement for camera maker",
    },
    "target_Model": {
        "variable": "target_Model",
        "default_value": "ILCE-7M2",
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
        "default_value": 6000,
        "type": int,
        "parameter": "requirement for photo width in pixels",
    },
    "target_ExifImageHeight": {
        "variable": "target_ExifImageHeight",
        "default_value": 4000,
        "type": int,
        "parameter": "requirement for photo height in pixels",
    },
    "target_FocalLength": {
        "variable": "target_FocalLength",
        "default_value": 28.0,
        "type": float,
        "parameter": "requirement for focal length",
    },
    "target_ExposureTime": {
        "variable": "target_ExposureTime",
        "default_value": 30.0,
        "type": float,
        "parameter": "requirement for exposure time",
    },
    "target_FNumber": {
        "variable": "target_FNumber",
        "default_value": 5.6,
        "type": float,
        "parameter": "requirement for f number",
    },
    "target_LensModel": {
        "variable": "target_LensModel",
        "default_value": "FE 28mm F2",
        "type": str,
        "parameter": "requirement for lens model",
    },
    "target_ISOSpeedRatings": {
        "variable": "target_ISOSpeedRatings",
        "default_value": 100,
        "type": int,
        "parameter": "requirement for ISO value",
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
    "flip": {
        "variable": "flip",
        "default_value": False,
        "type": bool,
        "parameter": "flip photo (rotate by 180°)",
    },
    "autorotate": {
        "variable": "autorotate",
        "default_value": True,
        "type": bool,
        "parameter": "automatically rotate photo so that main axis is horizontal",
    },
    "automask": {
        "variable": "automask",
        "default_value": True,
        "type": bool,
        "parameter": "use automask",
    },
    "automask_save": {
        "variable": "automask_save",
        "default_value": True,
        "type": bool,
        "parameter": "save automask",
    },
    "automask_grow": {
        "variable": "automask_grow",
        "default_value": 0.65,
        "type": float,
        "parameter": "growing of automask (0.5 <= grow < 1)",
    },
    "binarize_auto": {
        "variable": "binarize_auto",
        "default_value": True,
        "type": bool,
        "parameter": "automatically perform binarization in automask",
    },
    "binarize_threshold": {
        "variable": "binarize_threshold",
        "default_value": 10,
        "type": int,
        "parameter": "threshold for photo binarization (0-254) in automask if binarize_auto = False",
    },
    "mask_file": {
        "variable": "mask_file",
        "default_value": None,
        "type": str,
        "parameter": "path to mask file (open dialog if not found)",
    },
    "maskview": {
        "variable": "maskview",
        "default_value": "prompt",
        "type": str,
        "parameter": "don't save maskview (None), save maskview ('save') or prompt user if ok ('prompt)",
    },
    "autocrop": {
        "variable": "autocrop",
        "default_value": True,
        "type": bool,
        "parameter": "automatically crop photo to patch based on mask when True",
    },
    "autocrop_margin": {
        "variable": "autocrop_margin",
        "default_value": 40,
        "type": int,
        "parameter": "margin for autocrop in pixels",
    },
    "autocrop_save": {
        "variable": "autocrop_save",
        "default_value": "photo",
        "type": str,
        "parameter": "don't save (None), save cropped photo ('photo'), save cropped_masked_photo ('masked'), save photo, mask, cropped mask ('all')",
    },
    "pinholes": {
        "variable": "pinholes",
        "default_value": False,
        "type": bool,
        "parameter": "automatically evaluate pinholes",
    },
    "analyze_brightness": {
        "variable": "analyze_brightness",
        "default_value": False,
        "type": bool,
        "parameter": "analyzes brightness and optical density",
    },
    "radius_min_max": {
        "variable": "radius_min_max",
        "default_value": 2.5,
        "type": float,
        "parameter": "radius for min/max circle in mm",
    },
    "export_distribution": {
        "variable": "export_distribution",
        "default_value": False,
        "type": bool,
        "parameter": "exports csv with distribution",
    },
    "create_ppt": {
        "variable": "create_ppt",
        "default_value": False,
        "type": bool,
        "parameter": "auto-create pptx file with results?",
    },
}

# ------------------------------------------------
# function/class definitions


def set_up_logging() -> None:
    """
    Set up logging (to file and print).
    """
    log_filename = log_file
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    logging.basicConfig(
        handlers=[
            logging.FileHandler(log_filename, mode="w"),
            logging.StreamHandler(),  # to print to terminal
        ],
        format=("%(levelname)s (%(asctime)s): %(message)s"),
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
        # force=True,
    )


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

    def export_csv(self, path: str) -> None:
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
                        # if self.__dict__[attribute]["value"]
                        # else "not set"
                        ,
                    ]
                )
        logging.info(f'CSV file with results saved: "{path}".')


class Settings:
    """Object with user settings from csv file"""

    def __init__(self, filename: str, settings: dict) -> None:
        """Read csv file with user settings and set them as attributes."""

        # This list holds the set attributes.
        self.attribute_list = []
        if filename:
            logging.info(f"Trying to read user settings from {filename}.")
            self.read_settings_from_file(filename, settings)
        else:
            logging.info(
                "No file with user settings found. Setting default parameters."
            )
            self.set_settings_from_default_values(settings)

    def set_sett_attribute(self, attribute: str, value: dict) -> None:
        """
        Sets a setting as an attribute of the object
        and adds to list of attributes "attribute_list".
        """
        setattr(self, attribute, value)
        self.__dict__["attribute_list"].append(attribute)

    @staticmethod
    def set_settings_path(*paths) -> str:
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
        if not GUI:
            logging.info(
                "Trying to select correct csv file with settings via file dialog."
            )
            dialog_path = sg.popup_get_file(
                message="Select file containing the settings",
                icon=r"logo/logo.ico",
                title="Select file containing the settings",
                file_types=(("CSV files", ".csv"),),
                keep_on_top=True,
                no_window=False,
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
        logging.info("No setting file found. Using standard settings.")
        return None

    def read_settings_from_file(self, filename: str, settings: dict) -> None:
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
        for num, property in enumerate(settings.values()):
            corresponding_key = list(settings.keys())[num]
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
                        f'Setting for "{property["variable"]}" found. Value set to {None}.'
                    )
                else:
                    # set datatype
                    try:
                        if property["type"] == bool:
                            if propertyitem["value"] in {
                                "True",
                                "1",
                                "yes",
                                "on",
                                "enabled",
                            }:
                                attr_type = True
                            elif propertyitem["value"] in {
                                "False",
                                "0",
                                "no",
                                "off",
                                "disabled",
                            }:
                                attr_type = False
                            else:
                                logging.exception(
                                    f"Cannot interpret input for {property['variable']} in settings file."
                                )
                                raise ValueError(
                                    f"Cannot interpret input for {property['variable']} in settings file."
                                )
                        else:
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
                            f"Value set to {attr_type}."
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
                            f"Setting for \"{property['variable']}\" found: {propertyitem['value']},\n"
                            f'\tbut could not be converted to expected type "{property["type"]}". '
                            f'Setting to default value of {property["default_value"]}.'
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
                    f'Setting for "{property["variable"]}" expected but not found. Setting to default value of {property["default_value"]}.'
                )
        logging.info(f"All user settings read from {filename}.")

    def set_settings_from_default_values(self, settings: dict) -> None:
        """Set all settings to default values (in settings)."""

        for num, property in enumerate(settings.values()):
            corresponding_key = list(settings.keys())[num]
            self.set_sett_attribute(
                corresponding_key,
                {
                    "variable": property["variable"],
                    "parameter": property["parameter"],
                    "value": property["default_value"],
                },
            )
        logging.info("All user settings set to default values.")

    @staticmethod
    def create_default_settings_csv(settings: dict, path: str) -> None:
        """Creates a csv file with default settings for the user to modify."""
        csv_header = ["property", "value", "explanation"]
        with open(path, "w", encoding="UTF8", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC, delimiter=",")
            writer.writerow(csv_header)
            for entry in settings.values():
                writer.writerow(
                    [entry["variable"], entry["default_value"], entry["parameter"]]
                )
        logging.info(f'CSV file with default values created: "{path}".')


class Gui:
    """User interface"""

    @staticmethod
    def event_loop() -> None:
        global window, values

        sg.theme("SystemDefault")
        sg.theme_background_color(color="#EFEDE7")
        sg.theme_button_color(("black", "#00B0E9"))
        sg.theme_text_element_background_color(color="#EFEDE7")
        sg.theme_element_background_color(color="#EFEDE7")

        general_frame = sg.Frame(
            "General",
            [
                [
                    sg.Text(
                        "operator \u2753 ",
                        tooltip="Name of operator for documentation.",
                    ),
                    sg.Input(
                        key="operator",
                        default_text=user_settings.operator["value"],
                        size=(1, 1),
                        expand_x=True,
                    ),
                ],
                [
                    sg.Text(
                        "photo file: \u2753 ",
                        key="file_text",
                        tooltip="Select a photo file for evaluation.",
                        text_color=None,
                    ),
                    sg.Input(
                        key="photo_file",
                        size=(1, 1),
                        expand_x=True,
                        default_text=user_settings.photo_file["value"],
                    ),
                    sg.FileBrowse(
                        file_types=(("Image Files", "*.jpg *.jpeg *.tiff *.png"),),
                        key="photo_file_input",
                    ),
                ],
                [
                    sg.Checkbox(
                        "custom sample name \u2753 ",
                        tooltip="Name of the sample for single photo evaluation. \nIf left empty, the name of the photo file will be used.",
                        key="custom_sample_name",
                        enable_events=True,
                        default=True if user_settings.sample_name["value"] else False,
                    ),
                    sg.Input(
                        key="sample_name",
                        default_text=user_settings.sample_name["value"],
                        size=(1, 1),
                        expand_x=True,
                        disabled=False if user_settings.sample_name["value"] else True,
                    ),
                ],
                [
                    sg.Checkbox(
                        "batch evaluation \u2753",
                        enable_events=True,
                        key="batch_evaluation",
                        tooltip="Evaluate all files in a folder.",
                        default=user_settings.batch_evaluation["value"],
                    )
                ],
                [
                    sg.Text(
                        "photo folder: \u2753 ",
                        key="folder_text",
                        tooltip="Select a folder for batch evaluation of all contained photo files \n(if activated).",
                        text_color="black"
                        if user_settings.batch_evaluation["value"]
                        else "grey",
                    ),
                    sg.Input(
                        key="photo_folder",
                        size=(1, 1),
                        expand_x=True,
                        disabled=not user_settings.batch_evaluation["value"],
                        default_text=user_settings.photo_folder["value"],
                    ),
                    sg.FolderBrowse(
                        key="photo_folder_input",
                        disabled=not user_settings.batch_evaluation["value"],
                    ),
                ],
            ],
            expand_x=True,
        )

        mask_frame = sg.Frame(
            "Mask",
            [
                [
                    sg.Text(
                        "mask file: \u2753 ",
                        key="mask_text",
                        tooltip="Select mask for photo from disc, if you have one.",
                        text_color="black"
                        if not user_settings.automask["value"]
                        else "grey",
                    ),
                    sg.Input(
                        key="mask_file",
                        size=(1, 1),
                        expand_x=True,
                        disabled=user_settings.automask["value"],
                        default_text=user_settings.mask_file["value"],
                    ),
                    sg.FileBrowse(
                        file_types=(("Image Files", "*.jpg *.jpeg *.tiff *.png"),),
                        key="mask_file_input",
                        disabled=user_settings.automask["value"],
                    ),
                ],
                [
                    sg.Checkbox(
                        "use automask \u2753",
                        enable_events=True,
                        key="automask",
                        tooltip="Automatically generate a mask file. \nPreferred method if you don't have one yet.",
                        default=user_settings.automask["value"],
                    )
                ],
                [
                    sg.Text("     "),
                    sg.Checkbox(
                        "save automask \u2753",
                        key="automask_save",
                        disabled=False,
                        tooltip="Save the automatically generated mask to a file \n(typically for use with other photos).",
                        default=user_settings.automask_save["value"],
                    ),
                ],
                [
                    sg.Text("     "),
                    sg.Checkbox(
                        "auto binarize  \u2753",
                        key="binarize_auto",
                        enable_events=True,
                        disabled=not user_settings.automask["value"],
                        tooltip="Automatically determine the threshold for binarization in automask. \nTry manual if it doesn't work",
                        default=user_settings.binarize_auto["value"],
                    ),
                ],
                [
                    sg.Text(
                        "binarization threshold: \u2753 ",
                        key="binarize_threshold_text",
                        tooltip="Manual threshold brightness value for binarization in automask. \nIgnored if auto binarization is used.",
                        text_color="grey"
                        if user_settings.binarize_auto["value"]
                        else "black",
                    ),
                    sg.Slider(
                        range=(0, 0)
                        if user_settings.binarize_auto["value"]
                        else (0, 254),
                        default_value=0 if user_settings.binarize_auto["value"] else 50,
                        resolution=1,
                        key="binarize_threshold",
                        tick_interval=50,
                        orientation="horizontal",
                        disabled=user_settings.binarize_auto["value"],
                        size=(10, 10),
                        expand_x=True,
                        # text_color="grey",
                    ),
                ],
                [
                    sg.Text(
                        "automask grow: \u2753 ",
                        tooltip="Amount to grow the mask area after automask.",
                        key="automask_grow_text",
                        text_color="grey"
                        if not user_settings.binarize_auto["value"]
                        else "black",
                    ),
                    sg.Slider(
                        range=(0.500, 0.950),
                        default_value=0.650,
                        resolution=0.050,
                        tick_interval=0.100,
                        orientation="horizontal",
                        disabled=False
                        if user_settings.binarize_auto["value"]
                        else True,
                        size=(10, 10),
                        expand_x=True,
                        key="automask_grow",
                        # text_color=None,
                    ),
                ],
                [
                    sg.Text("Maskview: "),
                    sg.Radio(
                        "off \u2753",
                        group_id="maskview",
                        key="maskview_off",
                        default=True
                        if user_settings.maskview["value"] == None
                        else False,
                        tooltip="Don't generate maskview.",
                    ),
                    sg.Radio(
                        "save \u2753",
                        group_id="maskview",
                        key="maskview_save",
                        default=True
                        if user_settings.maskview["value"] == "save"
                        else False,
                        tooltip="Save maskview for photo.",
                    ),
                    sg.Radio(
                        "prompt \u2753",
                        group_id="maskview",
                        key="maskview_prompt",
                        default=True
                        if user_settings.maskview["value"] == "prompt"
                        else False,
                        tooltip="Save maskview and prompt user if it looks good.",
                    ),
                ],
            ],
            expand_x=True,
        )

        analysis_frame = sg.Frame(
            "Analysis",
            [
                [
                    sg.Checkbox(
                        "analyze brightness \u2753 ",
                        enable_events=True,
                        key="analyze_brightness",
                        tooltip="Analyze the brightness distribution. \nThis also calculates the optical density.",
                        default=user_settings.analyze_brightness["value"],
                    )
                ],
                [
                    sg.Text("     "),
                    sg.Checkbox(
                        "export CSV \u2753 ",
                        enable_events=True,
                        key="export_distribution",
                        tooltip="Saves a CSV file with the brightness distribution. \nTypically used to create new calibrations.",
                        disabled=not user_settings.analyze_brightness["value"],
                    ),
                ],
                [
                    sg.Checkbox(
                        "analyze pinholes \u2753 ",
                        enable_events=True,
                        key="pinholes",
                        tooltip="Analyze pinholes. You need a suitable calibration for that.",
                        default=user_settings.export_distribution["value"]
                        if user_settings.analyze_brightness["value"]
                        else False,
                    )
                ],
                [
                    sg.Checkbox(
                        "create pptx file \u2753 ",
                        enable_events=True,
                        key="create_ppt",
                        tooltip="Generates a PPTX file with the results.",
                        default=user_settings.create_ppt["value"],
                        disabled=not user_settings.analyze_brightness["value"],
                    )
                ],
            ],
            expand_x=True,
        )

        editing_frame = sg.Frame(
            "Editing",
            [
                [
                    sg.Checkbox(
                        "flip photo \u2753 ",
                        enable_events=True,
                        key="flip",
                        tooltip="Flip photo (rotate by 180°).",
                        default=user_settings.flip["value"],
                    )
                ],
                [
                    sg.Checkbox(
                        "autorotate \u2753 ",
                        enable_events=True,
                        key="autorotate",
                        tooltip="Rotate the photo so that the main axis is horizontal.",
                        default=user_settings.autorotate["value"],
                    )
                ],
                [
                    sg.Checkbox(
                        "autocrop \u2753 ",
                        enable_events=True,
                        key="autocrop",
                        tooltip="Automatically crop photo file based on mask.",
                        default=user_settings.autocrop["value"],
                    )
                ],
                [
                    sg.Text(
                        "autocrop margin \u2753 ",
                        enable_events=True,
                        key="autocrop_margin_text",
                        tooltip="Number of pixels to leave around patch when autocrop is used.",
                        text_color="black"
                        if user_settings.autocrop["value"]
                        else "grey",
                    ),
                    sg.Spin(
                        [i for i in range(500)],
                        user_settings.autocrop_margin["value"],
                        disabled=not user_settings.autocrop["value"],
                        readonly=False,
                        size=(4, 1),
                        key="autocrop_margin",
                    ),
                ],
                [
                    sg.Text(
                        "save autocropped \u2753 ",
                        enable_events=True,
                        key="autocrop_save_text",
                        tooltip="What to save after autocrop: \nDon't save (None), save cropped photo ('photo'), save cropped_masked_photo ('masked'), \nsave photo, mask, cropped mask ('all')",
                        text_color="black"
                        if user_settings.autocrop["value"]
                        else "grey",
                    ),
                    sg.Combo(
                        [None, "photo", "masked", "all"],
                        enable_events=True,
                        key="autocrop_save",
                        default_value=user_settings.autocrop_save["value"],
                        disabled=not user_settings.autocrop["value"],
                    ),
                ],
            ],
            expand_x=True,
        )

        targets_frame = sg.Frame(
            "Exif targets",
            [
                [
                    sg.Text(
                        "camera make \u2753 ",
                        enable_events=True,
                        key="target_Make_text",
                        tooltip="Target EXIF tag for camera make. \nWill not run if a different tag is found.",
                    ),
                    sg.Input(
                        key="target_Make",
                        size=(10, 1),
                        default_text=user_settings.target_Make["value"],
                    ),
                    sg.Text(
                        "   model \u2753 ",
                        enable_events=True,
                        key="target_Model_text",
                        tooltip="Target EXIF tag for camera model. \nWill not run if a different tag is found.",
                    ),
                    sg.Input(
                        key="target_Model",
                        size=(10, 1),
                        default_text=user_settings.target_Model["value"],
                    ),
                ],
                [
                    sg.Text(
                        "lens model \u2753 ",
                        enable_events=True,
                        key="target_LensModel_text",
                        tooltip="Target EXIF tag for lens model. \nWill not run if a different tag is found.",
                    ),
                    sg.Input(
                        key="target_LensModel",
                        size=(15, 1),
                        default_text=user_settings.target_LensModel["value"],
                    ),
                    sg.Text(
                        "focal length \u2753 ",
                        enable_events=True,
                        key="target_FocalLength_text",
                        tooltip="Target EXIF tag for focal length in mm. \nWill not run if a different tag is found.",
                    ),
                    sg.Input(
                        key="target_FocalLength",
                        size=(5, 1),
                        default_text=user_settings.target_FocalLength["value"],
                    ),
                ],
                [
                    sg.Text(
                        "image width \u2753 ",
                        enable_events=True,
                        key="target_ExifImageWidth_text",
                        tooltip="Target EXIF tag for image width in pixels. \nWill not run if a different tag is found.",
                    ),
                    sg.Input(
                        key="target_ExifImageWidth",
                        size=(5, 1),
                        default_text=user_settings.target_ExifImageWidth["value"],
                    ),
                    sg.Text(
                        "   image height \u2753 ",
                        enable_events=True,
                        key="target_ExifImageHeight_text",
                        tooltip="Target EXIF tag for image height in pixels. \nWill not run if a different tag is found.",
                    ),
                    sg.Input(
                        key="target_ExifImageHeight",
                        size=(5, 1),
                        default_text=user_settings.target_ExifImageHeight["value"],
                    ),
                ],
                [
                    sg.Text(
                        "ISO number \u2753 ",
                        enable_events=True,
                        key="target_ISOSpeedRatings_text",
                        tooltip="Target EXIF tag for ISO number. \nWill not run if a different tag is found.",
                    ),
                    sg.Input(
                        key="target_ISOSpeedRatings",
                        size=(5, 1),
                        default_text=user_settings.target_ISOSpeedRatings["value"],
                    ),
                    sg.Text(
                        "F number \u2753 ",
                        enable_events=True,
                        key="target_FNumber_text",
                        tooltip="Target EXIF tag for F number of aperture. \nWill not run if a different tag is found.",
                    ),
                    sg.Input(
                        key="target_FNumber",
                        size=(5, 1),
                        default_text=user_settings.target_FNumber["value"],
                    ),
                ],
                [
                    sg.Text(
                        "exposure time \u2753 ",
                        enable_events=True,
                        key="target_ExposureTime_text",
                        tooltip="Target EXIF tag for exposure time in seconds. \nWill not run if a different tag is found.",
                    ),
                    sg.Input(
                        key="target_ExposureTime",
                        size=(5, 1),
                        default_text=user_settings.target_ExposureTime["value"],
                    ),
                ],
            ],
            expand_x=True,
        )

        max_progress = 100

        layout = [
            [
                sg.Column(
                    [[general_frame], [mask_frame]],
                    expand_x=True,
                    element_justification="left",
                ),
                sg.Column(
                    [[editing_frame], [targets_frame], [analysis_frame]],
                    vertical_alignment="top",
                    element_justification="left",
                ),
            ],
            [
                sg.ProgressBar(
                    max_progress,
                    size=(10, 20),
                    expand_x=True,
                    key="-PBAR-",
                    bar_color=("#FF8672", "#C7BED1"),
                ),
                sg.Button(
                    "Run \u2753",
                    size=(10, 1),
                    tooltip="Run the evaluation.",
                    expand_x=False,
                ),
            ],
            [sg.Output(size=(150, 20), key="log", expand_x=True, expand_y=True)],
            [
                sg.Text(
                    "For help contact bastian.ebeling@kuraray.com.",
                    justification="right",
                    expand_x=True,
                )
            ],
        ]

        window = sg.Window(
            f"anabu v. {VERSION}",
            layout,
            resizable=True,
            icon=r"logo/logo.ico",
            finalize=True,
        )

        window.TKroot.minsize(500, 600)

        while True:  # Event Loop
            event, values = window.read(timeout=100)
            if event == sg.WIN_CLOSED:
                sys.exit()
            elif event == "automask":
                if values["automask"] == True:
                    window["automask_save"].update(disabled=False)
                    window["binarize_auto"].update(disabled=False)
                    window["mask_text"].update(text_color="grey")
                    window["mask_file"].update("", disabled=True)
                    window["mask_file_input"].update(disabled=True)
                    window["automask_grow_text"].update(text_color="black")
                    window["automask_grow"].update(
                        0.650, disabled=False, range=(0.500, 0.950)
                    )
                    if values["binarize_auto"] == False:
                        window["binarize_threshold_text"].update(text_color="black")
                        window["binarize_threshold"].update(
                            50, disabled=False, range=(0, 255)
                        )
                else:
                    window["automask_save"].update(False, disabled=True)
                    window["binarize_auto"].update(False, disabled=True)
                    window["mask_text"].update(text_color="black")
                    window["mask_file"].update(disabled=False)
                    window["mask_file_input"].update(disabled=False)
                    window["automask_grow_text"].update(text_color="grey")
                    window["automask_grow"].update(0, disabled=True, range=(0, 0))
                    window["binarize_threshold_text"].update(text_color="grey")
                    window["binarize_threshold"].update(0, disabled=True, range=(0, 0))
            elif event == "custom_sample_name":
                if values["custom_sample_name"] == True:
                    window["sample_name"].update(disabled=False)
                else:
                    window["sample_name"].update(disabled=True)
            elif event == "batch_evaluation":
                if values["batch_evaluation"] == True:
                    window["file_text"].update(text_color="grey")
                    window["custom_sample_name"].update(False, disabled=True)
                    window["sample_name"].update(disabled=True)
                    window["photo_file"].update("", disabled=True)
                    window["photo_file_input"].update(disabled=True)
                    window["sample_name"].update("")
                    window["photo_folder"].update(disabled=False)
                    window["photo_folder_input"].update(disabled=False)
                    window["folder_text"].update(text_color="black")
                if values["batch_evaluation"] == False:
                    window["file_text"].update(text_color="black")
                    window["custom_sample_name"].update(disabled=False)
                    window["photo_file"].update(disabled=False)
                    window["photo_file_input"].update(disabled=False)
                    window["photo_folder"].update("", disabled=True)
                    window["photo_folder_input"].update(disabled=True)
                    window["folder_text"].update(text_color="grey")
            elif event == "binarize_auto":
                if values["binarize_auto"] == False:
                    window["binarize_threshold_text"].update(text_color="black")
                    window["binarize_threshold"].update(
                        50, disabled=False, range=(0, 255)
                    )
                if values["binarize_auto"] == True:
                    window["binarize_threshold_text"].update(text_color="grey")
                    window["binarize_threshold"].update(0, disabled=True, range=(0, 0))
            elif event == "autocrop":
                if values["autocrop"] == True:
                    window["autocrop_margin_text"].update(text_color="black")
                    window["autocrop_margin"].update(
                        user_settings.autocrop_margin["value"], disabled=False
                    )
                    window["autocrop_save_text"].update(text_color="black")
                    window["autocrop_save"].update(disabled=False)
                if values["autocrop"] == False:
                    window["autocrop_margin_text"].update(text_color="grey")
                    window["autocrop_margin"].update(disabled=True)
                    window["autocrop_save_text"].update(text_color="grey")
                    window["autocrop_save"].update(disabled=True)
            elif event == "analyze_brightness":
                if values["analyze_brightness"] == True:
                    window["export_distribution"].update(disabled=False)
                    window["create_ppt"].update(disabled=False)
                if values["analyze_brightness"] == False:
                    window["export_distribution"].update(False, disabled=True)
                    window["create_ppt"].update(disabled=True)

            elif event == "Run \u2753":
                # analysis.run_button()
                try:
                    analysis.run_button()
                except:
                    logging.info("An error occurred!")
                    try:
                        copy2(
                            "log/logfile.log",
                            f"{os.path.splitext(photo.photo.photo_path)[0]}_logfile.txt",
                        )
                        logging.info(
                            f"Logfile copied to {os.path.splitext(photo.photo.photo_path)[0]}_logfile.txt."
                        )
                    except:
                        logging.info(f"See logfile.")

        window.close()

    @staticmethod
    def set_settings_from_GUI() -> None:
        user_settings.operator["value"] = values["operator"]
        user_settings.photo_file["value"] = values["photo_file"]
        user_settings.sample_name["value"] = values["sample_name"]
        user_settings.batch_evaluation["value"] = bool(values["batch_evaluation"])
        user_settings.photo_folder["value"] = values["photo_folder"]
        user_settings.automask["value"] = bool(values["automask"])
        user_settings.mask_file["value"] = values["mask_file"]
        user_settings.automask_save["value"] = bool(values["automask_save"])
        user_settings.binarize_auto["value"] = bool(values["binarize_auto"])
        user_settings.binarize_threshold["value"] = int(values["binarize_threshold"])
        user_settings.maskview["value"] = (
            None if values["maskview_off"] else user_settings.maskview["value"]
        )
        user_settings.maskview["value"] = (
            "save" if values["maskview_save"] else user_settings.maskview["value"]
        )
        user_settings.maskview["value"] = (
            "prompt" if values["maskview_prompt"] else user_settings.maskview["value"]
        )
        user_settings.analyze_brightness["value"] = bool(values["analyze_brightness"])
        user_settings.export_distribution["value"] = bool(values["export_distribution"])
        user_settings.create_ppt["value"] = bool(values["create_ppt"])
        user_settings.pinholes["value"] = bool(values["pinholes"])
        user_settings.flip["value"] = bool(values["flip"])
        user_settings.autorotate["value"] = bool(values["autorotate"])
        user_settings.autocrop["value"] = bool(values["autocrop"])
        user_settings.autocrop_margin["value"] = int(values["autocrop_margin"])
        user_settings.autocrop_save["value"] = values["autocrop_save"]
        user_settings.target_Make["value"] = values["target_Make"]
        user_settings.target_Model["value"] = values["target_Model"]
        user_settings.target_LensModel["value"] = values["target_LensModel"]
        user_settings.target_FocalLength["value"] = float(values["target_FocalLength"])
        user_settings.target_ExifImageWidth["value"] = int(
            values["target_ExifImageWidth"]
        )
        user_settings.target_ExifImageHeight["value"] = int(
            values["target_ExifImageHeight"]
        )
        user_settings.target_ISOSpeedRatings["value"] = int(
            values["target_ISOSpeedRatings"]
        )
        user_settings.target_FNumber["value"] = float(values["target_FNumber"])
        user_settings.target_ExposureTime["value"] = float(
            values["target_ExposureTime"]
        )
        logging.info("Settings updated with values from GUI.")

    @staticmethod
    def generate_progress_steps():
        batch = user_settings.batch_evaluation["value"]
        no_files = len(user_settings.file_list["value"]) if batch else 1
        steps = 2
        steps += 10 * no_files
        if user_settings.automask["value"]:
            steps += 7 * no_files
        if user_settings.autorotate["value"]:
            steps += 2 * no_files
        if user_settings.analyze_brightness["value"]:
            steps += 8 * no_files
        if user_settings.pinholes["value"]:
            steps += 12 * no_files
        if user_settings.create_ppt["value"]:
            steps += 7 * no_files
        for i in range(steps):
            yield (i + 1) / steps * 100

    @staticmethod
    def update_progress_bar():
        if GUI:
            window["-PBAR-"].update(current_count=next(analysis.progress_generator))

    @staticmethod
    def initiate_progress_bar():
        window["-PBAR-"].update(current_count=0, bar_color=("#FF8672", "#C7BED1"))

    @staticmethod
    def finish_progress_bar():
        window["-PBAR-"].update(current_count=100, bar_color=("#75B96C", "#C7BED1"))


class Handler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        global buffer
        record = f"{record.asctime} [{record.levelname}]: {record.message}"
        buffer = f"{buffer}\n{str(record)}".strip()
        window["log"].update(value=buffer)
        window.Refresh()


def get_folder(path: str) -> str:
    """Returns path stripped of the file extension."""
    return os.path.splitext(path)[0]


def get_files_in_folder(folder: str, ignore: list = files_ignore) -> list:
    """
    Get list of photo files in folder which don't contain strings in files

    Args:
        folder (str): folder containing photo files
        ignore (list): list of strings to ignore

    Returns:
        list: list of photo files
    """
    file_list_all = glob.glob(os.path.join(folder, "*.jpg"))
    file_list_all += glob.glob(os.path.join(folder, "*.jpeg"))
    file_list_all += glob.glob(os.path.join(folder, "*.png"))
    file_list_all += glob.glob(os.path.join(folder, "*.tiff"))
    file_list = [
        file
        for file in file_list_all
        if not any(ignorefile in file for ignorefile in ignore)
    ]
    return file_list


def folder_dialog() -> str:
    """
    Use dialog to select folder with photos.

    Returns:
        str: path to selected folder
    """
    logging.info(f"Using dialog for selecting folder with photos.")

    folder = sg.popup_get_folder(
        message="Select file containing the settings",
        icon=r"logo/logo.ico",
        title="Select file containing the settings",
        keep_on_top=True,
        no_window=False,
    )
    logging.info(f"Selected folder with photo files using dialog: {folder}")
    results.add_result(
        variable="folder_dialog",
        parameter="path to folder with photo files selected with dialog",
        value=folder,
    )
    return folder


def progressBar(
    iterable: Iterable,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 1,
    length: int = 100,
    fill: str = "█",
    printEnd: str = "\r",
) -> Generator:
    """
    Call in a loop to create terminal progress bar

    Args:
        iterable (Iterable): Iterable object
        prefix (str, optional): Prefix string. Defaults to ''.
        suffix (str, optional): Suffix string. Defaults to ''.
        decimals (int, optional): Positive number of decimals in percent complete. Defaults to 1.
        length (int, optional): Character length of bar. Defaults to 100.
        fill (str, optional): Bar fill character. Defaults to '█'.
        printEnd (str, optional): End character. Defaults to "\r".
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total))
        )
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + "-" * (length - filledLength)
        print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)

    # Initial call
    printProgressBar(0)
    # Update progress bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print new line on complete
    print()


def clear_log_file() -> None:
    """Clears the log file"""
    with open(log_file, "w", encoding="UTF8") as f:
        pass
    set_up_logging()


def end_analysis() -> None:
    """Function to be called at the end. Copies logfile to path."""
    results.export_csv(f"{os.path.splitext(photo.photo.photo_path)[0]}_results.csv")
    logging.info("----------------------------------")
    logging.info("Evaluation completed successfully!")
    logging.info("----------------------------------")
    copy2(
        "log/logfile.log", f"{os.path.splitext(photo.photo.photo_path)[0]}_logfile.txt"
    )
    logging.info(
        f"Logfile copied to {os.path.splitext(photo.photo.photo_path)[0]}_logfile.txt."
    )


def run_interface() -> None:
    """Execute the interface functions."""
    # set_up_logging() needs to be executed individually at the very start
    global user_settings, results, buffer
    set_up_logging()
    results = Results()
    settings_path = Settings.set_settings_path(*settings_try_paths)
    if IGNORE_SETTINGS_FILE:
        logging.info("Ignoring files with settings.")
        settings_path = None
    user_settings = Settings(settings_path, settings_dict)
    results.add_result(
        variable="version",
        parameter="version of anabu",
        value=VERSION,
    )

    logging.info("Starting GUI.")
    buffer = ""
    ch = Handler()
    logging.getLogger("").addHandler(ch)
    Gui.event_loop()


# ------------------------------------------------
# executions

if is_main:
    run_interface()
