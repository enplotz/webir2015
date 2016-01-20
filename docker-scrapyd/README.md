Scrapyd Docker Image
======================

Please read the whole readme before executing any lines.

To build this image use: 

```sh
docker build -t webir2015/scrapyd:latest .
```

You may edit these files:

- `packages.txt` - additional packages to be installed (via `apt-get install`)
- `dependencies.txt` - dependencies for python requirements (via `apt-get install/purge`)
- `requirements.txt` - additional python packages to be installed (via `pip install`)

If you prefer to experiment, what you have to put in these three files, you can attach to the running container using:

```sh
docker exec -it webir2015_scrapyd bash
```

If you are using *docker-machine* (so on a Mac), do not forget that the container will have a different IP address than
`localhost`. Use `eval "$(docker-machine env dev)"` followed by `docker-machine ip dev` to get the IP of the machine `dev`.

To inspect the logs of the running container use:

```sh
docker logs --follow webir2015_scrapyd
```

If you are using `docker-compose` use `docker-compose logs` to follow all the logs.



**OLD README CONTENTS BELOW:**

scrapyd-onbuild
===============

Dockerfile for building an image that runs [scrapyd][1].  

Please use this image as base for your own project.

You may edit these files:

- `packages.txt` - additional packages to be installed (via `apt-get install`)
- `dependencies.txt` - dependencies for python requirements (via `apt-get install/purge`)
- `requirements.txt` - additional python packages to be installed (via `pip install`)

[1]: https://github.com/scrapy/scrapyd
