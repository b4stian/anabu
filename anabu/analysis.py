#!/usr/bin/env python3

is_main = __name__ == "__main__"

# ------------------------------------------------
# imports

try:
    import interface
    import photo
    import pinholes
    import density
except:
    import anabu.interface as interface
    import anabu.photo as photo
    import anabu.pinholes as pinholes
    import anabu.density as density
import os



# ------------------------------------------------
# parameters

version = "0.6"

# ------------------------------------------------
# function/class definitions


def run_analysis_photo():
    """Runs the whole analysis script."""
    interface.set_up_logging()
    interface.logging.info("--------------------------------------------------------")
    interface.logging.info(f"anabu {str(version)}. Process started.")
    interface.logging.info("--------------------------------------------------------")
    interface.logging.info(
        "In case of problems with this tool contact bastian.ebeling@kuraray.com."
    )
    interface.logging.info("Main imports successful.")
    interface.run_interface()
    photo.run_photo()
    pinholes.run_pinholes()
    density.run_density()
    interface.end_analysis()
    interface.logging.info("DONE.")
    print('\a')


# ------------------------------------------------
# executed code

if is_main:
    run_analysis_photo()
