#!/usr/bin/env python3

# ------------------------------------------------
# imports

import anabu.interface as interface

class photo:
    """Object defining the photo file and properties."""
    def __init__(self) -> None:
        self.photo = interface.open_photo(interface.user_settings.photo_file)
        pass