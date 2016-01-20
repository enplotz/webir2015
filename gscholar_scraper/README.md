# GScholar Scraper Spider

The spiders can be run locally or using the scrapyd daemon. The native installation is intended for easier testing,
whereas the docker version supports a much more stable and quick setup if you just want to run the platform.

## Using Docker

The PostgreSQL storage pipeline uses the environment variables present on the system that runs `scrapyd`.

### Deploy Spider Using `docker-scrapyd`

*Note:* If you are using `docker-machine` (so you are on Mac OS or Windows), you have to put the machines IP address into `scrapy.cfg`
(under the [deploy:docker] section). If docker is running locally on your machine (e.g. Linux) put `localhost` there.

Deploy the scrapy project to scrapyd running in the docker container.
```
scrapy-deploy docker
```

## Native Installation

The following part describes the local installation and configuration necessary to run the scrapy spiders.

### Installation

The project uses Python 2.7 and assumes a PostgreSQL installation of at least version 9.4.
All required libraries are named in `requirements.txt`. Install them with `pip install -r requirements.txt`.

For the proxy connection a socks proxy (e.g. tor) can be used, together with a http proxy
to fire the actual requests against.

Recommended proxies:

- socks proxy: standard tor client
- http proxy: `privoxy` or `polipo`

See `settings.py` for the appropriate http proxy port. If you do not want to use a proxy, you can disable the proxy
middleware in the scrapy settings.

### Configuration

Environment variables (or crawler settings) are used to configure credentials like passwords or database connections.
 The files `*.env-sample` contain all parameters that are currently used (with placeholders). To provide your values,
 strip the suffix `-sample` from the files and fill in your values.
 So the file `database.env` contains the correct postgres connection credentials. The docker-compose file automatically
 includes these files, but what about command-line execution? For this, you can export the variables as environment variables.
 Prefix your command `foo` like so:
```
export $(cat ../*.env | xargs) && foo`
```
This command assumes that you are in the 
 folder `gscholar_scraper`, so the environment files are one level up.

#### Tor Control

The following config parameters are used to control the tor client using the built in class:

- `TOR_CONTROL_PASSWORD=...`

File: `proxy.env`

#### Database Access

The postgreSQL database is accessed using the following parameters:

- `SCRAPY_DB_HOST=...`
- `SCRAPY_DB_PORT=...`
- `SCRAPY_DB_USERNAME=...`
- `SCRAPY_DB_PASSWORD=...`
- `SCRAPY_DB_DATABASE=...`

File: `database.env`

### Deploy Spider Using Local Scrapyd

If you do not want to use docker, but still want to use scrapyd, you can just run scrapyd and deploy your projects
locally:

```
$ scrapyd &
```

Then in another shell in the `gscholar_scraper` directory run:
```
$ scrapy-deploy
```

Then schedule the spiders via the commands outline in *Testing Spiders Deployed To Scrapyd*.

### Run Spider Without Scrapyd

To run the spiders locally, issue the crawl command from the scrapy project directory (so, where the `scrapy.cfg` is).
You can list available spiders and run them.
```
scrapy crawl your_spiders_name
```

To pass spider settings, you can use the `-a` flag, e.g. `scrapy crawl dmoz -a my_param=itworks`.

## First run

Run the spiders in the following order:
 `author_labels --> author_general --> (author_detail | author_co | author_org)` 

The crawling process is seeded using a list of popular last names. See file `names.txt` for the list.

The spiders should create most of their database tables on their own (sans indexes for more speedy writes), 
when supplied with correct credentials.

A spider can be run via the command line (1) or programatically (2,3).

1.
    - `scrapy crawl author_detail -L INFO -a start_authors="YJm9he0AAAAJ"` to crawl detail information about the author having the id
      `YJm9he0AAAAJ`.
    - `scrapy crawl author_labels -L INFO` to crawl the labels of scientists having popular names.
2.
    - Using for example the PyCharm run configurations: Select `main.py` as the script and 
    `author_detail -L INFO -a start_authors="YJm9he0AAAAJ` as the script parameters. The scripts parameters are documented
    and accessible via the `-h` flag (or without any parameters).
3.
    See the scrapy documentation.
    
When run the spiders produce a lot of write-heavy load on the database server. Also currently they lack the capability 
of pause/resume. So when you stop a spider, it might pick up at the start of the list of labels again.

## Testing Spiders Deployed To Scrapyd

The easiest way to test the API endpoints of the running scrapyd service is
 to install [Postman](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop). 
 This way, you can somewhat interactively explore the API and its responses.

### Running A Deployed Spider On Scrapyd

We will test with the typical dmoz spider, that is included in all scrapy tutorials.
 The spider crawls two pages on dmoz, extracts items and stores them in the PostgreSQL 
 database (that you configured in the file `database.env`) in the table `websites`. 
 It will create the table if necessary (through SQLAlchemy).

To schedule a spider make a `POST` request to the url:
```
http://IP-FROM-DOCKER-MACHINE:6800/schedule.json
```

The parameters are:
```
URL Parameter Key : Value
project : tutorial
spider : dmoz
my_param : additional_params_like_so
```

The response body should contain json like the following:
```
{
  "status": "ok",
  "jobid": "a22bcb0abf0611e588740242ac110018",
  "node_name": "2f95918d7828"
}
```

To see if everything went smoothly, do a `SELECT * FROM websites` in your database.
 It should now contain several rows. Somewhere in the logs (go to the scrapyd services website) the additional
 parameter `my_param` should be printed. You can pass additional keyword parameters to spiders. See the dmoz spider
 how you can access them.

If you see an error like `exceptions.RuntimeError: Use "scrapy" to see available commands` this could mean, that you
 forgot to deploy your scrapy project to the scrapyd service.

