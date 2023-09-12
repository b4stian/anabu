#!/usr/bin/env python3

is_main = __name__ == "__main__"

# ------------------------------------------------
# imports

try:
    import charts
    import density
    import interface
    import photo
    import pinholes

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


def run_button():
    """Runs the code when the run button in the GUI is pressed."""
    global progress_generator
    interface.clear_log_file()
    interface.initiate_results()
    interface.results.add_result(
        variable="version",
        parameter="version of anabu",
        value=interface.VERSION,
    )
    interface.Gui.initiate_progress_bar()
    interface.logging.info("--------------------------------------------------------")
    interface.logging.info(
        f"Pressed Run. anabu {str(interface.VERSION)}. Evaluation started."
    )
    interface.logging.info("--------------------------------------------------------")
    interface.Gui.set_settings_from_GUI()
    if interface.user_settings.batch_evaluation["value"]:
        try:
            file_list = interface.get_files_in_folder(
                interface.user_settings.photo_folder["value"]
            )
        except:
            file_list = interface.get_files_in_folder(interface.folder_dialog())
        interface.user_settings.set_sett_attribute(
            "file_list",
            {
                "variable": "file_list",
                "parameter": "list of files for evaluation",
                "value": file_list,
            },
        )
        interface.results.add_result(
            variable="file_list",
            parameter="photo files for batch evaluation",
            value=file_list,
        )
        interface.logging.info(
            f"Found {len(file_list)} photos for batch evaluation: {file_list}"
        )
    progress_generator = interface.Gui.generate_progress_steps()
    interface.Gui.update_progress_bar()
    interface.results.settings_to_results(interface.user_settings)
    if interface.user_settings.batch_evaluation["value"]:
        for file in interface.user_settings.file_list["value"]:
            interface.user_settings.photo_file["value"] = file
            try:
                photo.run_photo()
                if interface.user_settings.pinholes["value"]:
                    pinholes.run_pinholes()
                if interface.user_settings.analyze_brightness["value"]:
                    density.run_density()
                    charts.run_charts()
                    ppt.run_pptx()
                interface.end_analysis()
            except:
                interface.logging.info(f"Error trying to evaluate file {file}.")
    else:
        photo.run_photo()
        if interface.user_settings.pinholes["value"]:
            pinholes.run_pinholes()
        if interface.user_settings.analyze_brightness["value"]:
            density.run_density()
            charts.run_charts()
            ppt.run_pptx()
        interface.end_analysis()
    interface.Gui.update_progress_bar()
    interface.Gui.finish_progress_bar()
    interface.logging.info("DONE.")


def run_analysis_photo():
    """Runs the whole analysis script."""
    interface.set_up_logging()
    interface.logging.info("--------------------------------------------------------")
    interface.logging.info(f"anabu {str(interface.VERSION)}. Process started.")
    interface.logging.info("--------------------------------------------------------")
    interface.logging.info(
        "In case of problems with this tool contact bastian.ebeling@kuraray.com."
    )
    interface.logging.info("Main imports successful.")
    interface.run_interface()


# ------------------------------------------------
# executed code

if is_main:
    run_analysis_photo()
