#!/usr/bin/env python3

is_main = __name__ == "__main__"

# ------------------------------------------------
# imports

try:
    import interface
    import photo
    import pinholes
    import density
    import charts
    import ppt
except:
    import anabu.interface as interface
    import anabu.photo as photo
    import anabu.pinholes as pinholes
    import anabu.density as density
    import anabu.charts as charts
    import anabu.ppt as ppt
import os

# ------------------------------------------------
# function/class definitions


def run_analysis_photo():
    """Runs the whole analysis script."""
    interface.set_up_logging()
    interface.logging.info("--------------------------------------------------------")
    interface.logging.info(f"anabu {str(interface.VERSION)}. Process started.")
    interface.logging.info("--------------------------------------------------------")
    interface.logging.info(
        "In case of problems with this tool contact bastian.ebeling@kuraray.com."
    )
    interface.logging
    interface.logging.info("Main imports successful.")
    interface.run_interface()
    if interface.user_settings.batch_evaluation["value"]:
        for file in interface.user_settings.file_list["value"]:
            interface.user_settings.photo_file["value"] = file
            try:
                photo.run_photo()
                pinholes.run_pinholes()
                density.run_density()
                charts.run_charts()
                ppt.run_pptx()
                interface.end_analysis()
            except:
                interface.logging.info(f"Error trying to evaluate file {file}.")
    else:
        photo.run_photo()
        pinholes.run_pinholes()
        density.run_density()
        charts.run_charts()
        ppt.run_pptx()
        interface.end_analysis()
    interface.logging.info("DONE.")
    print("\a")


# ------------------------------------------------
# executed code

if is_main:
    run_analysis_photo()
