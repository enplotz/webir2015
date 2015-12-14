# GScholar Scraper Spider

The following readme describes the installation and configuration necessary to run the scrapy spiders.

# Installation

The project uses Python 2.7 and assumes a PostgreSQL installation of at least version 9.4.
All required libraries are named in `requirements.txt`. Install them with `pip install -r requirements.txt`.

For the proxy connection a socks proxy (e.g. tor) can be used, together with a http proxy
to fire the actual requests against.

Recommended proxies:

- socks proxy: standard tor client
- http proxy: `privoxy` or `polipo`

See `settings.py` for the appropriate http proxy port. If you do not want to use a proxy, you can disable the proxy
middleware in the scrapy settings.

# Configuration

The file `.env` (create it next to `settings.py`) is used for confidential configuration parameters that should not end up in version control.

## Tor Control

The following config parameters are used to control the tor client using the built in class:

- `TOR_CONTROL_PASSWORD=...`

## Database Access

The postgreSQL database is accessed using the following parameters:

- `DB_HOST=...`
- `DB_PORT=...`
- `DB_USERNAME=...`
- `DB_PASSWORD=...`
- `DB_DATABASE=...`

# First run

Run the spiders in the following order:
 `author_labels --> author_general --> (author_detail | author_co | author_org)` 

The crawling process is seeded using a list of popular last names. See file `names.txt` for the list.

The spiders should create most of their database tables on their own (sans indexes for more speedy writes), 
when supplied with correct credentials. So be sure to create the `.env` file and fill in yours.

A spider can be run via the command line (1) or programatically (2).

1.
    - `scrapy crawl author_detail -L INFO -a start_authors="YJm9he0AAAAJ"` to crawl detail information about the author having the id
      `YJm9he0AAAAJ`.
    - `scrapy crawl author_labels -L INFO` to crawl the labels of scientists having popular names.
2.
    - Using for example the PyCharm run configurations: Select `main.py` as the script and 
    `author_detail -L INFO -a start_authors="YJm9he0AAAAJ` as the script parameters. The scripts parameters are documented
    and accessible via the `-h` flag (or without any parameters).
    
When run the spiders produce a lot of write-heavy load on the database server. Also currently they lack the capability 
of pause/resume. So when you stop a spider, it might pick up at the start of the list of labels again.

