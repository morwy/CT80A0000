#!/usr/bin/env python3

import logging
import os
import shutil
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

    mongodb_data_path = os.path.join(current_directory, "db", "radar-mongodb", "data")
    if os.path.exists(mongodb_data_path):
        logging.debug("Removing MongoDB data directory: %s", mongodb_data_path)
        shutil.rmtree(mongodb_data_path)
        os.makedirs(mongodb_data_path, exist_ok=True)

    logging.debug("Recreating and starting Docker containers.")

    result = subprocess.run(
        ["docker", "compose", "up", "-d"],
        cwd=current_directory,
        text=True,
        check=True,
    )

    logging.info("Databases recreated and Docker containers started successfully.")
