from Scraper import Scraper
import requests

# IMPORTATN: Don't use print() use self.write()


class Jobs(Scraper):

    NAME = "jobs.ch"
    URL_TEMPLATE = (
        "https://www.jobs.ch/de/stellenangebote/?location={location}&term={keyword}"
    )

    def fetch(self, keyword: str) -> requests.Response:
        return requests.get(
            self.URL_TEMPLATE.format(keyword=keyword, location=self.config["location"]),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            },
        )

    def parse(self, html: str) -> list[dict]:
        self.write(html)

        return [
            {"rank": 1, "title": "Demo Titel 1", "pensum": "100%"},
            {"rank": 2, "title": "Demo Titel 2", "pensum": "50%"},
        ]
