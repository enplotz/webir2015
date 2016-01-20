# From https://github.com/vimagick/dockerfiles/scrapyd
#


# We use the ONBUILD functionality from docker, to get a clean docker file for ourselves.
# Dockerfiles with ONBUILD instructions are a quick way to start our own (customized) applications from images.
# More: https://docs.docker.com/engine/reference/builder/#onbuild

FROM vimagick/scrapyd-onbuild
MAINTAINER Manuel Hotz <hi@enplotz.de>

# The onbuild-image already contains instructions to use the following three files:
# packages.txt - additional packages to be installed (via apt-get install)
# dependencies.txt - dependencies for python requirements (via apt-get install/purge)
# requirements.txt - additional python packages to be installed (via pip install)
#

