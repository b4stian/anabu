#!/usr/bin/env python3

import logging

# logging setup
logging.basicConfig(
    handlers=[
        logging.FileHandler("logfile.log", mode="w"),
        logging.StreamHandler(),
    ],
    format=("%(levelname)s (%(asctime)s): %(message)s"),
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    force=True,
)

