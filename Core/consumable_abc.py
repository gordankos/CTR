"""
Python module for Product and Recipe abstract base class.

"""

from Core.enums import ServingType

from abc import ABC, abstractmethod


class ConsumableItem(ABC):
    def __init__(
            self,
            item_id: int,
            name: str
    ):
        self.item_id = item_id
        self.name = name

    @property
    @abstractmethod
    def item_type(self) -> ServingType:
        pass

    @property
    def identifier_string(self) -> str:
        return f"{self.item_id}. {self.name}"
