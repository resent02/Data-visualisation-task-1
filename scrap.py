import re
import sqlite3

import scrapy


class WikiFilmSpider(scrapy.Spider):
    name = "wiki_film"
    start_urls = ["https://en.wikipedia.org/wiki/List_of_highest-grossing_films"]

    def parse(self, response):
        for row in response.css("table.wikitable tbody tr"):
            columns = row.css("td, th")

            if len(columns) < 5:
                continue

            title_link = columns[2].css("i a::attr(href)").get()
            title = columns[2].css("i a::text").get()
            release_year = columns[4].css("::text").get()
            box_office = columns[3].css("::text").get()

            if title_link and title and release_year and box_office:
                yield response.follow(
                    title_link,
                    self.parse_film,
                    meta={
                        "title": title,
                        "release_year": int(release_year),
                        "box_office": box_office.strip(),
                    },
                )

    def parse_film(self, response):
        title = response.meta["title"]
        release_year = response.meta["release_year"]
        box_office = response.meta["box_office"]

        # Extract directors
        director = response.xpath(
            "//th[contains(text(), 'Directed by')]/following-sibling::td//a[not(contains(@class, 'mw-redirect'))]/text()"
        ).getall()
        director = [d.strip() for d in director if d.strip()]

        # Extract countries
        country_section = response.xpath(
            "//th[contains(text(), 'Countries') or contains(text(), 'Country')]/following-sibling::td"
        )
        countries = []

        # First try to get country links
        country_links = country_section.xpath(
            ".//a[not(contains(@class, 'mw-redirect'))]/text()"
        ).getall()
        if country_links:
            countries = [link.strip() for link in country_links if link.strip()]
        else:
            # If no links, extract plain text and clean
            country_text = country_section.xpath("string(.)").get()
            if country_text:
                country_text = re.sub(r"\[\d+\]", "", country_text)
                countries = [
                    c.strip()
                    for c in re.split(r"[,;]|\band\b", country_text)
                    if c.strip()
                ]

        countries = [c for c in countries if c]

        # Insert into the SQLite database
        self.add_film_to_db(
            title,
            release_year,
            director[0] if director else None,
            box_office,
            countries[0] if countries else None,
        )

    def add_film_to_db(self, title, release_year, director, box_office, country):
        conn = sqlite3.connect("films.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO films (title, release_year, director, box_office, country)
            VALUES (?, ?, ?, ?, ?)
        """,
            (title, release_year, director, box_office, country),
        )

        conn.commit()
        conn.close()
