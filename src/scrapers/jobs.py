from Scraper import Scraper
from typing import Tuple
import requests
from bs4 import BeautifulSoup

# IMPORTANT: Don't use print() use self.write()


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

        # get all search results plus advertisement
        jobs = site.select(
            'div[data-feat="boosted_jobs"],div[data-feat="searched_jobs"]'
        )

        for rank, job in enumerate(jobs):

            # Tip: use following to inspect what you have selected
            # open("output/example.html", "w").write(job.prettify())
            # exit()

            # ad
            is_ad = job["data-feat"] == "boosted_jobs"

            # release date
            release_date_span = job.select_one('span[aria-hidden="true"]')
            release_date = release_date_span.get("title") if release_date_span else None

            # starting point for other elements too
            merken_button = job.select_one('button[title="Merken"]')

            # pylance/pyright cant handle beautifulsoup correctly :(

            # title
            title_div = merken_button.next_sibling if merken_button else None
            title_span = title_div.span if title_div else None  # type: ignore
            title = title_span.get_text() if title_span else None

            meta_div = title_div.next_sibling if title_div else None
            meta_ps = meta_div.select("div>p") if meta_div else None  # type: ignore

            if meta_ps and len(meta_ps) == 3:  # type: ignore
                # locations
                locations = meta_ps[0].get_text()
                # pensum percentage
                pensum_percentage = meta_ps[1].get_text()
                # pensum string
                pensum_string = meta_ps[2].get_text()
            else:
                locations, pensum_percentage, pensum_string = None, None, None

            # employer
            employer_div = meta_div.next_sibling if title_div else None  # type: ignore
            employer_strong = (
                employer_div.select_one("strong") if employer_div else None  # type: ignore
            )
            employer = employer_strong.get_text() if employer_strong else None  # type: ignore

            result.append(
                {
                    "amount found": amount_found,
                    "rank": rank,
                    "ad": is_ad,
                    "title": title,
                    "release date": release_date,
                    "pensum string": pensum_string,
                    "pensum percentage": pensum_percentage,
                    "locations": locations,
                    "employer": employer,
                }
            )

        # view data
        # self.write(result.__repr__())
        # exit(0)

        return result
