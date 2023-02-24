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
    import photo
except:
    from anabu import photo
from collections.abc import Generator, Iterable
import csv
from datetime import datetime
import glob
import logging
import os
from shutil import copy2
from tkinter import Tk, filedialog, messagebox  # FIXME messagebox needed in this file?
import PySimpleGUI as sg


# ------------------------------------------------
# variables

# version number of anabu
VERSION = "0.8"

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
    "_scale_axes",
    "_distribution_plot",
}

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
        "parameter": "name of the analyzed sample (not for batch)",
    },
    "photo_file": {
        "variable": "photo_file",
        "default_value": "undefined",
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
        "default_value": "undefined",
        "type": str,
        "parameter": "folder for batch batch evaluation",
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
        "default_value": None,
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
        "default_value": None,
        "type": str,
        "parameter": "don't save (None), save cropped photo ('photo'), save cropped_masked_photo ('masked'), save photo, mask, cropped mask ('all')",
    },
    "pinholes": {
        "variable": "pinholes",
        "default_value": True,
        "type": bool,
        "parameter": "automatically evaluate pinholes",
    },
    "export_distribution": {
        "variable": "export_distribution",
        "default_value": False,
        "type": bool,
        "parameter": "exports csv with distribution",
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


def set_up_tkinter() -> None:
    """
    Set up tkinter.
    """
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
    folder = filedialog.askdirectory(
        title="Select folder with photo files for evaluation",
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


# FIXME finalize/test function
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
    global user_settings, results

    set_up_tkinter()
    results = Results()
    settings_path = Settings.set_settings_path(*settings_try_paths)
    user_settings = Settings(settings_path, settings_dict)
    results.add_result(
        variable="version",
        parameter="version of anabu",
        value=VERSION,
    )
    results.settings_to_results(user_settings)
    if user_settings.batch_evaluation["value"]:
        try:
            file_list = get_files_in_folder(user_settings.photo_folder["value"])
        except:
            file_list = get_files_in_folder(folder_dialog())
        user_settings.set_sett_attribute(
            "file_list",
            {
                "variable": "file_list",
                "parameter": "list of files for evaluation",
                "value": file_list,
            },
        )
        results.add_result(
            variable="file_list",
            parameter="photo files for batch evaluation",
            value=file_list,
        )
        logging.info(f"Found {len(file_list)} photos for batch evaluation: {file_list}")


class Handler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        global buffer
        record = f"{record.asctime} [{record.levelname}]: {record.message}"
        buffer = f"{buffer}\n{str(record)}".strip()
        window["log"].update(value=buffer)


# ------------------------------------------------
# executions

sg.theme("SystemDefault")

general_frame = sg.Frame(
    "General",
    [
        [
            sg.Text("operator \u2753 ", tooltip="Name of operator for documentation."),
            sg.Input(key="operator", default_text="not defined", size= (1,1),expand_x = True)
        ],
        [
            sg.Text(
                "mask file: \u2753 ",
                key="file_text",
                tooltip="Select a photo file for evaluation.",
            ),
            sg.Input(key="photo_file", size= (1,1),expand_x = True),
            sg.FileBrowse(
                file_types=(("Image Files", "*.jpg *.jpeg *.tiff *.png"),),
                key="photo_file_input",
            ),
        ],
        [
            sg.Text("sample name \u2753 ", tooltip="Name of the sample for single photo evaluation. \nIf left empty, the name of the photo file will be used."),
            sg.Input(key="sample name", default_text="", size= (1,1),expand_x = True)
        ],
        [
            sg.Checkbox(
                "batch evaluation \u2753",
                enable_events=True,
                key="batch_evaluation",
                tooltip="Evaluate all files in a folder.",
            )
        ],
        [
            sg.Text(
                "photos folder: \u2753 ",
                key="file_text",
                tooltip="Select a folder for batch evaluation of all contained photo files \n(if activated).",
            ),
            sg.Input(key="photo_folder", size= (1,1),expand_x = True),
            sg.FolderBrowse(
                key="photo_folder_input",
            ),
        ],
    ],
    expand_x = True
)

mask_frame = sg.Frame(
    "Mask",
    [
        [
            sg.Text(
                "mask file: \u2753 ",
                key="mask_text",
                tooltip="Select mask for photo from disc, if you have one.",
            ),
            sg.Input(key="mask_file", size= (1,1),expand_x = True),
            sg.FileBrowse(
                file_types=(("Image Files", "*.jpg *.jpeg *.tiff *.png"),),
                key="mask_file_input",
            ),
        ],
        [
            sg.Checkbox(
                "use automask \u2753",
                enable_events=True,
                key="automask",
                tooltip="Automatically generate a mask file. \nPreferred method if you don't have one yet.",
            )
        ],
        [
            sg.Checkbox(
                "save automask \u2753",
                key="automask_save",
                disabled=True,
                tooltip="Save the automatically generated mask to a file \n(typically for use with other photos).",
            )
        ],
        [
            sg.Checkbox(
                "auto binarize  \u2753",
                key="binarize_auto",
                disabled=True,
                tooltip="Automatically determine the threshold for binarization in automask. \nTry manual if it doesn't work",
            )
        ],
        [
            sg.Text(
                "binarization threshold: \u2753 ",
                tooltip="Manual threshold brightness value for binarization in automask. \nIgnored if auto binarization is used.",
            ),
            sg.Slider(
                range=(0, 254),
                default_value=50,
                resolution=1,
                key="binarize_threshold",
                tick_interval=50,
                orientation="horizontal",
                disabled=True,
                size= (10,10),
                expand_x = True
            ),
        ],
        [
            sg.Text(
                "automask grow: \u2753 ",
                tooltip="Amount to grow the mask area after automask.",
            ),
            sg.Slider(
                range=(0.500, 0.950),
                default_value=0.650,
                resolution=0.050,
                tick_interval=0.100,
                orientation="horizontal",
                disabled=False,
                size= (10,10),
                expand_x = True
            ),
        ],
        [
            sg.Text("Maskview: "),
            sg.Radio(
                "off \u2753",
                "Radiomaskview",
                default=False,
                tooltip="Don't generate maskview.",
            ),
            sg.Radio(
                "save \u2753",
                "Radiomaskview",
                default=True,
                tooltip="Save maskview for photo.",
            ),
            sg.Radio(
                "prompt \u2753",
                "Radiomaskview",
                default=False,
                tooltip="Save maskview and prompt user if it looks good.",
            ),
        ],
    ],
    expand_x = True
)

analysis_frame = sg.Frame(
    "Analysis",
    [
        [
            sg.Checkbox(
                "analyze brightness \u2753 ",
                enable_events=True,
                key="density",
                tooltip="Analyze the brightness distribution. \nThis also calculates the optical density.",
            )
        ],
        [
            sg.Checkbox(
                "export CSV \u2753 ",
                enable_events=True,
                key="export CSV",
                tooltip="Saves a CSV file with the brightness distribution. \nTypically used to create new calibrations.",
            )
        ],
        [
            sg.Checkbox(
                "analyze pinholes \u2753 ",
                enable_events=True,
                key="export_distribution",
                tooltip="Analyze pinholes. You need a suitable calibration for that.",
            )
        ],
        [
            sg.Checkbox(
                "create pptx file \u2753 ",
                enable_events=True,
                key="create_ppt",
                tooltip="Generates a PPTX file with the results.",
            )
        ],
    ],
    expand_x = True
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
            )
        ],
        [
            sg.Checkbox(
                "autorotate \u2753 ",
                enable_events=True,
                key="autorotate",
                tooltip="Rotate the photo so that the main axis is horizontal.",
            )
        ],
        [
            sg.Checkbox(
                "analyze pinholes \u2753 ",
                enable_events=True,
                key="export_distribution",
                tooltip="Analyze pinholes. You need a suitable calibration for that.",
            )
        ],
        [
            sg.Checkbox(
                "create pptx file \u2753 ",
                enable_events=True,
                key="create_ppt",
                tooltip="Generates a PPTX file with the results.",
            )
        ],
    ],
    expand_x = True
)

max_progress = 100

layout = [
    [sg.Column([[general_frame],[mask_frame]], expand_x = True, element_justification = "left"),
    sg.Column([[editing_frame],[analysis_frame]], expand_x = True, vertical_alignment='top', element_justification = "left")],
    [sg.ProgressBar(max_progress, size=(10, 20), expand_x = True,  key='-PBAR-'),
    sg.Button("Run \u2753", size=(10, 1), tooltip="Run the evaluation.", expand_x = False)],
    [sg.Output(size=(150, 8), key="log", expand_x = True, expand_y = True)],
    [
        sg.Text(
            "For help contact bastian.ebeling@kuraray.com.",
            justification="right",
            expand_x=True,
        )
    ],
]

window = sg.Window(f"anabu v. {VERSION}", layout, resizable=True, icon=r"logo/logo.ico", finalize=True)

window.TKroot.minsize(500,600)


set_up_logging()
buffer = ""
ch = Handler()
logging.getLogger("").addHandler(ch)

while True:  # Event Loop
    event, values = window.read(timeout=100)
    if event == sg.WIN_CLOSED:
        break
    elif event == "automask":
        if values["automask"] == True:
            window["automask_save"].update(disabled=False)
            window["binarize_auto"].update(disabled=False)
            window["mask_file"].update(disabled=True)
            window["mask_file_input"].update(disabled=True)
        else:
            window["automask_save"].update(False, disabled=True)
            window["binarize_auto"].update(False, disabled=True)
            window["mask_file"].update(disabled=False)
            window["mask_file_input"].update(disabled=False)
    if event == "Run \u2753":
        run_interface()
        # file = sg.popup_get_file(
        #     "Select mask file",
        #     title="Select mask file",
        #     no_window=True,
        #     icon=r"logo/logo.ico",
        #     file_types=(("Image Files", "*.jpg *.jpeg *.tiff *.png"),),
        # )
        
window.close()

if is_main_2:
    run_interface()
    sg.theme("BlueMono")
    layout = [
        [sg.Text("Some text on Row 1")],
        [
            sg.Text("operator"),
            sg.InputText(default_text=user_settings.operator["value"], key="operator"),
        ],
        [sg.Button("Ok"), sg.Button("Cancel")],
    ]
    # Create the Window
    window = sg.Window(f"anabu v. {VERSION}", layout, icon=r"logo/logo.ico")
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if (
            event == sg.WIN_CLOSED or event == "Cancel"
        ):  # if user closes window or clicks cancel
            break
        user_settings.operator["value"] = values["operator"]
        sg.easy_print("You entered ", values)
    # print(user_settings.operator['value'])

    window.close()
