# Provides various tools surrounding plex and anime

## Local Installation

```
$ pip install -r requirements.txt

$ pip install setup.py
```

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

### Configuration

Anime Tools needs to be configured before it will run, it also caches the offline database.
If you are using docker, both the cache path and configuration path should be mapped.

Copy config/anime_tools.yml.example to ~/.config/anime_tools/anime_tools.yml and fill in the missing plex details.


### Environment Setup

The following demonstrates setting up and working with a development environment:

```
### create a virtualenv for development

$ make virtualenv

$ source env/bin/activate

### run anime_tools cli application

$ anime_tools --help


### run pytest / coverage

$ make test
```

## Running Anime Tools

### Docker

Copy config/anime_tools.yml.example to config/anime_tools.yml and fill in the missing plex details
```
$ make docker # on systems with make
$ docker build -t anime_tools:latest . # on systems with no make
$ docker run -v ./config:/etc/anime_tools -v ./db-cache:/root/.config/anime_tools/db-cache -it anime_tools
```

### Usage

####Updating a single show  
anime_tools update_all [library name] [show name]

####Updating an entire library  