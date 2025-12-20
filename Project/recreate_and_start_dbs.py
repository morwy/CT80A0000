#!/usr/bin/env python3

import logging
import os
import subprocess

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")

    current_directory = os.path.dirname(os.path.abspath(__file__))
    logging.debug("Current directory: %s", current_directory)

    logging.debug("Stopping and removing Docker containers.")

    result = subprocess.run(
        ["docker", "compose", "down"],
        cwd=current_directory,
        text=True,
        check=True,
    )

    logging.debug("Recreating and starting Docker containers.")

    result = subprocess.run(
        ["docker", "compose", "up", "-d"],
        cwd=current_directory,
        text=True,
        check=True,
    )

    logging.info("Databases recreated and Docker containers started successfully.")
