from Scraper import Scraper
from requests import Response

# IMPORTATN: Don't use print() use self.write()


class Demo(Scraper):

    NAME = "Demo"
    URL_TEMPLATE = ""

    def fetch(self, keywords: str) -> Response:
        return Response()

    def parse(self, html: str) -> list[dict]:
        return [
            {"rank": 1, "title": "Demo Titel 1", "pensum": "100%"},
            {"rank": 2, "title": "Demo Titel 2", "pensum": "50%"},
        ]
