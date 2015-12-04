# GScholar Scraper Spider

# Installation

All required libraries are in `requirements.txt`. Install them with `pip`.
For the proxy connection a socks proxy (e.g. tor) can be used, together with a http proxy
to fire the actual requests against.

Recommended proxies:
- socks proxy: standard tor client
- http proxy: `privoxy` or `polipo`

Look into the `settings.py` for the appropriate http proxy port.
