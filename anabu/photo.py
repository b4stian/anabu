#!/usr/bin/env python3

is_main = __name__ == "__main__"

# ------------------------------------------------
# imports

if is_main:
    import interface
else:
    import anabu.interface as interface
    
from PIL import \
    Image as PIL_Image, \
    ExifTags as PIL_ExifTags
import skimage as sm
import skimage as sm
import skimage.io as sm_io
from skimage.util import crop
from skimage.transform import rotate  

# ------------------------------------------------
# variables

# These are the supported photo types. Not tested, but it's very likely that other types will work out of the box when added to this list.
supported_types = ["MPO", "JPEG", "PNG", "TIFF"]
    
# ------------------------------------------------
# function/class definitions

class Photo:
    """
    Photo object for evaluation.
    """
    def __init__(self, photo_path:str) -> None:
        """
        Read photo and set as attribute. Use dilog if file not found.

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
        try:
            # read photo with skimage (for evaluation)
            self.photo = sm_io.imread(photo_path)
            interface.logging.info(f"File {photo_path} loaded.")
        except:
            interface.logging.exception(f"Photo file could not be loaded. {photo_path}")
            raise Exception(f"Photo file could not be loaded. {photo_path}")

    
    def __repr__(self) -> str:
        sm_io.imshow(self.photo)
        return f"Photo object for evaluation: shape: {self.photo.shape}."
    
if is_main:
    interface.run_interface()
    photo_eval = Photo(interface.user_settings.photo_file['value'])
    #print(photo_eval)
    print(photo_eval)
    
