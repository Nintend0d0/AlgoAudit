from Scraper import Scraper
from typing import Tuple
import requests
from bs4 import BeautifulSoup

# IMPORTATN: Don't use print() use self.write()


class Jobs(Scraper):

    NAME = "jobs.ch"
    URL_TEMPLATE = "https://www.jobs.ch/de/stellenangebote/?location={location}&page={page}&term={keyword}"

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

    def pages(self, keyword: str) -> Tuple[int, requests.Response]:
        response = requests.get(
            self.URL_TEMPLATE.format(
                keyword=keyword, location=self.config["location"]["name"], page=1
            ),
            headers={"User-Agent": self.user_agent},
        )

        site = BeautifulSoup(response.text, "html.parser")

        last_site_link_span = site.select_one(
            'div[data-cy="paginator"]>div>div>a.cursor_pointer:last-child>span:first-child'
        )

        if last_site_link_span is None:
            raise RuntimeError("Jobs.ch paginator selector not correct anymore.")

        last_site_link_text = last_site_link_span.contents[0].get_text()

        pages = int(last_site_link_text.split(" ")[-1])

        return pages, response

    def fetch(self, keyword: str, page: int) -> requests.Response:
        return requests.get(
            self.URL_TEMPLATE.format(
                keyword=keyword, location=self.config["location"]["name"], page=page
            ),
            headers={"User-Agent": self.user_agent},
        )

    def parse(self, html: str) -> list[dict]:
        # self.write(html)

        # exit(0)

        return [
            {"rank": 1, "title": "Demo Titel 1", "pensum": "100%"},
            {"rank": 2, "title": "Demo Titel 2", "pensum": "50%"},
        ]
