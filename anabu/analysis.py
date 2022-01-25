#!/usr/bin/env python3

import interface

version = "0.2.0"


def run():
    """Runs the whole analysis script."""
    interface.logging.info(
        "--------------------------------------------------------")
    interface.logging.info(
        f"anabu {str(version)}. Process started.")
    interface.logging.info(
        "--------------------------------------------------------")
    interface.logging.info(
        "In case of problems with this tool contact bastian.ebeling@kuraray.com.")
    interface.logging.info("Imports successful.")


if __name__ == "__main__":
    run()
