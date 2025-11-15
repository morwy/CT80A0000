#!/usr/bin/env python3

import logging
from dataclasses import dataclass
from enum import Enum

import mysql.connector
from mysql.connector import Error


@dataclass
class DatabaseInformation:
    """
    Holds information required to connect to a database.
    """

    host: str = "127.0.0.1"
    port: int = 0
    name: str = ""
    user: str = "root"
    password: str = "SuperSecureMilitaryPassword"
    timeout_seconds: int = 5


class FrontendApplication:
    """
    Frontend application that works with multiple databases.
    """

    def __init__(self):
        logging.info("Frontend application initialized.")

        # Disable MySQL connector debug logs
        logging.getLogger("mysql").setLevel(logging.WARNING)
        logging.getLogger("mysql.connector").setLevel(logging.WARNING)

        self.__connect_to_databases()

        while True:
            try:
                logging.info(
                    "-------------- Loop started, press Ctrl+C to exit --------------"
                )
                self.__selected_db = self.__ask_to_select_database()
                self.__selected_table = self.__ask_to_select_table(self.__selected_db)
                self.__do_action_with_database(
                    self.__selected_db, self.__selected_table
                )

            except KeyboardInterrupt:
                logging.info("Application interrupted by user.")
                raise

            except Error as e:
                logging.error("Database error occurred: %s", e)

    def __del__(self):
        logging.info("Shutting down frontend application.")
        self.__disconnect_from_databases()

    def __connect_to_databases(self):
        logging.info("Connecting to databases.")

        self.__databases = [
            DatabaseInformation(name="radar1_db", port=33061),
            DatabaseInformation(name="radar2_db", port=33062),
            DatabaseInformation(name="radar3_db", port=33063),
        ]

        self.__db_connections = {}

        for database in self.__databases:
            conn = mysql.connector.connect(
                host=database.host,
                port=database.port,
                user=database.user,
                password=database.password,
                database=database.name,
                connection_timeout=database.timeout_seconds,
            )

            if conn.is_connected():
                self.__db_connections[database.name] = conn
                logging.info(
                    "Connected to MySQL database '%s' on %s:%s",
                    database.name,
                    database.host,
                    database.port,
                )

            else:
                logging.warning(
                    "Unable to establish connection to database '%s'", database.name
                )
                raise Error(f"Connection to database '{database.name}' failed.")

        logging.info("Connected to databases successfully.")

    def __disconnect_from_databases(self):
        logging.info("Disconnecting from databases.")

        for db, conn in self.__db_connections.items():
            if conn.is_connected():
                conn.close()
                logging.info("Disconnected from database '%s'", db)

        logging.info("Disconnected from databases successfully.")

    def __ask_to_select_database(self) -> str:
        logging.info("Available databases:")

        for idx, database in enumerate(self.__databases, start=1):
            logging.info(
                "  %d. %s (%s:%d)", idx, database.name, database.host, database.port
            )

        while True:
            entered_value = input("Select a database by number: ")

            if not entered_value.isdigit():
                logging.warning("Invalid selection. Please try again.")
                continue

            choice_idx = int(entered_value) - 1
            if not 0 <= choice_idx < len(self.__databases):
                logging.warning("Invalid selection. Please try again.")
                continue

            selected_db = self.__databases[choice_idx].name

            logging.info("Selected database: %s", selected_db)

            return selected_db

    def __ask_to_select_table(self, database_name: str) -> str:
        logging.info("Available tables:")

        conn = self.__db_connections.get(database_name)
        if conn is None or not conn.is_connected():
            logging.error("No active connection to database '%s'", database_name)
            return ""

        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        for idx, (table_name,) in enumerate(tables, start=1):
            logging.info("  %d. %s", idx, table_name)

        while True:
            entered_value = input("Select a table by number: ")

            if not entered_value.isdigit():
                logging.warning("Invalid selection. Please try again.")
                continue

            choice_idx = int(entered_value) - 1
            if not 0 <= choice_idx < len(tables):
                logging.warning("Invalid selection. Please try again.")
                continue

            selected_table = tables[choice_idx][0]

            logging.info("Selected table: %s", selected_table)

            return selected_table

    def __do_action_with_database(self, database_name: str, table_name: str):
        logging.info("Available actions:")

        class Action(Enum):
            """
            Actions that can be performed with the selected database.
            """

            SHOW_DATA = "Show data"
            UPDATE_DATA = "Update data"

        for idx, action in enumerate(Action, start=1):
            logging.info("  %d. %s", idx, action.value)

        while True:
            entered_value = input("Select an action by number: ")

            if not entered_value.isdigit():
                logging.warning("Invalid selection. Please try again.")
                continue

            choice_idx = int(entered_value) - 1
            if not 0 <= choice_idx < len(Action):
                logging.warning("Invalid selection. Please try again.")
                continue

            selected_action = list(Action)[choice_idx]

            logging.info("Selected action: %s", selected_action.value)

            if selected_action == Action.SHOW_DATA:
                self.__show_data(database_name, table_name)
            elif selected_action == Action.UPDATE_DATA:
                self.__update_data(database_name, table_name)

            break

    def __show_data(self, database_name: str, table_name: str):
        logging.info(
            "Showing data from database '%s' and table '%s'", database_name, table_name
        )

        conn = self.__db_connections.get(database_name)
        if conn is None or not conn.is_connected():
            logging.error("No active connection to database '%s'", database_name)
            return

        cursor = conn.cursor()

        cursor.execute(f"DESCRIBE {table_name};")
        columns = [row[0] for row in cursor.fetchall()]
        logging.info("(%s)", ", ".join(columns))

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        for row in rows:
            logging.info(row)

    def __update_data(self, database_name: str, table_name: str):
        logging.info(
            "Updating data in database '%s' and table '%s'", database_name, table_name
        )

        conn = self.__db_connections.get(database_name)
        if conn is None or not conn.is_connected():
            logging.error("No active connection to database '%s'", database_name)
            return

        logging.info("Available entries to update:")

        cursor = conn.cursor()

        cursor.execute(
            """
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = %s
                AND COLUMN_KEY = 'PRI';
            """,
            (database_name, table_name),
        )

        pk_columns = [row[0] for row in cursor.fetchall()]

        cursor.execute(f"DESCRIBE {table_name};")
        columns = [row[0] for row in cursor.fetchall()]
        logging.info("(%s)", ", ".join(columns))

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        for row in rows:
            logging.info(row)

        selected_entry_id = input("Enter the ID of the entry to update: ")
        selected_entry_column = input("Enter the column name to update: ")

        new_value = input("Enter the new value: ")

        cursor.execute(
            f"UPDATE {table_name} SET {selected_entry_column} = %s WHERE {pk_columns[0]} = %s",
            (new_value, selected_entry_id),
        )
        conn.commit()

        logging.info("Entry updated successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    app = FrontendApplication()
