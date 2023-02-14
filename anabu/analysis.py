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
except:
    import anabu.interface as interface
    import anabu.photo as photo
    import anabu.pinholes as pinholes
    import anabu.density as density
    import anabu.charts as charts
import os


# ------------------------------------------------
# parameters

version = "0.7"

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
    if interface.user_settings.batch_evaluation["value"]:
        for file in interface.user_settings.file_list["value"]:
            interface.user_settings.photo_file["value"] = file
            try:
                photo.run_photo()
                if interface.user_settings.pinholes["value"]:
                    pinholes.run_pinholes()
                density.run_density()
                charts.run_charts()
                interface.end_analysis()
            except:
                interface.logging.info(f"Error trying to evaluate file {file}.")
    else:
        photo.run_photo()
        if interface.user_settings.pinholes["value"]:
            pinholes.run_pinholes()
        density.run_density()
        charts.run_charts()
        interface.end_analysis()
    interface.logging.info("DONE.")
    print("\a")


# ------------------------------------------------
# executed code

if is_main:
    run_analysis_photo()
