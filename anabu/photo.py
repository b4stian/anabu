#!/usr/bin/env python3

is_main = __name__ == "__main__"

# ------------------------------------------------
# imports

if is_main:
    import interface
else:
    import anabu.interface as interface
from datetime import datetime
from PIL import \
    Image as PIL_Image, \
    ExifTags as PIL_ExifTags
import os
import skimage as sm
import skimage.io as sm_io
from skimage.util import crop as sm_crop
from skimage.morphology import label as sm_label
from skimage.measure import regionprops as sm_regionprops
from skimage.transform import rotate as sm_rotate
from skimage.filters import threshold_triangle as sm_thresh_triangle
from typing import Union

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
    ["FocalLengthIn35mmFilm", "Focal length in 35 mm film in mm", None]
    ]
   

# ------------------------------------------------
# function/class definitions

class Photo:
    """
    Photo object for evaluation.
    """
    def __init__(self, photo_path:str) -> None:
        """
        Read photo and set as attributes. Use dialog if file not found.
        
        Read and save photo format and creation date.
        
        Set attributes:
            photo_path: path to loaded photo
            photo_check: photo loaded with PIL for EXIF checks
            photo: photo loaded with skimage for evaluation
            file_name: name of photo file (without extension)
            folder: folder of photo file
            gray_photo: 8-bit grayscale of photo

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
                variable = "photo_file_dialog",
                parameter = 'path to photo file selected with dialog',
                value = photo_file,
                )
            return photo_file
        
        self.photo_path = photo_path
        try:
            # read photo with PIL (for checks)
            self.photo_check = PIL_Image.open(photo_path)
        except FileNotFoundError:
            interface.logging.info(f"File {photo_path} not found.")
            photo_path = photo_dialog()  
        except AttributeError:
            interface.logging.warning(f"Filename {photo_path} could not be read.")
            photo_path = photo_dialog()          
        try:
            self.photo_check = PIL_Image.open(photo_path)
            interface.logging.info(f"File {photo_path} found.")
        except AttributeError:
            interface.logging.exception(f"No valid photo file selected.")
            raise Exception(f"No valid photo file selected.")
        self.file_name = os.path.splitext(os.path.basename(photo_path))[0]
        try:
            # read photo with skimage (for evaluation)
            self.photo = sm_io.imread(photo_path)
            interface.logging.info(f"File {photo_path} loaded.")
        except:
            interface.logging.exception(f"Photo file could not be loaded. {photo_path}")
            raise Exception(f"Photo file could not be loaded. {photo_path}")
        self.folder = os.path.splitext(photo_path)[0]
        self.gray_photo = sm.util.img_as_ubyte(sm.color.rgb2gray(self.photo))

    def __repr__(self) -> str:
        sm_io.imshow(self.photo)
        return f"Photo object for evaluation: shape: {self.photo.shape}."     
    
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
            interface.logging.info(f'Selected photo has the image type "{self.format}".')
            interface.results.add_result(
                variable = "image_type" + self.file_name,
                parameter = 'image type of photo file ' + self.file_name,
                value = self.format,
                )
        except:
            interface.logging.warning(f"Could not read format of photo file.")
        if self.format in supported_types:
            interface.logging.info(f'The image type "{self.format}" is supported.')
        else:
            interface.logging.exception(f'The image type "{self.format}" is not supported.')
            raise TypeError(f'The image type "{self.format}" is not supported.')
        try:
            self.creation_date = datetime.fromtimestamp(
                os.path.getmtime(self.photo_path)
                ).strftime(
                    "%Y-%m-%d %H:%M:%S"
                    )  #This is better manually and not from EXIF.
            interface.logging.info(f'Selected photo has the creation date "{self.creation_date}".')
            interface.results.add_result(
                variable = "creation_date_" + self.file_name,
                parameter = 'creation date of photo file ' + self.file_name,
                value = self.creation_date,
                )
        except:
            interface.logging.warning(f"Could not read creation date of photo file.")
        if bool(interface.user_settings.sample_name['value']):
            self.sample_name = interface.user_settings.sample_name['value']
            interface.logging.info(f'The sample name is "{self.sample_name}".')
        else:
            self.sample_name = self.file_name
            interface.logging.info(f'No sample name given. Using file name "{self.file_name}" as the sample name.')
        interface.results.add_result(
                variable = 'sample_name_' + self.file_name,
                parameter = 'sample name of photo file ' + self.file_name,
                value = self.sample_name,
                )
        self.height, self.width = self.photo.shape[0], self.photo.shape[1]
        interface.logging.info(f"The photo has the width and height of {self.photo.shape[1]} and {self.photo.shape[0]} pixels.")
        interface.results.add_result(
                variable = 'width_' + self.file_name,
                parameter = 'width of photo file ' + self.file_name,
                value = self.photo.shape[1],
                )
        interface.results.add_result(
                variable = 'height_' + self.file_name,
                parameter = 'height of photo file ' + self.file_name,
                value = self.photo.shape[0],
                )   
    
    @staticmethod
    def get_EXIF_targets() -> list:
        """
        Returns:
            list: EXIF targets from user settings
        """
        EXIF_tags_targets = {
            "Make": interface.user_settings.target_Make['value'],
            "Model": interface.user_settings.target_model['value'],
            "BrightnessValue": interface.user_settings.target_BrightnessValue['value'],
            "ExifImageWidth": interface.user_settings.target_ExifImageWidth['value'],
            "ExifImageHeight": interface.user_settings.target_ExifImageHeight['value'],
            "FocalLength": interface.user_settings.target_FocalLength['value'],
            "ExposureTime": interface.user_settings.target_ExposureTime['value'],
            "FNumber": interface.user_settings.target_FNumber['value'],
            "LensModel": interface.user_settings.target_LensModel['value'],
            "ISOSpeedRatings": interface.user_settings.target_ISOSpeedRatings['value'],
            "WhiteBalance": interface.user_settings.target_WhiteBalance['value'],
            "MeteringMode": interface.user_settings.target_MeteringMode['value'],
            "DigitalZoomRatio": interface.user_settings.target_DigitalZoomRatio['value'],
            "FocalLengthIn35mmFilm": interface.user_settings.target_FocalLengthIn35mmFilm['value'],
            }
        return EXIF_tags_targets
    
    def check_exif(self) -> bool:
        """
        Check the EXIF data of the photo file and compare with target parameters.

        Returns:
            bool: EXIF data coincide with targets.
        """
        image_exif = self.photo_check._getexif()  #doesn't find all exif data with .getexif(), older method seems to be ok
        exif_tag_dict = {}
        for key, val in image_exif.items():
            if key in PIL_ExifTags.TAGS:
                exif_tag_dict[PIL_ExifTags.TAGS[key]] = val 
        interface.logging.info("Extracted EXIF data from photo file.")
        EXIF_tags_targets = Photo.get_EXIF_targets()
        for tagno in range(len(EXIF_tags)):
            try:
                EXIF_tags[tagno][2] = exif_tag_dict[ EXIF_tags[tagno][0]  ]
                interface.logging.info(f'EXIF tag "{EXIF_tags[tagno][0]}" found. {EXIF_tags[tagno][1]} is {EXIF_tags[tagno][2]}.')
                interface.results.add_result(
                    variable = EXIF_tags[tagno][0] + self.file_name,
                    parameter = EXIF_tags[tagno][1] + " " + self.file_name,
                    value = EXIF_tags[tagno][2],
                    )
            except:
                logging.warning(f'EXIF tag "{EXIF_tags[tagno][0]}" not found. Value cannot be recorded, but script will continue.')
                interface.results.add_result(
                    variable = EXIF_tags[tagno][0] + self.file_name,
                    parameter = EXIF_tags[tagno][1] + " " + self.file_name,
                    value = EXIF_tags[tagno][2],
                    )
            if not EXIF_tags_targets[EXIF_tags[tagno][0]]:
                interface.logging.info(f'There is no target for "{EXIF_tags[tagno][0]}" defined in settings.')
            else:
                if EXIF_tags[tagno][2] == EXIF_tags_targets[EXIF_tags[tagno][0]]:
                    interface.logging.info(f'There is a target for "{EXIF_tags[tagno][0]}". It coincides with the extracted value.')
                else:
                    interface.logging.exception(f"The target for {EXIF_tags[tagno][0]} is {EXIF_tags_targets[EXIF_tags[tagno][0]]}." \
                        f"A different value was extracted: {EXIF_tags[tagno][2]}." \
                        f"Exiting evaluation.")
                    raise Exception(f"The target for {EXIF_tags[tagno][0]} is {EXIF_tags_targets[EXIF_tags[tagno][0]]}." \
                        f"A different value was extracted: {EXIF_tags[tagno][2]}. Exiting evaluation.") 
            interface.logging.info(f"All EXIF tags extracted successfully for {self.file_name}. No conflict with target values.")
            interface.results.add_result(
                variable = "EXIF_check_" + self.file_name,
                parameter = "EXIF check for " + self.file_name,
                value = True,
                )
            return True
        
    def binarize_photo(self, thresh_value: Union[str,int] = "auto") -> None:
        """
        Binarize photo and set attributes 
        "thresh_value" and "binarized_photo". 
                            
        Args:
            thresh (Union[str,int], optional): 
                Threshold brightness value.
                "auto" for triangle algorithm.
                Defaults to "auto".
        """
        thresh = sm_thresh_triangle(self.gray_photo) \
            if thresh_value == "auto" else thresh_value 
        interface.logging.info(f"Threshold point set to {thresh}." \
            f"{' (auto).' if thresh_value == 'auto' else '.'}")
        self.thresh_value = thresh
        interface.results.add_result(
            variable = "thresh_value_" + self.file_name,
            parameter = "threshold value for binarization of " + self.file_name,
            value = self.thresh_value,
            )
        self.binarization_method = "auto" if thresh_value == "auto" else "manual"
        interface.results.add_result(
            variable = "binarization_method_" + self.file_name,
            parameter = "binarization method for " + self.file_name,
            value = self.thresh_value,
            )
        self.binarized_photo = self.gray_photo > thresh
        interface.logging.info(f"Created binarized photo (threshold = {thresh}).")
        
    def automask(self, grow:float = 0.65, save:bool = False) -> None:
        """
        Create automask for photo.

        Args:
            grow (float): threshold point for final rebinarization
                (0.5 <= grow < 1)
            save (bool): save to file
        """
        interface.logging.info("Creating automask...")
        if not "binarized_photo" in self.__dict__.keys():
            interface.logging.exception(f'You must first create binarized photo using "binarize()" method.')
            raise ValueError(f'You must first create binarized photo using "binarize()" method.')         
        if not (grow >= 0.5) and (grow < 1):
            interface.logging.exception(f"Grow value must be 0.5 <= grow < 1, not {grow}.")
            raise ValueError(f"Grow value must be 0.5 <= grow < 1, not {grow}.")
        edge_length = min(self.width, self.height)
        photo_holes_removed = sm.morphology.remove_small_holes(self.binarized_photo, area_threshold=(edge_length/24)**2)
        photo_objects_removed = sm.morphology.remove_small_objects(photo_holes_removed, min_size=(edge_length/16)**2)
        footprint_disk = sm.morphology.disk(10)
        hull = sm.morphology.binary_opening(photo_objects_removed, footprint_disk)  #MUCH faster than non-binary
        footprint_square = sm.morphology.square(10)
        hull2 = sm.morphology.binary_opening(hull, footprint_square)
        hull3 = sm.filters.gaussian(hull2, 3)
        self.automask = hull3 > grow  #Grow the mask image a bit by setting threshpoint > 0.5.
        interface.logging.info(f"Successfully created automask.")
        if save:
            sm.io.imsave(os.path.splitext(self.photo_path)[0] + '_automask.tiff', sm.util.img_as_ubyte(self.automask))
            interface.logging.info(f"Saved automask to {os.path.splitext(self.photo_path)[0] + '_automask.tiff'}.")
        
    
    def orientation(self) -> None:
        """
        Calculate photo orientation and set attribute "orientation" based on automask.
        """
        if not "automask" in self.__dict__.keys():
            interface.logging.exception(f'You must first create automask using "automask()" method.')
            raise ValueError(f'You must first create automask first using "automask()" method.')  
        pass #incomplete     
    
    def rotate(self) -> None:
        """
        Rotate the photo so that the main axis is horizontal.
        """
        pass
            
    
if is_main:
    interface.run_interface()
    photo = Photo(interface.user_settings.photo_file['value'])
    photo.basic_attribs()
    photo.check_exif()
    photo.binarize_photo("auto")
    photo.automask(0.65, True)
    print(photo.folder)
    
