#!/usr/bin/env python3

"""
Defines the photo class.
"""

# ------------------------------------------------
# imports

try:
    import interface
except:
    import anabu.interface as interface

import os
import platform
from datetime import datetime
from typing import Union

import numpy as np
import skimage as sm
from PIL import ExifTags as PIL_ExifTags
from PIL import Image as PIL_Image

# ------------------------------------------------
# variables

# These are the supported photo types. Not tested, but it's very likely that other types will work out of the box when added to this list.
supported_types = ["MPO", "JPEG", "PNG", "TIFF"]

# Relevant EXIF tags
EXIF_tags = [
    ["Make", "Camera maker", None],
    ["Model", "Camera model", ""],
    ["BrightnessValue", "APEX average scene luminance", None],
    ["ExifImageWidth", "Image width in pixels", None],
    ["ExifImageHeight", "Image height in pixels", None],
    ["FocalLength", "Focal length in mm", None],
    ["ExposureTime", "Exposure time", None],
    ["FNumber", "F number (aperture)", None],
    ["LensModel", "Lens model", None],
    ["ISOSpeedRatings", "ISO (sensitivity)", None],
    ["WhiteBalance", "White balance", None],
    ["MeteringMode", "Metering mode", None],
    ["DigitalZoomRatio", "Digital zoom ratio", None],
    ["FocalLengthIn35mmFilm", "Focal length in 35 mm film in mm", None],
]

# set scale factor (from photographs of ruler)
SCALE_FACTOR = 8.82  # px per mm

# ------------------------------------------------
# function/class definitions


class Photo:
    """
    Photo object for evaluation.
    """

    def __init__(self, photo_path: str) -> None:
        """
        Read photo and set as attributes. Use dialog if file not found.

        Read and save photo format and creation date.

        Set attributes:
            photo_path: path to loaded photo
            photo_check: photo loaded with PIL for EXIF checks
            photo: photo loaded with skimage for evaluation
            file_name: name of photo file (without extension)
            folder: folder of photo file
            file_root: path to photo file (without extension)
            photo_file: path to photo file (with extension)

        Args:
            photo_path (str): path to photo
        """

        def photo_dialog() -> str:
            """
            Use dialog to select photo file.

            Returns:
                str: path to selected photo file
            """
            interface.logging.info(f"Using dialog for selecting photo file.")
            photo_file = interface.filedialog.askopenfilename(
                filetypes=[("Image Files", ".png .tiff, .jpeg .jpg")],
                title="Select photo file for evaluation",
            )
            interface.logging.info(f"Selected photo file using dialog: {photo_file}")
            interface.results.add_result(
                variable="photo_file_dialog",
                parameter="path to photo file selected with dialog",
                value=photo_file,
            )
            return photo_file

        self.photo_path = photo_path
        try:
            # read photo with PIL (for checks)
            self.photo_check = PIL_Image.open(photo_path)
        except FileNotFoundError:
            interface.logging.warning(f"File {photo_path} not found.")
            photo_path = photo_dialog()
        except AttributeError:
            interface.logging.warning(f"Filename {photo_path} could not be read.")
            photo_path = photo_dialog()
        try:
            self.photo_check = PIL_Image.open(photo_path)
            interface.logging.info(f"File {photo_path} found.")
        except AttributeError:
            interface.logging.exception(f"No valid photo file selected. {photo_path}")
            raise Exception(f"No valid photo file selected. {photo_path}")
        self.file_name = os.path.splitext(os.path.basename(photo_path))[0]
        try:
            # read photo with skimage (for evaluation)
            self.photo = sm.io.imread(photo_path)
            interface.logging.info(f"File {photo_path} loaded.")
        except:
            interface.logging.exception(f"Photo file could not be loaded. {photo_path}")
            raise Exception(f"Photo file could not be loaded. {photo_path}")
        self.folder = os.path.dirname(os.path.abspath(photo_path))
        self.file_root = os.path.splitext(photo_path)[0]
        self.photo_file = os.path.basename(photo_path)

    def __repr__(self) -> str:
        sm.io.imshow(self.photo)
        return f"Photo object for evaluation: shape: {self.photo.shape}."

    def save_image(self, image: np.array, suffix: str) -> None:
        """
        Save image to tiff file in folder of original
        and adds suffix to file name of original.

        Args:
            image (np.array): image to save
            filename (str): file name (w/o extension)
        """
        sm.io.imsave(
            os.path.splitext(self.photo_path)[0] + "_" + suffix + ".tiff",
            sm.util.img_as_ubyte(image),
        )
        interface.logging.info(
            f"Saved {suffix} to {os.path.splitext(self.photo_path)[0]}_{suffix}.tiff."
        )

    def open_image_os(self, suffix: str) -> None:
        """
        Open image in file folder for different os.

        Args:
            suffix (str): suffic of file including extension
        """
        # Open file for Mac, Windows, Linux
        if platform.system() == "Darwin":
            subprocess.call(
                ("open", os.path.splitext(self.photo_path)[0] + "_" + suffix)
            )
        elif platform.system() == "Windows":
            os.startfile(os.path.splitext(self.photo_path)[0] + "_" + suffix)
        else:
            subprocess.call(
                ("xdg-open", os.path.splitext(self.photo_path)[0] + "_" + suffix)
            )

    def basic_attribs(self) -> None:
        """
        Set basic attributes of photo.

        Set attributes:
            format: format of photo file
            creation_date: creation date of photo file
            sample_name: sample name given in settings or file name
            height, width: height and width of photo
        """
        try:
            self.format = self.photo_check.format
            interface.logging.info(
                f'Selected photo has the image type "{self.format}".'
            )
            interface.results.add_result(
                variable="image_type",
                parameter="image type of photo file",
                value=self.format,
            )
        except:
            interface.logging.warning(f"Could not read format of photo file.")
        if self.format in supported_types:
            interface.logging.info(f'The image type "{self.format}" is supported.')
        else:
            interface.logging.exception(
                f'The image type "{self.format}" is not supported.'
            )
            raise TypeError(f'The image type "{self.format}" is not supported.')
        try:
            self.creation_date = datetime.fromtimestamp(
                os.path.getmtime(self.photo_path)
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            )  # This is better manually and not from EXIF.
            interface.logging.info(
                f'Selected photo has the creation date "{self.creation_date}".'
            )
            interface.results.add_result(
                variable="creation_date",
                parameter="creation date of photo file",
                value=self.creation_date,
            )
        except:
            interface.logging.warning(f"Could not read creation date of photo file.")
        if bool(interface.user_settings.sample_name["value"]):
            self.sample_name = interface.user_settings.sample_name["value"]
            interface.logging.info(f'The sample name is "{self.sample_name}".')
        else:
            self.sample_name = self.file_name
            interface.logging.info(
                f'No sample name given. Using file name "{self.file_name}" as the sample name.'
            )
        interface.results.add_result(
            variable="sample_name",
            parameter="sample name of photo file",
            value=self.sample_name,
        )
        self.height, self.width = self.photo.shape[0], self.photo.shape[1]
        interface.logging.info(
            f"The photo has the width and height of {self.photo.shape[1]} and {self.photo.shape[0]} pixels."
        )
        interface.results.add_result(
            variable="width",
            parameter="width of photo file",
            value=self.photo.shape[1],
        )
        interface.results.add_result(
            variable="height",
            parameter="height of photo file",
            value=self.photo.shape[0],
        )

    @staticmethod
    def get_EXIF_targets() -> list:
        """
        Returns:
            list: EXIF targets from user settings
        """
        EXIF_tags_targets = {
            "Make": interface.user_settings.target_Make["value"],
            "Model": interface.user_settings.target_model["value"],
            "BrightnessValue": interface.user_settings.target_BrightnessValue["value"],
            "ExifImageWidth": interface.user_settings.target_ExifImageWidth["value"],
            "ExifImageHeight": interface.user_settings.target_ExifImageHeight["value"],
            "FocalLength": interface.user_settings.target_FocalLength["value"],
            "ExposureTime": interface.user_settings.target_ExposureTime["value"],
            "FNumber": interface.user_settings.target_FNumber["value"],
            "LensModel": interface.user_settings.target_LensModel["value"],
            "ISOSpeedRatings": interface.user_settings.target_ISOSpeedRatings["value"],
            "WhiteBalance": interface.user_settings.target_WhiteBalance["value"],
            "MeteringMode": interface.user_settings.target_MeteringMode["value"],
            "DigitalZoomRatio": interface.user_settings.target_DigitalZoomRatio[
                "value"
            ],
            "FocalLengthIn35mmFilm": interface.user_settings.target_FocalLengthIn35mmFilm[
                "value"
            ],
        }
        return EXIF_tags_targets

    def check_exif(self) -> bool:
        """
        Check the EXIF data of the photo file and compare with target parameters.

        Returns:
            bool: EXIF data coincide with targets.
        """
        image_exif = (
            self.photo_check._getexif()
        )  # doesn't find all exif data with .getexif(), older method seems to be ok
        exif_tag_dict = {}
        for key, val in image_exif.items():
            if key in PIL_ExifTags.TAGS:
                exif_tag_dict[PIL_ExifTags.TAGS[key]] = val
        interface.logging.info("Extracted EXIF data from photo file.")
        EXIF_tags_targets = Photo.get_EXIF_targets()
        for tagno in range(len(EXIF_tags)):
            try:
                EXIF_tags[tagno][2] = exif_tag_dict[EXIF_tags[tagno][0]]
                interface.logging.info(
                    f'EXIF tag "{EXIF_tags[tagno][0]}" found. {EXIF_tags[tagno][1]} is {EXIF_tags[tagno][2]}.'
                )
                interface.results.add_result(
                    variable=EXIF_tags[tagno][0],
                    parameter=EXIF_tags[tagno][1],
                    value=EXIF_tags[tagno][2],
                )
            except:
                logging.warning(
                    f'EXIF tag "{EXIF_tags[tagno][0]}" not found. Value cannot be recorded, but script will continue.'
                )
                interface.results.add_result(
                    variable=EXIF_tags[tagno][0],
                    parameter=EXIF_tags[tagno][1],
                    value=EXIF_tags[tagno][2],
                )
            if not EXIF_tags_targets[EXIF_tags[tagno][0]]:
                interface.logging.info(
                    f'There is no target for "{EXIF_tags[tagno][0]}" defined in settings.'
                )
            else:
                if EXIF_tags[tagno][2] == EXIF_tags_targets[EXIF_tags[tagno][0]]:
                    interface.logging.info(
                        f'There is a target for "{EXIF_tags[tagno][0]}". It coincides with the extracted value.'
                    )
                else:
                    interface.logging.exception(
                        f"The target for {EXIF_tags[tagno][0]} is {EXIF_tags_targets[EXIF_tags[tagno][0]]}."
                        f"A different value was extracted: {EXIF_tags[tagno][2]}."
                        f"Exiting evaluation."
                    )
                    raise Exception(
                        f"The target for {EXIF_tags[tagno][0]} is {EXIF_tags_targets[EXIF_tags[tagno][0]]}."
                        f"A different value was extracted: {EXIF_tags[tagno][2]}. Exiting evaluation."
                    )
        interface.logging.info(
            f"All EXIF tags extracted successfully for {self.file_name}. No conflict with target values."
        )
        interface.results.add_result(
            variable="EXIF_check",
            parameter="EXIF check for",
            value=True,
        )
        return True

    def mask_file(self, mask_path: str) -> None:
        """
        Open mask file and set attributes.

        Attr.:
            mask_path: file to loaded mask
            mask: the mask image
            mask_creation: creation date of mask file
            mask_width: pixel width of mask file
            mask_height: pixel height of mask file
        """

        def mask_dialog() -> str:
            """
            Use dialog to select mask file. In a masked file, pixels with value 0
            will be masked.

            Returns:
                str: path to selected mask file
            """
            interface.logging.info(f"Using dialog for selecting mask file.")
            mask_file = interface.filedialog.askopenfilename(
                filetypes=[("Image Files", ".png .tiff, .jpeg .jpg")],
                title="Select mask file for evaluation",
            )
            interface.logging.info(f"Selected mask file using dialog: {mask_file}")
            interface.results.add_result(
                variable="mask_file_dialog",
                parameter="path to mask file selected with dialog",
                value=mask_file,
            )
            return mask_file

        try:
            mask = sm.io.imread(mask_path)
        except FileNotFoundError:
            interface.logging.warning(f'Mask file could not be found. "{mask_path}"')
            mask_path = mask_dialog()
        except ValueError:
            interface.logging.warning(f'Mask file could not be opened. "{mask_path}"')
            mask_path = mask_dialog()
        except IOError:
            interface.logging.warning(f'No valid mask file given. "{mask_path}"')
            mask_path = mask_dialog()
        try:
            mask = sm.io.imread(mask_path)
            # convert to 1D
            try:
                mask = sm.util.img_as_ubyte(sm.color.rgb2gray(mask))
            except:
                pass
            # convert to boolean array, only 0 will be masked
            self.mask = mask != 0
            interface.logging.info(f"Mask file {mask_path} loaded.")
        except ValueError:
            interface.logging.exception(
                f"Mask file could not be opened. {mask_path} Choose valid mask file or use automask."
            )
            raise Exception(f"Mask file could not be opened. {mask_path} Choose valid mask file or use automask.")
        self.mask_path = mask_path
        try:
            self.mask_creation = datetime.fromtimestamp(
                os.path.getmtime(mask_path)
            ).strftime("%Y-%m-%d %H:%M:%S")
            interface.logging.info(f"Creation date of mask file: {self.mask_creation}")
        except:
            self.mask_creation = "error"
            interface.logging.warning(f"Creation date of mask file could not be read.")
        interface.results.add_result(
            variable="mask_creation_date",
            parameter="creation date of mask file",
            value=self.mask_creation,
        )
        self.mask_height, self.mask_width = self.mask.shape[0], self.mask.shape[1]
        if not (self.height == self.mask_height) and (self.width == self.mask_width):
            logging.interface.exception(
                f"Dimensions of photo and mask file do not coincide ({(self.width, self.height)} vs {(self.mask_width, self.mask_height)})."
            )
            raise Exception(
                f"Dimensions of photo and mask file do not coincide ({(self.width, self.height)} vs {(self.mask_width, self.mask_height)})."
            )
        else:
            interface.logging.info(f"The mask has the right dimensions for the photo.")

    def automask(self, grow: float = 0.65, save: bool = False) -> None:
        """
        Create automask for photo and set attribute 'mask'.

        Args:
            thresh (Union[str,int], optional):
                    Threshold brightness value for binarization step.
                    "auto" for triangle algorithm.
                    Defaults to "auto".
            grow (float): threshold point for final rebinarization
                (0.5 <= grow < 1)
            save (bool): save to file
        """
        if not (grow >= 0.5) and (grow < 1):
            interface.logging.exception(
                f"Grow value must be 0.5 <= grow < 1, not {grow}."
            )
            raise ValueError(f"Grow value must be 0.5 <= grow < 1, not {grow}.")
        edge_length = min(self.width, self.height)

        binarized_photo = (
            photo_holes_removed
        ) = photo_objects_removed = hull = hull2 = hull3 = None

        def binarize_photo(thresh_value: Union[str, int] = "auto") -> None:
            """
            Binarize photo and set attribute "thresh_value" and
            nonlocal "binarized_photo".

            Args:
                thresh (Union[str,int], optional):
                    Threshold brightness value.
                    "auto" for triangle algorithm.
                    Defaults to "auto".
            """
            nonlocal binarized_photo
            thresh = (
                sm.filters.threshold_triangle(
                    sm.util.img_as_ubyte(sm.color.rgb2gray(self.photo))
                )
                if thresh_value == "auto"
                else thresh_value
            )
            interface.logging.info(
                f"Threshold point set to {thresh}"
                f"{' (auto).' if thresh_value == 'auto' else '.'}"
            )
            self.thresh_value = thresh
            interface.results.add_result(
                variable="thresh_value",
                parameter="threshold value for binarization of",
                value=self.thresh_value,
            )
            self.binarization_method = "auto" if thresh_value == "auto" else "manual"
            interface.results.add_result(
                variable="binarization_method",
                parameter="binarization method for",
                value=self.thresh_value,
            )
            binarized_photo = (
                sm.util.img_as_ubyte(sm.color.rgb2gray(self.photo)) > thresh
            )
            interface.logging.info(f"Created binarized photo (threshold = {thresh}).")

        if interface.user_settings.binarize_auto["value"] == True:
            thresh_value = "auto"
        else:
            thresh_value = interface.user_settings.binarize_threshold["value"]
        binarize_photo(thresh_value)

        def automask_hole_removal() -> None:
            nonlocal photo_holes_removed
            photo_holes_removed = sm.morphology.remove_small_holes(
                binarized_photo, area_threshold=(edge_length / 24) ** 2
            )

        def automask_object_removal() -> None:
            nonlocal photo_objects_removed
            photo_objects_removed = sm.morphology.remove_small_objects(
                photo_holes_removed, min_size=(edge_length / 16) ** 2
            )

        def automask_opening_disk() -> None:
            nonlocal hull
            footprint_disk = sm.morphology.disk(10)
            hull = sm.morphology.binary_opening(
                photo_objects_removed, footprint_disk
            )  # MUCH faster than non-binary

        def automask_opening_square() -> None:
            nonlocal hull2
            footprint_square = sm.morphology.square(10)
            hull2 = sm.morphology.binary_opening(hull, footprint_square)

        def automask_gaussian() -> None:
            nonlocal hull3
            hull3 = sm.filters.gaussian(hull2, 3)

        def automask_final_binarization() -> None:
            self.mask = (
                hull3 > grow
            )  # Grow the mask image a bit by setting threshpoint > 0.5.

        automask_function_list = [
            automask_hole_removal,
            automask_object_removal,
            automask_opening_disk,
            automask_opening_square,
            automask_gaussian,
            automask_final_binarization,
        ]
        for function in interface.progressBar(
            automask_function_list, prefix="Automask:", suffix="complete", length=50
        ):
            function()
        self.mask_height, self.mask_width = self.mask.shape[0], self.mask.shape[1]
        interface.logging.info(f"Successfully created automask.")
        if save:
            self.save_image(self.mask, "automask")

    def add_mask(self) -> None:
        """
        Add mask by either mask_file() or automask().

        Attr.:
            unmasked_pixels: number of unmasked pixels
            masked_pixels: number of masked pixels
            percentage_nonmasked: percentage of nonmasked pixels
        """
        if interface.user_settings.automask["value"]:
            self.automask(
                grow=interface.user_settings.automask_grow["value"],
                save=interface.user_settings.automask_save["value"],
            )
        elif interface.user_settings.automask["value"] == False:
            self.mask_file(interface.user_settings.mask_file["value"])
        else:
            interface.logging.exception(f"Missing valid setting for 'automask'.")
            raise ValueError(f"Missing valid setting for 'automask'.")
        self.unmasked_pixels = np.count_nonzero(self.mask)
        self.masked_pixels = np.count_nonzero(np.invert(self.mask))
        self.percentage_nonmasked = (
            100 * self.unmasked_pixels / (self.unmasked_pixels + self.masked_pixels)
        )
        interface.logging.info(
            f"{self.unmasked_pixels} of {self.masked_pixels} pixels are not masked ({round(self.percentage_nonmasked, 2)}%)."
        )
        interface.results.add_result(
            variable="percentage_nonmasked",
            parameter="percentage of masked pixels",
            value=self.percentage_nonmasked,
        )

    def get_orientation(self) -> None:
        """
        Calculate photo orientation and set attribute "orientation" based on automask.
        """
        if not "mask" in self.__dict__.keys():
            interface.logging.exception(
                f'You must first provide a mask file or create automask using "mask" or "automask" method.'
            )
            raise ValueError(
                f'You must first provide a mask file or create automask using "mask" or "automask" method.'
            )
        patch_label = sm.morphology.label(self.mask, connectivity=2)
        try:
            self.orientation = sm.measure.regionprops(patch_label)[0].orientation - np.pi/2
        except:
            interface.logging.exception(
                f"There is a problem with the mask. Cannot determine its orientation."
            )
            raise Exception(
                f"There is a problem with the mask. Cannot determine its orientation."
            )
        interface.logging.info(f"The orientation of the patch is {self.orientation}.")

    def rotate_photo_mask(self) -> None:
        """
        Rotate the image so that the main axis is horizontal.
        """
        if not "mask" in self.__dict__.keys():
            interface.logging.exception(
                f'You must first provide a mask file or create automask using "mask" or "automask" method.'
            )
            raise ValueError(
                f'You must first provide a mask file or create automask using "mask" or "automask" method.'
            )
        if not "orientation" in self.__dict__.keys():
            interface.logging.exception(
                f'You must first get orientation of patch using "orientation" method.'
            )
            raise ValueError(
                f'You must first get orientation of patch using "orientation" method.'
            )
        if interface.user_settings.autorotate['value']:
            self.photo = sm.transform.rotate(
                self.photo, -self.orientation * 180 / np.pi -180
            )
            interface.logging.info(f"Rotated photo by {-self.orientation}.")
            self.mask = sm.transform.rotate(
                self.mask, -self.orientation * 180 / np.pi -180
            )
            interface.logging.info(f"Rotated mask by {-self.orientation}.")
        
    def flip_photo_mask(self) -> None:
        """
        Flip the image.
        """
        if not "mask" in self.__dict__.keys():
            interface.logging.exception(
                f'You must first provide a mask file or create automask using "mask" or "automask" method.'
            )
            raise ValueError(
                f'You must first provide a mask file or create automask using "mask" or "automask" method.'
            )
        if interface.user_settings.flip['value']:
            self.photo = sm.transform.rotate(
                self.photo, 180
            )
            interface.logging.info(f"Rotated photo by 180°.")
            self.mask = sm.transform.rotate(
                self.mask, 180
            )
            interface.logging.info(f"Rotated mask by 180°.")                

    def maskview(self, output: str = None) -> None:
        """
        Create maskview image and sets attribute.
        Possibility for user prompt if ok and image saving.

        Args:
            output (str, optional):
                "save" for save file,
                "prompt" for save file and prompt user if ok.
                Defaults to None.
        """
        if output == None:
            return None
        if not "mask" in self.__dict__.keys():
            interface.logging.exception(
                f'You must first provide a mask file or create automask using "mask" or "automask" method.'
            )
            raise ValueError(
                f'You must first provide a mask file or create automask using "mask" or "automask" method.'
            )
        if not output in ["save", "prompt", None]:
            interface.logging.exception(
                f'Parameter "ouput" can only be "save", "prompt" and None.'
            )
            raise ValueError(
                f'Parameter "ouput" can only be "save", "prompt" and None.'
            )
        gray_photo = sm.util.img_as_ubyte(sm.color.rgb2gray(self.photo))
        # narrow brightness values to be able to see the red/green color in all areas
        photo_narrowed_brightness = sm.exposure.rescale_intensity(
            gray_photo, out_range=(80, 230)
        )
        red_multiplier = [1, 0, 0]
        green_multiplier = [0, 1, 0]
        rgb_image = sm.color.gray2rgb(photo_narrowed_brightness) / 255
        red_image = red_multiplier * rgb_image
        green_image = green_multiplier * rgb_image
        hull2_3d = np.expand_dims(self.mask, 2)
        self.maskview = sm.util.img_as_ubyte(
            red_image * ~hull2_3d + green_image * hull2_3d
        )
        if (output == "save") or (output == "prompt"):
            self.save_image(self.maskview, "maskview")
        if output == "prompt":
            self.open_image_os("maskview.tiff")
            interface.logging.info(
                f"Showing masked photo and dialog for operator check if masking was applied correctly."
            )
            mask_ok = interface.messagebox.askyesno(
                "Is the masking ok?",
                "Please have a look at file "
                + os.path.splitext(self.photo_path)[0]
                + "_maskview.tiff. Is the mask applied correctly?",
            )
            if mask_ok:
                self.mask_ok = True
                interface.logging.info(
                    "The user confirmed that the mask is applied correctly. Continuing..."
                )
            else:
                interface.logging.exception(
                    "The user answered that the masking was not correct. Exiting program. Please correct mask file or change automask parameters."
                )
                raise Exception(
                    "The user answered that the masking was not correct. Exiting program. Please correct mask file or change automask parameters."
                )

    def autocrop(self, photo, margin: int = 40, save: str = None) -> None:
        """
        Crop photo based on masked areas in mask leaving the given additional margin.
        Optionally saves cropped photo.

        Args:
            photo (_type_): _description_
            margin (int, optional): _description_. Defaults to 40.
            save (str, optional): don't save (None), save cropped photo ('photo'),
                save cropped_masked_photo ('masked'),
                save photo, mask, cropped mask ('all')

        Returns:
            np.ndarray: masked cropped photo

        Attribs:
            cropped_photo: cropped photo
            cropped_mask: cropped mask
            masked_cropped_photo: masked cropped photo
        """

        def get_crop_edges(binary_mask: np.ndarray) -> tuple:
            """
            Calculate the amount of masked pixels from all four directions
            of a mask file (for identifying patch/cropping to patch).

            Args:
                binary_mask (np.ndarray): mask for evaluation

            Returns:
                tuple: top, bottom, left, and right borders
            """
            # get the indices of the non-zero elements in the mask (patch area)
            self.save_image(binary_mask, "binary_mask")
            indices_not_masked = np.nonzero(binary_mask)
            indices_y = indices_not_masked[0]  # indices along the first axis
            indices_x = np.sort(
                indices_not_masked[1]
            )  # indices along the second axis, needs to be sorted
            # get the four indices from the first and last elements of the arrays
            top_edge = indices_y[0]
            bottom_edge = (
                binary_mask.shape[0] - indices_y[-1] - 1
            )  # needs to be one less because it will be cut off
            left_edge = indices_x[0]
            right_edge = (
                binary_mask.shape[1] - indices_x[-1] - 1
            )  # needs to be one less because it will be cut off
            crop_edges = (top_edge, bottom_edge, left_edge, right_edge)
            return crop_edges

        def dimensions_patch(photo: np.ndarray, crop_edges: tuple) -> tuple:
            """
            Calculate size parameters for photo after cropping to patch
            and return height and width in mm.

            Args:
                photo (np.ndarray): photo to crop
                crop_edges (tuple): pixels top, bottom, left, right to cut off

            Returns:
                tuple: (patch height in mm, patch width in mm)

            Attribs:
                height_patch: height of patch in pixels
                width_patch: width of patch in pixels
                height_patch_mm: height of patch in mm
                width_patch_mm: width of patch in mm
                percent_patch_photo: percent patch area of total photo
            """
            top_edge, bottom_edge, left_edge, right_edge = crop_edges
            self.height_patch = photo.shape[0] - top_edge - bottom_edge
            self.width_patch = photo.shape[1] - left_edge - right_edge
            self.height_patch_mm = self.height_patch / SCALE_FACTOR
            self.width_patch_mm = self.width_patch / SCALE_FACTOR
            self.percent_patch_photo = (
                100 * self.height_patch * self.width_patch / self.height / self.width
            )
            interface.logging.info(
                f"The patch is {round(self.height_patch_mm,1)} mm high and {round(self.width_patch_mm,1)} mm wide "
                f"({self.height_patch} and {self.width_patch} pixels). "
                f"The patch area is {round(self.percent_patch_photo,1)}% of the total photo area (excluding margin)."
            )
            return (self.height_patch_mm, self.width_patch_mm)

        def crop_photo(photo, edges: tuple, margin: int = 40) -> np.ndarray:
            """
            Crop photo by cutting off pixel number defined in "edges" (minus "margin") from all four edges.
            Variable "edges" must be a tuple of 4 positive integers corresponding to the number of pixels to cut off.

            Args:
                photo (_type_): Photo to crop
                edges (tuple): Positive integers corresponding to the number of pixels to cut off.
                margin (int, optional): Number of additional pixels to leave. Defaults to 40.

            Returns:
                np.ndarray: cropped photo
            """
            smaller_side = min(photo.shape[0], photo.shape[1])
            if not margin >= 0 and margin <= smaller_side / 2:
                raise ValueError(
                    f"Margin must be between 0 and half the smaller photo side."
                )
            if (
                not len(edges) == 4
                and np.product([type(i) == int for i in edges])
                and np.product([i > 0 for i in edges])
                and type(edges) == tuple
            ):
                interface.logging.exception(
                    f"Edges must be a tuple of 4 positive integers."
                )
                raise ValueError(f"Edges must be a tuple of 4 positive integers.")
            y1, y2, x1, x2 = edges
            if not y1 + y2 + margin * 2 < photo.shape[0]:
                interface.logging.exception(
                    f"Cannot cut off more than the photo height (top, bottom and twice the margin). Photo height is {height}. You want to cut off {y1 + y2 + margin * 2} pixels."
                )
                raise ValueError(
                    f"Cannot cut off more than the photo height (top, bottom and twice the margin). Photo height is {height}. You want to cut off {y1 + y2 + margin * 2} pixels."
                )
            if not x1 + x2 + margin * 2 < photo.shape[1]:
                interface.logging.exception(
                    f"Cannot cut off more than the photo height (top, bottom and twice the margin). Photo height is {width}. You want to cut off {x1 + x2 + margin * 2} pixels."
                )
                raise ValueError(
                    f"Cannot cut off more than the photo height (top, bottom and twice the margin). Photo height is {width}. You want to cut off {x1 + x2 + margin * 2} pixels."
                )
            if len(photo.shape) == 3:
                cropped_photo = sm.util.crop(
                    photo,
                    ((y1 - margin, y2 - margin), (x1 - margin, x2 - margin), (0, 0)),
                    copy=False,
                )
            elif len(photo.shape) == 2:
                cropped_photo = sm.util.crop(
                    photo,
                    ((y1 - margin, y2 - margin), (x1 - margin, x2 - margin)),
                    copy=False,
                )
            else:
                interface.logging.exception(
                    f"There is a problem. Photo must be 2 or 3 dimensional."
                )
                raise Exception(
                    f"There is a problem. Photo must be 2 or 3 dimensional."
                )
            return cropped_photo

        if not "mask" in self.__dict__.keys():
            interface.logging.exception(
                f'You must first provide a mask file or create automask using "mask" or "automask" method.'
            )
            raise ValueError(
                f'You must first provide a mask file or create automask using "mask" or "automask" method.'
            )
        edges = get_crop_edges(self.mask)
        dimensions_patch(photo, edges)
        self.cropped_photo = crop_photo(photo, edges, margin)
        interface.logging.info(f"Created cropped photo with {margin} pixels margin.")
        self.cropped_mask = crop_photo(self.mask, edges, margin)
        interface.logging.info(
            f"Cropped corresponding mask file with {margin} pixels margin."
        )
        self.masked_cropped_photo = self.cropped_photo * np.expand_dims(
            self.cropped_mask, 2
        )
        if save not in {None, "photo", "masked", "all"}:
            interface.logging.exception(
                f"Possible values for 'save' are None, 'photo', 'masked', and 'all'."
            )
            raise ValueError(
                f"Possible values for 'save' are None, 'photo', 'masked', and 'all'."
            )
        if save == "photo":
            self.save_image(self.cropped_photo, "cropped_photo")
        if save == "masked":
            self.save_image(self.masked_cropped_photo, "masked_cropped")
        if save == "all":
            self.save_image(self.cropped_photo, "cropped_photo")
            self.save_image(self.masked_cropped_photo, "masked_cropped")
            self.save_image(self.cropped_mask, "cropped_mask")
        return self.masked_cropped_photo


def run_photo() -> None:
    """Execute the photo functions."""
    global photo
    photo = Photo(interface.user_settings.photo_file["value"])
    photo.basic_attribs()
    photo.check_exif()
    photo.add_mask()
    photo.flip_photo_mask()
    photo.get_orientation()
    photo.rotate_photo_mask()
    photo.maskview(output=interface.user_settings.maskview["value"])
    photo.autocrop(
        photo.photo,
        margin=interface.user_settings.autocrop_margin["value"],
        save=interface.user_settings.autocrop_save["value"],
    )


# ------------------------------------------------
# executions

is_main = __name__ == "__main__"

if is_main:
    interface.run_interface()
    photo = Photo(interface.user_settings.photo_file["value"])
    photo.basic_attribs()
    photo.check_exif()
    photo.add_mask()
    photo.flip_photo_mask()
    photo.get_orientation()
    photo.rotate_photo_mask()
    photo.maskview(output=interface.user_settings.maskview["value"])
    photo.autocrop(
        photo.photo,
        margin=interface.user_settings.autocrop_margin["value"],
        save=interface.user_settings.autocrop_save["value"],
    )
