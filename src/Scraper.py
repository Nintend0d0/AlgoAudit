from abc import ABC, abstractmethod
from requests import Response


class Scraper(ABC):

    NAME = ""
    URL_TEMPLATE = ""

    @abstractmethod
    def fetch(self, keywords: str) -> Response:
        pass

    @abstractmethod
    def parse(self, html: str) -> str:
        pass
