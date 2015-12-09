# GScholar Scraper Spider

The following readme describes the installation and configuration necessary to run the scrapy spiders.

# Installation

All required libraries are in `requirements.txt`. Install them with `pip install -r requirements.txt`.

For the proxy connection a socks proxy (e.g. tor) can be used, together with a http proxy
to fire the actual requests against.

Recommended proxies:

- socks proxy: standard tor client
- http proxy: `privoxy` or `polipo`

See `settings.py` for the appropriate http proxy port.

# Configuration

The file `.env` is used for confidential configuration parameters that should not end up in version control.

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

- ... TODO

The crawling process is seeded using a list of popular last names. See file `TODO` for the list.
