#!/usr/bin/env python3

# imports

import logging
from tkinter import Tk, filedialog, messagebox
import csv

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
        force=True,
    )

def set_up_tkinter():
    """set up tkinter"""
    root = Tk()
    # hides small tkinter window
    root.withdraw()
    # make opened windows will be active above all windows
    root.attributes(
        "-topmost", True
    )

class settings:
    """Object with user settings from scv file"""

    def __init__(self, filename: str, expected_settings: dict):
        logging.info(f"Reading user settings from {filename}.")
        # get list of dicts from csv file
        with open(filename, 'r') as csvfile:
            csvreader = csv.DictReader(
                csvfile, delimiter=",", skipinitialspace=True, quoting=csv.QUOTE_MINIMAL)
            property_list = list(csvreader)
        # check if expected properties were in csv file and set them
        # TODO implement check for type
        for num, property in enumerate(expected_settings.values()):
            corresponding_key = list(expected_settings.keys())[num]
            propertyitem = next(
                (item for item in property_list if item["property"] == property[0]), None)
            if propertyitem:
                setattr(self, corresponding_key,propertyitem['value'])
                logging.info(
                        f"Setting for \"{property[0]}\" found in {filename}. Value set to \"{propertyitem['value']}\".")
            else:
                setattr(self, corresponding_key,property[1])
                logging.warning(
                    f"Setting for \"{property[0]}\" expected but not found in {filename}. Setting to default value of \"{property[1]}\".")

# variables

# property: ["name of property in csv", "default value if not found", "type of value"]
# TODO Double-check target values
settings_dict = {
    "operator": ["operator","undefined",str], 
    "sample_name": ["sample_name","undefined",str], 
    "photo_file": ["photo_file","undefined",str], 
    "target_Make": ["target_Make",None,str], 
    "target_model": ["target_Model",None,str], 
    "target_BrightnessValue": ["target_BrightnessValue",None,int], 
    "target_ExifImageWidth": ["target_ExifImageWidth",None,int], 
    "target_ExifImageHeight": ["target_ExifImageHeight",None,int], 
    "target_FocalLength": ["target_FocalLength",None,int], 
    "target_ExposureTime": ["target_ExposureTime",None,float], 
    "target_FNumber": ["target_FNumber",None,int], 
    "target_LensModel": ["target_LensModel",None,str], 
    "target_ISOSpeedRatings": ["target_ISOSpeedRatings",None,int], 
    "target_WhiteBalance": ["target_WhiteBalance",None,int], 
    "target_MeteringMode": ["target_MeteringMode",None,int], 
    "target_DigitalZoomRatio": ["target_DigitalZoomRatio",None,int], 
    "target_MeteringMode": ["target_MeteringMode",None,str], 
    "target_FocalLengthIn35mmFilm": ["target_FocalLengthIn35mmFilm",None,int], 
    "automask": ["automask",True,bool], 
    "mask_file": ["mask_file",None,str], 
    "mask_correction_x": ["mask_correction_x",0,int], 
    "mask_correction_y": ["mask_correction_y",0,int], 
    "mask_rotation_clockwise": ["mask_rotation_clockwise",0,float], 
    "binarize_threshold": ["binarize_threshold",150,int]
    }

# run interface functions
set_up_logging()
set_up_tkinter()
user_settings = settings("anabu/standard_settings.csv", settings_dict)