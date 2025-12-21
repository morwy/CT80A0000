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
from typing import List, Union

import mysql.connector
from mysql.connector import Error
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, CenterMiddle, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

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
    can_view: bool = False
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
            user.permissions.can_view = bool(permission_entry[0])  # type: ignore
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

    def permissions(self) -> _Permission | None:
        """
        Returns the permissions of the currently logged-in user.

        :return: The permissions of the user, or None if no user is logged in.
        """
        self.log(
            "USER_ACCOUNT",
            "PERMISSIONS_REQUEST",
            f"Requesting permissions for user '{self._user.username if self._user else 'None'}'.",
        )

        if self._user is None:
            _LOGGER.warning("No user is currently logged in.")
            return None

        return self._user.permissions

    def audit_logs(self) -> List[_AuditLogEntry]:
        """
        Retrieves audit log entries from the database.

        :return: A list of audit log entries.
        """
        self.log(
            "AUDIT_LOG",
            "LOG_RETRIEVAL_ATTEMPT",
            "Retrieving audit logs.",
        )

        if self.__db_connection is None or not self.__db_connection.is_connected():
            _LOGGER.error("Database connection is not established.")
            return []

        try:
            cursor = self.__db_connection.cursor()
            query = "SELECT log_id, timestamp, user_id, operation, radar_station, table_name, description FROM AUDIT_LOG ORDER BY log_id DESC;"
            cursor.execute(query)
            log_entries = cursor.fetchall()

            audit_logs: List[_AuditLogEntry] = []

            for entry in log_entries:
                log = _AuditLogEntry()
                log.log_id = int(entry[0])  # type: ignore
                log.timestamp = entry[1]  # type: ignore
                log.user_id = int(entry[2]) if entry[2] is not None else None  # type: ignore
                log.operation = entry[3]  # type: ignore
                log.radar_station = int(entry[4])  # type: ignore
                log.table_name = entry[5]  # type: ignore
                log.description = entry[6]  # type: ignore

                audit_logs.append(log)

            self.log(
                "AUDIT_LOG",
                "LOG_RETRIEVAL_SUCCESS",
                f"Retrieved {len(audit_logs)} audit log entries.",
            )

            return audit_logs

        except Error as e:
            self.log(
                "AUDIT_LOG",
                "LOG_RETRIEVAL_ERROR",
                f"Error retrieving audit logs: {e}",
            )
            return []


_ARGUS_SYSTEM = ArgusSystem()


# --------------------------------------------------------------------------------------------------
#
# UI elements
#
# --------------------------------------------------------------------------------------------------
class LoginScreen(ModalScreen[bool]):
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
            yield Button("Login", id="login", variant="primary", compact=True)
            yield Static("", id="status")

    def action_submit(self) -> None:
        """
        Handles the submit action.
        """
        username = self.query_one("#username", Input).value
        password = self.query_one("#password", Input).value
        status = self.query_one("#status", Static)

        if _ARGUS_SYSTEM.login(username, password):
            self.dismiss(True)
        else:
            status.update("Access denied")

    def action_cancel(self) -> None:
        """
        Handles the cancel action.
        """
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handles button press events.
        """
        if event.button.id == "login":
            self.action_submit()


class LogScreen(Screen):
    """
    Screen to display audit logs.
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
        Binding("ctrl+q", "close", "Close"),
    ]

    def compose(self):
        yield Header(show_clock=True)
        yield Center(DataTable(id="log_table"))
        yield Footer()

    @work(exclusive=True)
    async def load_data(self, logs: List[_AuditLogEntry]) -> None:
        """
        Loads audit log data into the table.

        :param logs: List of audit log entries to display.
        """
        columns = [
            "ID",
            "Timestamp",
            "User ID",
            "Operation",
            "Radar Station",
            "Table Name",
            "Description",
        ]

        table = self.query_one("#log_table", DataTable)

        table.clear(columns=True)
        table.add_columns(*columns)

        for log in logs:
            rows = [
                str(log.log_id),
                str(log.timestamp),
                str(log.user_id),
                str(log.operation),
                str(log.radar_station),
                str(log.table_name),
                str(log.description),
            ]
            table.add_row(*rows)

    def action_close(self) -> None:
        """
        Closes the log screen.
        """
        self.app.pop_screen()


class MainScreen(Screen):
    """
    Main application screen.
    """

    BINDINGS = [
        Binding("l", "log", "View Logs"),
        Binding("d", "detections", "View Detections"),
        Binding("m", "map", "View Map"),
        Binding("o", "logout", "Logout"),
        Binding("q", "quit", "Quit"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.__permissions: _Permission | None = None  # type: ignore

    def compose(self) -> ComposeResult:
        #
        # ASCII art logo from: https://emojicombos.com/eye-ascii-art
        # License is not specified, assumed to be public domain.
        #
        logo = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣤⣴⡶⠶⠾⠟⠛⠛⠛⠛⠷⠶⣦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣶⠿⠛⠉⣁⣠⠤⠤⠀⠀⠀⠀⠀⠀⠀⠘⠷⢬⣙⡛⠷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡶⠟⢉⣠⠴⠚⠉⠁⣀⡀⠠⠀⠐⠂⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠦⣍⡻⢷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⠿⢋⡤⠞⢉⣠⡤⠖⢚⣉⣁⣤⣤⣴⣦⣤⣤⣄⣀⣀⠀⠀⠘⠲⢤⡀⠀⠈⠙⠲⣌⡛⢷⣤⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⡾⢋⣡⠞⣋⠴⠚⣉⣥⡴⠾⠟⠛⢉⣉⣀⣠⣤⣤⣭⣍⣉⣛⡻⠶⣦⣤⣀⠉⠓⠦⣄⠀⠀⠙⢦⡉⠻⣦⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣀⣴⠟⢁⣴⣫⠷⢛⣡⣴⠟⠋⣁⣤⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠿⠿⣿⣶⣬⣝⡻⢶⣤⡀⠙⠂⢀⠀⠘⠢⡈⠻⣶⣄⠀⠀⠀
⠀⠀⠀⠀⣠⡾⠛⠁⢠⡿⠛⣡⣶⠟⢋⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣀⣤⣤⠀⠻⣿⣿⣿⣷⣮⣟⠷⣦⣜⠀⠀⠀⠀⠀⠈⠛⢷⣄⠀
⠀⢀⣰⡾⠋⠀⠀⠀⢋⣴⠿⢋⣦⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡇⠈⣿⢿⣿⣿⣿⣿⣾⣝⡻⣦⣄⠀⠀⠀⠀⠀⠙⠷
⣰⡿⠋⠀⠀⠀⣠⡾⢛⣡⣶⡿⠛⣿⣿⣿⣿⠻⣿⠸⣏⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡇⠀⣿⠈⢻⣿⢿⣿⢿⣿⣿⣷⣭⣀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣤⣾⣯⣴⡿⠛⠋⠀⠀⢹⡼⣿⣿⠀⢿⡀⠉⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢣⡇⢀⡿⠀⣸⡏⢸⡟⢘⣿⠁⠙⠛⣻⣷⠀⢸⡆⠀⠀
⠀⠀⠀⠘⣯⣾⡟⢷⡄⠀⠀⠀⠀⠀⠀⠙⢿⣆⠘⣷⡀⠀⠀⠙⠿⣿⣿⣿⣿⣿⣿⣿⡿⢋⡾⢀⡼⠁⣰⡟⠀⠞⠁⢸⡏⠀⢀⣴⣿⠁⠀⣸⠇⠀⠀
⠀⠀⣰⣿⢛⣿⡇⠘⠃⠀⠀⠀⠀⠀⠀⠀⠈⠻⣧⣈⠃⠀⠀⠀⠀⠀⠈⠉⠛⠛⠋⠉⠴⠋⣠⠞⢀⣼⠏⠀⠀⠀⠀⡞⢀⣴⣿⣿⠏⠀⠀⠁⠀⠀⠀
⠀⠀⠙⠛⠛⠛⠿⠿⣷⣦⣄⡐⢦⣀⠀⠀⠀⠀⠈⠛⢷⣦⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢞⣡⣴⠟⠁⠀⠀⠀⢀⣠⣾⣿⣿⠟⡁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⡀⠀⠀⠀⠀⠀⠀⠈⠙⠻⢶⣭⣟⡦⣤⣀⡀⠀⠀⠉⠛⠻⠿⠶⣶⣤⣤⣤⣶⣶⠿⠟⠋⠀⠀⠀⢀⣠⣶⣿⣿⡿⠋⣠⣾⠇⣠⠀⠀⠀⠀⠀⠀
⠀⠘⠛⠛⠛⠛⠻⢷⣦⣀⠀⠀⠀⠈⠉⠛⠷⢮⣽⣓⡲⠤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣶⣿⣿⡿⠛⠉⢁⣴⠟⢡⡾⠃⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠸⣄⡈⠛⠿⣶⣤⣄⡀⠀⠀⠀⠀⠉⠙⠛⠿⠷⣶⣦⣤⣤⣤⣤⣴⣶⣶⡿⠿⠿⠟⠛⠋⠁⢀⣠⡾⠛⢁⡴⠋⣠⠆⢀⡴⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢻⣌⡛⠶⣤⣀⠈⠙⠛⠿⢶⣦⣤⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣾⠟⠋⣠⡶⢋⡠⠞⠁⠠⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠷⣍⡛⠳⢶⣭⠅⠀⠀⠀⠀⠀⠈⠉⢛⠛⠿⠷⢶⣶⣦⣤⣤⣤⣤⣤⣤⣴⣶⡾⠟⠛⠉⠀⠀⠚⠡⠖⣋⡤⠖⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠓⠃⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⣶⠦⠤⠤⠤⠤⣄⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   
"""

        yield Header(name="ARGUS PANOPTES RADAR SYSTEM", show_clock=True)
        yield CenterMiddle(Static(logo, id="logo", expand=True))
        yield Footer()

    def on_mount(self) -> None:
        """
        Called when the screen is mounted.
        """
        self.start_login()

    def on_unmount(self) -> None:
        """
        Called when the screen is unmounted.
        """
        global _ARGUS_SYSTEM
        del _ARGUS_SYSTEM

    @work(exclusive=True)
    async def start_login(self) -> None:
        """
        Starts the login process.
        """
        authenticated = await self.app.push_screen_wait(LoginScreen())
        if not authenticated:
            self.app.exit(1)

        self.__permissions = _ARGUS_SYSTEM.permissions()
        if self.__permissions is None:
            self.app.exit(1)

    def action_log(self) -> None:
        """
        Views the logs.
        """
        if self.__permissions is None or not self.__permissions.can_view:
            _LOGGER.warning("User does not have permission to view logs.")
            _ARGUS_SYSTEM.log(
                "AUDIT_LOG",
                "UNAUTHORIZED_ACCESS",
                "Attempted to view logs without permission.",
            )
            self.notify(
                message="You do not have permission to view logs.", severity="error"
            )
            return

        logs = _ARGUS_SYSTEM.audit_logs()

        log_screen = LogScreen()
        self.app.push_screen(log_screen)
        log_screen.load_data(logs)

    def action_detections(self) -> None:
        """
        Views the radar detections.
        """
        if self.__permissions is None or not self.__permissions.can_view:
            _LOGGER.warning("User does not have permission to view detections.")
            _ARGUS_SYSTEM.log(
                "RADAR_DETECTION",
                "UNAUTHORIZED_ACCESS",
                "Attempted to view detections without permission.",
            )
            self.notify(
                message="You do not have permission to view detections.",
                severity="error",
            )
            return

    def action_map(self) -> None:
        """
        Views the radar map.
        """
        if self.__permissions is None or not self.__permissions.can_view:
            _LOGGER.warning("User does not have permission to view detections on map.")
            _ARGUS_SYSTEM.log(
                "RADAR_DETECTION",
                "UNAUTHORIZED_ACCESS",
                "Attempted to view detections on map without permission.",
            )
            self.notify(
                message="You do not have permission to view detections on map.",
                severity="error",
            )
            return

    def action_logout(self) -> None:
        """
        Logs out the current user.
        """
        _ARGUS_SYSTEM.logout()
        self.start_login()

    def action_quit(self):
        """
        Quits the application.
        """
        self.app.exit(0)


class MainApplication(App):
    """
    Login application class.
    """

    TITLE = "ARGUS PANOPTES RADAR SYSTEM"

    CSS = """
    LoginScreen {
        background: #181818;
    }
    
    Screen {
        align: center middle;
    }

    #logo {
        text-align: center;
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

    def on_mount(self) -> None:
        """
        Called when the application is mounted.
        """
        self.push_screen(MainScreen())


# --------------------------------------------------------------------------------------------------
#
# Entry point.
#
# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    MainApplication().run()
