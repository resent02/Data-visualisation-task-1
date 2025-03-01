# Quickstart

### Creating Virtual Environment

```python -m venv .venv```
Then you need to activate environment.
Next step is  installing all dependencies.
```pip intall -r requirements.txt```
### Initializing Database

To init DB you need to run ```python db.py``` It will create films.db which will contain all films after inserting in the next step


### Scraping data from Wikipedia

Run command ```scrapy runspider scrap.py ``` to start scraping. After that all films that a scraped will be in the films.db file (sqlite3 database)