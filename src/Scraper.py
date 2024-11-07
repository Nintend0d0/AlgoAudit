from abc import ABC, abstractmethod

class Scraper(ABC):

    NAME = ""

    @abstractmethod
    def print(self):
        pass
