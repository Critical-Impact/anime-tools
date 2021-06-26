# Provides various tools surrounding plex and anime

## Installation

```
$ pip install -r requirements.txt

$ pip install setup.py
```

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

### Environment Setup

The following demonstrates setting up and working with a development environment:

```
### create a virtualenv for development

$ make virtualenv

$ source env/bin/activate


### configuration

Anime Tools needs to be configured before it will run, it also caches the offline database and as such both those paths need to be mounted as volumes.  

Copy config/anime_tools.yml.example to ~/.config/anime_tools/anime_tools.yml and fill in the missing plex details


### run anime_tools cli application

$ anime_tools --help


### run pytest / coverage

$ make test
```


### Releasing to PyPi

Before releasing to PyPi, you must configure your login credentials:

**~/.pypirc**:

```
[pypi]
username = YOUR_USERNAME
password = YOUR_PASSWORD
```

Then use the included helper function via the `Makefile`:

```
$ make dist

$ make dist-upload
```

## Running Anime Tools

### Docker

Included is a basic `Dockerfile` for running `Anime Tools`,
and can be built with the included `make` helper:  
Anime Tools needs to be configured before it will run, it also caches the offline database and as such both those paths need to be mounted as volumes.  

Copy config/anime_tools.yml.example to config/anime_tools.yml and fill in the missing plex details
```
$ make docker # on systems with make
$ docker build -t anime_tools:latest . # on systems with no make
$ docker run -v ./config:/etc/anime_tools -v ./db-cache:/root/.config/anime_tools/db-cache -it anime_tools
```
