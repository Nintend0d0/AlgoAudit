from Scraper import Scraper
from typing import Tuple
import requests
from bs4 import BeautifulSoup
import math
iport re

# IMPORTANT: Don't use print() use self.write()


class Careerjet(Scraper):

    NAME = "careerjet.ch"
    URL_TEMPLATE = "https://www.careerjet.ch/stellenangebote?s={keyword}&p={page}"
    URL_LOC_TEMPLATE = "https://www.careerjet.ch/stellenangebote?s={keyword}&l={location}&p={page}"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

    def pages(self, keyword: str) -> Tuple[int, requests.Response]:
        if self.config["use_location"]:
            url = self.URL_LOC_TEMPLATE.format(keyword=keyword, location=self.config["location"]["name"], page=1)
        else:
            url = self.URL_TEMPLATE.format(keyword=keyword, page=1)
        response = requests.get(url=url, headers={"User-Agent": self.user_agent})

        site = BeautifulSoup(response.text, "html.parser")

        number_of_jobs_span = site.select_one('div[id="search-content"]>header>p>span')

        if number_of_jobs_span is None:
            self.write(f"No results found for {keyword}")
            pages = 0
        else:
            number_of_jobs_text = number_of_jobs_span.get_text().strip().split(" ")[0]
            amount_found = int(re.sub(r'\D', '', number_of_jobs_text))
            pages = math.ceil(amount_found / 20)

        return pages, response


    def fetch(self, keyword: str, page: int) -> requests.Response:
        if self.config["use_location"]:
            url = self.URL_LOC_TEMPLATE.format(keyword=keyword, location=self.config["location"]["name"], page=page)
        else:
            url = self.URL_TEMPLATE.format(keyword=keyword, page=page)
        return requests.get(url=url, headers={"User-Agent": self.user_agent})


    def parse(self, html: str) -> list[dict]:
        result = []

        site = BeautifulSoup(html, "html.parser")

        # amount found
        number_of_jobs_span = site.select_one('div[id="search-content"]>header>p>span')

        if number_of_jobs_span is None:
            raise RuntimeError("careerjet.ch number of jobs selector not correct anymore.")

        number_of_jobs_text = number_of_jobs_span.get_text().strip().split(" ")[0]
        amount_found = int(re.sub(r'\D', '', number_of_jobs_text))

        # get all search results plus advertisement
        jobs = site.select(
            'div[id="search-content"]>ul[class="jobs"]>li:not(.cjgad-outer)'
        )

        for rank, job in enumerate(jobs):

            # ad id and title
            job_ad_id = job.select_one('article')['data-url'].split("/")[-1]
            title = job.select_one('article>header>h2>a')['title']
            description = job.select_one('article>div[class="desc"]').get_text().strip()
            release_date = job.select_one('article>footer>ul>li>span').get_text().strip()

            # employer
            employer_container = job.select_one('article>p[class="company"]>a')
            employer = employer_container.get_text().strip() if employer_container else None

            # locations
            locations_container = job.select_one('article>ul[class="location"]>li')
            locations = locations_container.get_text().strip() if locations_container else None

            # salary
            salary_container = job.select_one('article>ul[class="salary"]')
            salary = salary_container.li.get_text().strip() if salary_container else None

            result.append(
                {
                    "amount found": amount_found,
                    "rank": rank,
                    "job ad id": job_ad_id,
                    "title": title,
                    "release date": release_date,
                    "salary": salary,
                    "locations": locations,
                    "employer": employer,
                    "description": description,
                }
            )

        return result
