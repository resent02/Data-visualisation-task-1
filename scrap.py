import json
import re
import sqlite3

import scrapy


class WikiFilmSpider(scrapy.Spider):
    name = "wiki_film"
    start_urls = ["https://en.wikipedia.org/wiki/List_of_highest-grossing_films"]

    def __init__(self):
        self.conn = sqlite3.connect("films.db")
        self.cursor = self.conn.cursor()
        self._create_table()
        super().__init__()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS films (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                release_year INTEGER,
                directors TEXT,
                box_office TEXT,
                countries TEXT
            )
        """)
        self.conn.commit()

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
                        "release_year": int(release_year.strip())
                        if release_year
                        else None,
                        "box_office": box_office.strip(),
                    },
                )

    def parse_film(self, response):
        meta = response.meta
        title = meta["title"]

        # Director extraction
        directors = response.xpath(
            "//th[contains(., 'Directed by')]/following-sibling::td//a[not(@class='mw-redirect')]/text()"
        ).getall()
        directors = [d.strip() for d in directors if d.strip()]

        # Country extraction
        country_section = response.xpath(
            "//th[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'country')]/following-sibling::td[1]"
        )
        countries = []

        # Try linked countries first
        country_links = country_section.xpath(
            ".//a[not(contains(@class, 'mw-redirect'))]/text()"
        ).getall()
        if country_links:
            countries = [link.strip() for link in country_links if link.strip()]

        # Fallback to text processing
        if not countries:
            country_text = country_section.xpath("string(.)").get()
            if country_text:
                country_text = re.sub(r"\[\d+\]|[()]", "", country_text)
                countries = [
                    c.strip()
                    for c in re.split(r"\s*[,;]\s*|\s+\b(and|&)\b\s+", country_text)
                    if c.strip()
                ]

        countries = list(dict.fromkeys([c for c in countries if c]))

        # Insert into database
        self.cursor.execute(
            """
            INSERT INTO films (title, release_year, directors, box_office, countries)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title,
                meta["release_year"],
                json.dumps(directors) if directors else None,
                meta["box_office"],
                json.dumps(countries) if countries else None,
            ),
        )
        self.conn.commit()

    def closed(self, reason):
        self.conn.close()
