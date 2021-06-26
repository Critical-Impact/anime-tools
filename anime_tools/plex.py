import os
from urllib.request import URLopener
import time

from plexapi.exceptions import BadRequest
from plexapi.server import PlexServer
from cement import fs, App



def connect_plex(app):
    if not app.config.has_option('anime_tools', 'plex_token') or not app.config.has_option('anime_tools', 'plex_address') or not app.config.has_option('anime_tools', 'plex_libraries'):
        app.log.error('Plex not configured, closing application')
        app.close(1)
    else:
        plex_token = app.config.get('anime_tools', 'plex_token')
        plex_address = app.config.get('anime_tools', 'plex_address')
        plex_libraries = app.config.get('anime_tools', 'plex_libraries')
        try:
            plex = PlexServer(plex_address, plex_token)
        except BadRequest:
            app.log.error('Failed to connect to plex')
            return app.close()
        app.log.info('Plex connection successful')
        app.config.set(section='anime_tools',key='plex_server', value=plex)
