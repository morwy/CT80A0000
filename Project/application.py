#!/usr/bin/env python3

# --------------------------------------------------------------------------------------------------
#
# Imports.
#
# --------------------------------------------------------------------------------------------------
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Union

import mysql.connector
from mysql.connector import Error
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Static

# --------------------------------------------------------------------------------------------------
#
# Logger initialization.
# Output logs to a file so that they don't interfere with the textual UI.
#
# --------------------------------------------------------------------------------------------------
_LOG_FILEPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "application.log"
)

_LOGGER = logging.getLogger("argus_po_application")
_LOGGER.setLevel(logging.DEBUG)
_LOGGER.propagate = False

_FILE_HANDLER = logging.FileHandler(
    filename=_LOG_FILEPATH, mode="w", encoding="utf-8", errors="ignore"
)
_FILE_HANDLER.setLevel(logging.DEBUG)
_FILE_HANDLER.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
)
_LOGGER.addHandler(_FILE_HANDLER)

# Disable MySQL connector debug logs
logging.getLogger("mysql").setLevel(logging.WARNING)
logging.getLogger("mysql.connector").setLevel(logging.WARNING)


# --------------------------------------------------------------------------------------------------
#
# Database connection information.
#
# --------------------------------------------------------------------------------------------------
@dataclass
class _DatabaseInformation:
    """
    Holds information required to connect to a database.
    """

    host: str = "127.0.0.1"
    port: int = 33061
    name: str = "radar_db"
    user: str = "root"
    password: str = "SuperSecureMilitaryPassword"
    timeout_seconds: int = 5


@dataclass
class _UserGroup:
    """
    Holds information about a user group.
    """

    id: int = 0
    name: str = ""
    description: str = ""


@dataclass
class _Permission:
    """
    Holds information about user permissions.
    """

    id: int = 0
    can_select: bool = False
    can_insert: bool = False
    can_update: bool = False
    can_delete: bool = False


@dataclass
class _UserInformation:
    """
    Holds information about a user.
    """

    id: int = 0
    group: _UserGroup = field(default_factory=_UserGroup)
    username: str = ""
    password: str = ""
    radar_station: int = 0
    permissions: _Permission = field(default_factory=_Permission)


@dataclass
class _RadarDetection:
    """
    Holds information about a radar detection.
    """

    detection_id: int = 0
    radar_id: int = 0
    timestamp: datetime = datetime.now()
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    reflection_rate: float = 0.0


@dataclass
class _AuditLogEntry:
    """
    Holds information about an audit log entry.
    """

    log_id: int = 0
    timestamp: datetime = datetime.now()
    user_id: int = 0
    operation: str = ""
    radar_station: int = 0
    table_name: str = ""
    description: str = ""


class ArgusSystem:
    """
    Manages connection to the database.
    """

    def __init__(self):
        _LOGGER.info("Database connector initialized.")

        self.__current_radar_station_id = 1

        self.__db_information: _DatabaseInformation = _DatabaseInformation()  # type: ignore
        self.__db_connection: Union[mysql.connector.pooling.PooledMySQLConnection, mysql.connector.MySQLConnection] | None = None  # type: ignore

        self._user: _UserInformation | None = None  # type: ignore

        self.__connect_to_database()

    def __del__(self):
        _LOGGER.info("Shutting down database connector.")
        self.logout()
        self.__disconnect_from_databases()

    def __connect_to_database(self):
        _LOGGER.info("Connecting to the database.")

        connection = mysql.connector.connect(
            host=self.__db_information.host,
            port=self.__db_information.port,
            user=self.__db_information.user,
            password=self.__db_information.password,
            database=self.__db_information.name,
            connection_timeout=self.__db_information.timeout_seconds,
        )

        if connection.is_connected():
            self.__db_connection = connection  # type: ignore
            _LOGGER.info(
                "Connected to the database '%s' on %s:%s",
                self.__db_information.name,
                self.__db_information.host,
                self.__db_information.port,
            )

        else:
            _LOGGER.warning(
                "Unable to establish connection to database '%s'",
                self.__db_information.name,
            )
            raise Error(
                f"Connection to database '{self.__db_information.name}' failed."
            )

        _LOGGER.info("Connected to database successfully.")

    def __disconnect_from_databases(self):
        if self.__db_connection is not None:
            _LOGGER.info("Disconnecting from database.")

            if self.__db_connection.is_connected():
                self.__db_connection.close()
                _LOGGER.info("Disconnected from database.")

    def log(
        self,
        table_name: str,
        operation: str,
        description: str,
    ) -> None:
        """
        Logs an operation performed by a user.

        :param table_name: The name of the table affected.
        :param operation: The operation performed (e.g., 'INSERT', 'UPDATE').
        :param description: A description of the operation.
        """
        if self.__db_connection is None or not self.__db_connection.is_connected():
            _LOGGER.error("Database connection is not established.")
            return

        try:
            cursor = self.__db_connection.cursor()
            query = "INSERT INTO AUDIT_LOG (timestamp, user_id, operation, radar_station, table_name, description) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(
                query,
                (
                    datetime.now(),
                    self._user.id if self._user is not None else None,
                    operation,
                    self.__current_radar_station_id,
                    table_name,
                    description,
                ),
            )
            self.__db_connection.commit()

            _LOGGER.info("Logged message to database: %s", description)

        except Error as e:
            _LOGGER.error("Error logging message to database: %s", e)

    def login(self, username: str, password: str) -> bool:
        """
        Attempts to log in a user with the given username and password.

        :param username: The username to log in.
        :param password: The password to log in.
        :return: True if login is successful, False otherwise.
        """
        if self.__db_connection is None or not self.__db_connection.is_connected():
            _LOGGER.error("Database connection is not established.")
            return False

        self.log(
            "USER_ACCOUNT", "LOGIN_ATTEMPT", f"User '{username}' attempting to log in."
        )

        try:
            cursor = self.__db_connection.cursor()
            query = f"SELECT * FROM USER_ACCOUNT WHERE username='{username}' AND password_hash='{password}';"
            cursor.execute(query)
            user_entry = cursor.fetchone()

            if not user_entry or len(user_entry) == 0:
                self.log(
                    "USER_ACCOUNT",
                    "LOGIN_FAILED",
                    f"User '{username}' failed to log in.",
                )
                return False

            user_group: int = int(user_entry[1])  # type: ignore

            query = f"SELECT group_id, group_name, description FROM USER_GROUP WHERE group_id = {user_group};"
            cursor.execute(query)
            group_entry = cursor.fetchone()

            query = f"SELECT can_select, can_insert, can_update, can_delete FROM PERMISSION WHERE group_id = {user_group};"
            cursor.execute(query)
            permission_entry = cursor.fetchone()

            user = _UserInformation()
            user.id = int(user_entry[0])  # type: ignore
            user.group.id = int(group_entry[0])  # type: ignore
            user.group.name = group_entry[1]  # type: ignore
            user.group.description = group_entry[2]  # type: ignore
            user.username = username
            user.password = password
            user.permissions.can_select = bool(permission_entry[0])  # type: ignore
            user.permissions.can_insert = bool(permission_entry[1])  # type: ignore
            user.permissions.can_update = bool(permission_entry[2])  # type: ignore
            user.permissions.can_delete = bool(permission_entry[3])  # type: ignore

            self._user = user

            self.log(
                "USER_ACCOUNT",
                "LOGIN_SUCCESS",
                f"User '{username}' logged in successfully.",
            )

            return True

        except Error as e:
            self.log(
                "USER_ACCOUNT",
                "LOGIN_ERROR",
                f"Error during login for user '{username}': {e}",
            )
            return False

    def logout(self) -> None:
        """
        Logs out the current user.
        """
        if self._user is None:
            _LOGGER.warning("No user is currently logged in.")
            return

        username = self._user.username

        self.log(
            "USER_ACCOUNT",
            "LOGOUT_SUCCESS",
            f"User '{username}' logged out successfully.",
        )

        self._user = None


_ARGUS_SYSTEM = ArgusSystem()


# --------------------------------------------------------------------------------------------------
#
# UI elements
#
# --------------------------------------------------------------------------------------------------
class LoginScreen(Screen):
    """
    Login application class.
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="login-box"):
            yield Static("ARGUS PANOPTES RADAR SYSTEM", id="title")
            yield Static("Username:")
            yield Input(id="username", compact=True)
            yield Static("Password:")
            yield Input(password=True, id="password", compact=True)
            yield Button("OK", id="ok", variant="primary", compact=True)
            yield Static("", id="status")

    def action_submit(self) -> None:
        """
        Handles the submit action.
        """

        username = self.query_one("#username", Input).value
        password = self.query_one("#password", Input).value
        status = self.query_one("#status", Static)

        if _ARGUS_SYSTEM.login(username, password):
            self.app.pop_screen()
        else:
            status.update("Access denied")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handles button press events.
        """
        if event.button.id == "ok":
            self.action_submit()


class LoginApplication(App):
    """
    Login application class.
    """

    CSS = """
    Screen {
        align: center middle;
    }

    #login-box {
        width: 60%;
        max-width: 60;
        min-width: 32;
        height: auto;
        padding: 1 2;
        background: black;
    }

    #title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    Button {
        margin-top: 1;
        width: 100%;
    }

    #status {
        margin-top: 1;
        height: 1;
        text-align: center;
    }
    """

    def __init__(self):
        super().__init__()

    def on_mount(self) -> None:
        """
        Called when the application is mounted.
        """
        self.push_screen(LoginScreen())


# --------------------------------------------------------------------------------------------------
#
# Entry point.
#
# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    LoginApplication().run()
