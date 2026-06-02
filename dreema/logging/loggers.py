"""Logger factory helpers for Dreema.

This module provides convenience static logging methods with a shared
Setup logger instance per filename.
"""

from .setup import Setup

class Logger:
    """Factory that returns shared file-based logger instances."""

    _instances = {}  # filename → Setup instance

    @classmethod
    def logger(cls, filename):
        """Return a shared Setup logger for the given filename."""
        if filename not in cls._instances:
            cls._instances[filename] = Setup(file=filename)
        return cls._instances[filename]

    @staticmethod
    def success(message: str, filename='system'):
        """Log a success-level message."""
        log = Logger.logger(filename)
        log.write('success', message=message)

    @staticmethod
    def info(message: str, filename='system'):
        """Log an info-level message."""
        log = Logger.logger(filename)
        log.write('info', message=message)
    
    @staticmethod
    def debug(message: str, filename='system'):        
        """Log a debug-level message."""
        log = Logger.logger(filename)
        log.write('debug', message=message)

    @staticmethod
    def error(message: str, filename='system'):
        log = Logger.logger(filename)
        log.write('error', message=message)