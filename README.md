# [Project] Web Information Retrieval 2015

Task: Crawling of Google Scholar

## Project Architecture

The project prototype consists of two applications. A web scraper (a collection of *scrapy* spiders) to scrape information
 from Google Scholar and a *flask* web application to show and analyze the scraped data.

Annotated directory structure and useful files:
```
.
├── README.md                   -- current readme
├── gscholar_scraper            -- scraper project root
│   ├── README.md               -- more information on the scraper
│   ├── gscholar_scraper        -- scraper implementation
│   │   ├── models
│   │   ├── ...
│   │   ├── settings.py
│   │   ├── spiders
│   │   │   ├── ...
│   ├── main.py                 -- programmatic access to the spiders
│   ├── names.txt               -- list of 1000 most frequent english names
│   ├── requirements.txt        
│   └── scrapy.cfg              -- config for scrapy
└── webapp                      -- webapp project root
    ├── __init__.py             -- python file that contains the small webapp (view & controller logic)
    ├── config.py               
    ├── queries
    │   ├── ...
    ├── requirements.txt
    ├── static                  -- static files, like css and js
    │   ├── ...
    └── templates               -- page templates
        ├── ...
```

The scraper consists of a couple of *scrapy* spiders, notably:

- `author_labels`: Searches for the names in `SEED_NAME_LIST` (see settings.py) and scrapes the labels from author's 
  profiles
- `author_general`: Searches for all labels in the database and scrapes general author information
- `author_detail`: Complements existing author information by requesting the profile page of specific authors
- `author_co`: Scrapes co-authorship information of specified authors

A typical scraping workflow using the above spiders would be, to first scrape label information using the popular names,
then getting authors for these labels and finally augmenting general author information by detail information regarding
scientific measurements or co-authorship.

## Installation / Usage

Required software:

- PostgreSQL > 9.4
- Python 2.7

### `gscholar_scraper`

- Python libraries: see `gscholar_scraper/requirements.txt` (tip: these can be installed by pip using the file!)
- `cd gscholar_scraper && pip install -r requirements.txt`

For usage details see `gscholar_scraper/README.md`.

### `webapp`

- Python libraries: see `webapp/requirements.txt`
- `cd webapp && pip install -r requirements.txt`

To configure the webapp, copy over your `.env` file from the scraper sub-directory and put it next to `config.py`.
Additionally, set the desired app settings via the env key `APP_SETTINGS=...` with one of the following:
 
 - config.DevelopmentConfig
 - config.ProductionConfig
 
If you are running the webapp in production, be sure to set the env key `SECRET_KEY` to a long and random value.

The webapp can be started via `cd webapp && python __init__.py` and normally accessed via `http://localhost:5000`.


