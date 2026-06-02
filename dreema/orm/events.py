"""Abstract ORM event interface for Dreema.

Defines the required async CRUD contract for database query classes.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any


class EventsInterface(ABC):
    """Base abstract class for database event handlers."""

    @abstractmethod
    async def read(
        self, filters: dict[Any, Any] | None, params: Optional[dict[Any, Any]] = None
    ):
        """
        Get a single object from the database

        :param filters: Nested list of query parameters.
        :param params: Additional flag that can be activated
        :return: An object containing data, status, message and trace
        """
        pass

    @abstractmethod
    async def create(self, data, params: Optional[dict[Any, Any]] = None):
        """
        Insert data into the database.

        :param data: Dictionary of data to create.
        :param params: Additional flag that can be activated
        :return: An object containing data, status, message and trace
        """
        pass

    @abstractmethod
    async def delete(
        self,
        filters: Optional[dict[Any, Any]] = None,
        params: Optional[dict[Any, Any]] = None,
    ):
        """
        Delete an object from the database.

        :param filters: Nested list of query parameters.
        :param params: Additional flag that can be activated
        :return: An object containing data, status, message and trace
        """
        pass

    @abstractmethod
    async def update(
        self,
        filters: Optional[dict[Any, Any]] = None,
        data=None,
        params: Optional[dict[Any, Any]] = None,
    ):
        """
        Update an object in the database.

        :param filters: Nested list of query parameters.
        :param data: Dictionary of data to update.
        :param params: Additional flag that can be activated
        :return: An object containing data, status, message and trace
        """
        pass

    @abstractmethod
    async def count(
        self,
        filters: Optional[dict[Any, Any]] = None,
        params: Optional[dict[Any, Any]] = None,
    ):
        """Count the number of objects in the database.

        :param filters: Nested list of query parameters.
        :param params: Additional flag that can be activated
        :return: An object containing data, status, message and trace
        """
        pass