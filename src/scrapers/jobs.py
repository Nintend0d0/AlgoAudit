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

        last_site_link_text = last_site_link_span.get_text()

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
        result = []

        site = BeautifulSoup(html, "html.parser")

        # amount found
        span_page_header = site.select_one('span[data-cy="page-header"]')

        if span_page_header is None:
            raise RuntimeError("Jobs.ch page header selector not correct anymore.")

        span_page_header_text = span_page_header.get_text()
        amount_found = span_page_header_text.split(" ")[0]

        # get all search results plus advertisment
        jobs = site.select(
            'div[data-feat="boosted_jobs"],div[data-feat="searched_jobs"]'
        )

        for rank, job in enumerate(jobs):
            is_ad = job["data-feat"] == "boosted_jobs"
            # TODO: parse job
            result.append(
                {
                    "amount found": amount_found,
                    "rank": rank,
                    "ad": is_ad,
                    "title": f"todo {rank}",
                    "pensum": f"todo {rank}",
                }
            )

        return result
