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

def run_button():
    """Runs the code when the run button in the GUI is pressed."""
    interface.clear_log_file()
    interface.logging.info("--------------------------------------------------------")
    interface.logging.info(f"Pressed Run. anabu {str(interface.VERSION)}. Evaluation started.")
    interface.logging.info("--------------------------------------------------------")
    interface.window['-PBAR-'].update(current_count=5)
    interface.Gui.set_settings_from_GUI()
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
        interface.window['-PBAR-'].update(current_count=20)
        if interface.user_settings.pinholes["value"]:
            pinholes.run_pinholes()
        if interface.user_settings.analyze_brightness["value"]:
            interface.window['-PBAR-'].update(current_count=30)
            density.run_density()
            interface.window['-PBAR-'].update(current_count=40)
            charts.run_charts()
            interface.window['-PBAR-'].update(current_count=60)
            ppt.run_pptx()
            interface.window['-PBAR-'].update(current_count=80)
        interface.end_analysis()
    interface.window['-PBAR-'].update(current_count=100)
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
