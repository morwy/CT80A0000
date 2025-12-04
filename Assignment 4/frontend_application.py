#!/usr/bin/env python3

import logging
from dataclasses import dataclass
from enum import Enum

import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient


class DatabaseType(Enum):
    """
    Enum for different database types.
    """

    UNKNOWN = "Unknown"
    MYSQL = "MySQL"
    MONGODB = "MongoDB"


@dataclass
class DatabaseInformation:
    """
    Holds information required to connect to a database.
    """

    db_type: DatabaseType = DatabaseType.UNKNOWN
    host: str = "127.0.0.1"
    port: int = 0
    name: str = "radar_db"
    user: str = "root"
    password: str = "SuperSecureMilitaryPassword"
    timeout_seconds: int = 5


class FrontendApplication:
    """
    Frontend application that works with multiple databases.
    """

    def __init__(self):
        logging.info("Frontend application initialized.")

        # Disable MySQL connector and MongoDB debug logs
        logging.getLogger("mysql").setLevel(logging.WARNING)
        logging.getLogger("mysql.connector").setLevel(logging.WARNING)
        logging.getLogger("pymongo").setLevel(logging.WARNING)

        self.__connect_to_databases()

        while True:
            try:
                logging.info(
                    "-------------- Loop started, press Ctrl+C to exit --------------"
                )
                self.__selected_table = self.__ask_to_select_table()
                self.__do_action_with_database(self.__selected_table)

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
            DatabaseInformation(db_type=DatabaseType.MYSQL, port=3306),
            DatabaseInformation(db_type=DatabaseType.MONGODB, port=27017),
        ]

        self.__db_connections = {}

        for database in self.__databases:
            if database.db_type == DatabaseType.MYSQL:
                conn = mysql.connector.connect(
                    host=database.host,
                    port=database.port,
                    user=database.user,
                    password=database.password,
                    database=database.name,
                    connection_timeout=database.timeout_seconds,
                )

                if conn.is_connected():
                    self.__db_connections[database.db_type] = conn
                    logging.info(
                        "Connected to MySQL database '%s' on %s:%s",
                        database.name,
                        database.host,
                        database.port,
                    )
                else:
                    logging.error(
                        "Unable to establish connection to database '%s'", database.name
                    )
                    raise Error(f"Connection to database '{database.name}' failed.")

            elif database.db_type == DatabaseType.MONGODB:
                mongo_uri = f"mongodb://{database.user}:{database.password}@{database.host}:{database.port}/?authSource=admin"
                client = MongoClient(
                    host=mongo_uri,
                    serverSelectionTimeoutMS=database.timeout_seconds * 1000,
                )

                self.__db_connections[database.db_type] = client
                logging.info(
                    "Connected to MongoDB database '%s' on %s:%s",
                    database.name,
                    database.host,
                    database.port,
                )
            else:
                logging.error(
                    "Unsupported database type '%s' for database '%s'",
                    database.db_type,
                    database.name,
                )
                raise Error(f"Unsupported database type '{database.db_type}'.")

        logging.info("Connected to databases successfully.")

    def __disconnect_from_databases(self):
        logging.info("Disconnecting from databases.")

        for db_type, conn in self.__db_connections.items():
            if db_type == DatabaseType.MYSQL:
                if conn.is_connected():
                    conn.close()

            elif db_type == DatabaseType.MONGODB:
                conn.close()

            logging.info("Disconnected from database '%s'", db_type)

        logging.info("Disconnected from databases successfully.")

    def __get_tables_in_database(self, requested_db_type: DatabaseType) -> list[str]:
        #
        # Well, it is the same database name in both systems.
        #
        database_name = self.__databases[0].name

        tables = []

        conn = self.__db_connections.get(requested_db_type)
        if conn is None:
            logging.error("No active connection to database '%s'", database_name)
            raise Error(f"No connection to database '{database_name}'.")

        if requested_db_type == DatabaseType.MYSQL:
            if conn is None or not conn.is_connected():
                logging.error("No active connection to database '%s'", database_name)
                return []

            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables_mysql = cursor.fetchall()

            for table in tables_mysql:
                if table not in tables:
                    tables.append(table)

        elif requested_db_type == DatabaseType.MONGODB:
            db = conn[database_name]
            tables_mongo = db.list_collection_names()
            for table in tables_mongo:
                if (table.upper(),) not in tables:
                    tables.append((table.upper(),))

        return [table[0] for table in tables]

    def __ask_to_select_table(self) -> str:
        logging.info("Available tables:")

        unique_tables = []
        for db_type, _ in self.__db_connections.items():
            tables = self.__get_tables_in_database(db_type)
            for table in tables:
                if table not in unique_tables:
                    unique_tables.append(table)

        unique_tables.sort()

        for idx, table_name in enumerate(unique_tables, start=1):
            logging.info("  %d. %s", idx, table_name)

        while True:
            entered_value = input("Select a table by number: ")

            if not entered_value.isdigit():
                logging.warning("Invalid selection. Please try again.")
                continue

            choice_idx = int(entered_value) - 1
            if not 0 <= choice_idx < len(unique_tables):
                logging.warning("Invalid selection. Please try again.")
                continue

            selected_table = unique_tables[choice_idx]

            logging.info("Selected table: %s", selected_table)

            return selected_table

    def __do_action_with_database(self, table_name: str):
        logging.info("Available actions:")

        class Action(Enum):
            """
            Actions that can be performed with the selected database.
            """

            SHOW_DATA = "Show data"
            INSERT_DATA = "Insert data"
            UPDATE_DATA = "Update data"
            DELETE_DATA = "Delete data"

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
                logging.info("Showing data from table '%s'", table_name)
                show_both = bool(
                    input("Show data from both databases? (y/n): ").strip().lower()
                    == "y"
                )
                self.__show_data(table_name, show_both=show_both)
            elif selected_action == Action.INSERT_DATA:
                self.__insert_data(table_name)
            elif selected_action == Action.UPDATE_DATA:
                self.__update_data(table_name)
            elif selected_action == Action.DELETE_DATA:
                self.__delete_data(table_name)

            break

    def __show_data(self, table_name: str, show_both: bool = False):
        for db_type, conn in self.__db_connections.items():
            tables = self.__get_tables_in_database(db_type)
            if table_name in tables:
                if db_type == DatabaseType.MYSQL:
                    cursor = conn.cursor()

                    cursor.execute(f"DESCRIBE {table_name};")
                    columns_mysql = [row[0] for row in cursor.fetchall()]
                    logging.info("(%s)", ", ".join(columns_mysql))

                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    for row in rows:
                        logging.info("(%s)", ", ".join(str(value) for value in row))

                    if not show_both:
                        break

                elif db_type == DatabaseType.MONGODB:
                    database_name = self.__databases[0].name
                    db = conn[database_name]
                    collection = db[table_name.lower()]

                    documents = collection.find()

                    logging.info(
                        "(%s)", ", ".join(str(value) for value in documents[0].keys())
                    )

                    for doc in documents:
                        logging.info(
                            "(%s)", ", ".join(str(value) for value in doc.values())
                        )

                    if not show_both:
                        break

    def __insert_data(self, table_name: str):
        logging.info("Inserting data to table '%s'", table_name)

        logging.info("Available entries:")

        self.__show_data(table_name)

        values = input("Enter values separated by commas: ")
        values_list = [value.strip() for value in values.split(",")]

        for db_type, conn in self.__db_connections.items():
            tables = self.__get_tables_in_database(db_type)
            if table_name in tables:
                if db_type == DatabaseType.MYSQL:
                    cursor = conn.cursor()
                    cursor.execute(
                        f"INSERT INTO {table_name} () VALUES ({', '.join(['%s'] * len(values_list))})",
                        values_list,
                    )
                    conn.commit()

                elif db_type == DatabaseType.MONGODB:
                    database_name = self.__databases[0].name
                    db = conn[database_name]
                    collection = db[table_name.lower()]
                    columns = collection.find_one().keys()
                    document = {
                        c: value
                        for i, (c, value) in enumerate(zip(columns, values_list))
                    }
                    collection.insert_one(document)

        logging.info("Entry inserted successfully.")

        logging.info("Updated entries:")

        self.__show_data(table_name)

        input("Press any button to continue...")

    def __update_data(self, table_name: str):
        logging.info("Updating data in table '%s'", table_name)

        logging.info("Available entries to update:")

        self.__show_data(table_name)

        selected_entry_id = int(input("Enter the ID of the entry to update: "))
        selected_entry_column = input("Enter the column name to update: ").lower()

        new_value = input("Enter the new value: ")

        for db_type, conn in self.__db_connections.items():
            tables = self.__get_tables_in_database(db_type)
            if table_name in tables:
                if db_type == DatabaseType.MYSQL:
                    cursor = conn.cursor()
                    cursor.execute(
                        f"UPDATE {table_name} SET {selected_entry_column} = %s WHERE _id = %s",
                        (new_value, selected_entry_id),
                    )
                    conn.commit()

                elif db_type == DatabaseType.MONGODB:
                    database_name = self.__databases[0].name
                    db = conn[database_name]
                    collection = db[table_name.lower()]
                    collection.update_one(
                        {"_id": int(selected_entry_id)},
                        {"$set": {selected_entry_column: new_value}},
                    )

        logging.info("Entry updated successfully.")

        logging.info("Updated entries:")

        self.__show_data(table_name)

        input("Press any button to continue...")

    def __delete_data(self, table_name: str):
        logging.info("Deleting data from table '%s'", table_name)

        logging.info("Available entries to delete:")

        self.__show_data(table_name)

        selected_entry_id = int(input("Enter the ID of the entry to delete: "))

        for db_type, conn in self.__db_connections.items():
            tables = self.__get_tables_in_database(db_type)
            if table_name in tables:
                if db_type == DatabaseType.MYSQL:
                    cursor = conn.cursor()
                    cursor.execute(
                        f"DELETE FROM {table_name} WHERE _id = %s",
                        (selected_entry_id,),
                    )
                    conn.commit()

                elif db_type == DatabaseType.MONGODB:
                    database_name = self.__databases[0].name
                    db = conn[database_name]
                    collection = db[table_name.lower()]
                    collection.delete_one({"_id": int(selected_entry_id)})

        logging.info("Entry deleted successfully.")

        logging.info("Updated entries:")

        self.__show_data(table_name)

        input("Press any button to continue...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    app = FrontendApplication()
