from abc import ABC, abstractmethod
from typing import Tuple
import requests


class Scraper(ABC):

    NAME = ""
    URL_TEMPLATE = ""

    def __init__(self, out, config) -> None:
        self.write = out
        self.config = config
        super().__init__()

    def pages(self, keyword: str) -> Tuple[int, requests.Response]:
        response = requests.Response()
        response.status_code = 200
        return 1, response

    @abstractmethod
    def fetch(self, keyword: str, page: int) -> requests.Response:
        pass

    @abstractmethod
    def parse(self, html: str) -> list[dict]:
        pass


fieldnames = ["keyword", "site", "page", "total pages", "rank", "title", "pensum"]
