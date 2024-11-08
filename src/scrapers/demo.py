from Scraper import Scraper
from requests import Response


class Demo(Scraper):

    NAME = "Demo"
    URL_TEMPLATE = ""

    def fetch(self, keywords: str) -> Response:
        print("I fetch")
        return Response()

    def parse(self, html: str) -> str:
        print("I parse")
        return ""
