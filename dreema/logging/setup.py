"""Logging setup helpers for Dreema.

This module initializes the log storage directory and writes log entries
with timestamps and severity levels.
"""

import os
from datetime import datetime

class Setup:
    """Manage a file-based logger for Dreema applications."""

    def __init__(self, file):
        self.path = "storage/logs"
        self.filename = f"{self.path}/{file}.log"
        self._prepareLogger()

    def _prepareLogger(self):
        """Ensure the log path exists and create the log file if missing."""
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                f.write("DATE LEVEL MESSAGE\n")

    def write(self, level: str, message: str):
        """Append a timestamped log entry to the log file."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = f"{now} {level.upper()} {message}\n"

        with open(self.filename, "a") as f:
            f.write(log)
