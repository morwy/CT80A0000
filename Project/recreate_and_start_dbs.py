#!/usr/bin/env python3

import logging
import os
import shutil
import subprocess
import time

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

    db1_storage_path = os.path.join(current_directory, "db", "radar1")
    if os.path.exists(db1_storage_path):
        logging.debug("Removing database storage at: %s", db1_storage_path)
        shutil.rmtree(db1_storage_path, ignore_errors=True)
    os.makedirs(db1_storage_path, exist_ok=True)

    db2_storage_path = os.path.join(current_directory, "db", "radar2")
    if os.path.exists(db2_storage_path):
        logging.debug("Removing database storage at: %s", db2_storage_path)
        shutil.rmtree(db2_storage_path, ignore_errors=True)
    os.makedirs(db2_storage_path, exist_ok=True)

    db3_storage_path = os.path.join(current_directory, "db", "radar3")
    if os.path.exists(db3_storage_path):
        logging.debug("Removing database storage at: %s", db3_storage_path)
        shutil.rmtree(db3_storage_path, ignore_errors=True)
    os.makedirs(db3_storage_path, exist_ok=True)

    logging.debug("Recreating and starting Docker containers.")

    logging.debug("Starting first container.")

    result = subprocess.run(
        ["docker", "compose", "up", "-d", "radar1"],
        cwd=current_directory,
        text=True,
        check=True,
    )

    logging.debug("Waiting for the first container to become healthy.")

    TIMEOUT_SECS = 30
    INTERVAL_SECS = 1
    start_time = time.time()

    while True:
        try:
            result = subprocess.run(
                [
                    "docker",
                    "inspect",
                    "-f",
                    "{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}",
                    "radar1",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            status, health = result.stdout.strip().split()

            logging.debug("\tStatus: %s, Health: %s.", status, health)

            if status == "running" and health in ("healthy", "none"):
                logging.debug("\tContainer 'radar1' is up and healthy.")
                break

        except subprocess.CalledProcessError:
            logging.debug("\tContainer 'radar1' not available yet.")

        if time.time() - start_time > TIMEOUT_SECS:
            raise TimeoutError(
                f"Container 'radar1' did not become healthy within {TIMEOUT_SECS} seconds."
            )

        time.sleep(INTERVAL_SECS)

    logging.debug("Starting remaining containers.")

    result = subprocess.run(
        ["docker", "compose", "up", "-d", "radar2", "radar3"],
        cwd=current_directory,
        text=True,
        check=True,
    )

    logging.info("Databases recreated and Docker containers started successfully.")
