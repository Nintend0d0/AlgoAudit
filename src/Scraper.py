from abc import ABC, abstractmethod
from requests import Response


class Scraper(ABC):

    NAME = ""
    URL_TEMPLATE = ""

    def __init__(self, out, config) -> None:
        self.write = out
        self.config = config
        super().__init__()

    @abstractmethod
    def fetch(self, keywords: str) -> Response:
        pass

    @abstractmethod
    def parse(self, html: str) -> list[dict]:
        pass


fieldnames = ["keyword", "page", "rank", "title", "pensum"]
