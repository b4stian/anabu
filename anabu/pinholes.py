#!/usr/bin/env python3

"""
Pinhole evaluator
"""

is_main = __name__ == "__main__"

# ------------------------------------------------
# imports

# if is_main:
#     import interface
#     import photo
# else:
#     import anabu.interface as interface
#     import anabu.photo as photo

import numpy as np
import skimage as sm
import matplotlib.pyplot as plt

# ------------------------------------------------
# variables

# ------------------------------------------------
# function/class definitions

class Pinholer:
    """
    Find pinholes in photo.
    """

    def __init__(self, photo:np.ndarray, mask:np.ndarray) -> None:
        self.photo = photo
        self.mask = mask
        
def run_pinholes():
    pinholer = Pinholer(photo.photo.photo, photo.photo.mask)

# ------------------------------------------------
# executions

if is_main:
    #interface.run_interface()
    #photo.run_photo()
    run_pinholes()