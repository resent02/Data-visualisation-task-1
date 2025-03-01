# Quickstart

### Creating Virtual Environment

```python -m venv .venv```
Then you need to activate environment.
Next step is  installing all dependencies.
```pip intall -r requirements.txt```

### Scraping data from Wikipedia and DB init

Run command ```scrapy runspider scrap.py ``` to start scraping. After that all films that a scraped will be in the films.db file (sqlite3 database)

### Creatng json for Github Pages

```python main.py```