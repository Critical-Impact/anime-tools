from argparse import Namespace
from cement import Controller, ex, fs
import os
import json
import re, string;

from plexapi.library import LibrarySection
from plexapi.server import PlexServer

indexedDict = {}

class Genres(Controller):
    class Meta:
        label = 'genres'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(
        help='update genres on all shows',
        arguments=[
            (['library_name'],{'help': 'the name of the library to update','action': 'store'}),
            (['show_name'],{'help': 'the name of the show to update','action': 'store'})
        ],
    )
    def update(self):
        libraryName = self.app.pargs.library_name
        showName = self.app.pargs.show_name
        db_cache_path = fs.abspath('./../db-cache')
        self.app.log.info('Updating : %s on %s' % (showName, libraryName))
        offline_database = os.path.join(db_cache_path, "offline_database.json")
        plex_token = self.app.config.get('anime_tools', 'plex_token')
        pattern = re.compile('[\W_]+')

        with open(offline_database, encoding='utf-8') as json_file:
            data = json.load(json_file)
            actualData = data['data']
            for item in actualData:
                itemTitle = item['title'].strip().lower()
                itemTitle = pattern.sub('', itemTitle)
                itemTitle = re.sub("\s\s+", '', itemTitle)
                itemTitle = itemTitle.replace(" ", "")
                itemTitle = itemTitle.strip().lower()
                indexedDict[itemTitle] = item
                if "animeSeason" in item:
                    itemTitle = itemTitle + " (" + str(item["animeSeason"]["year"]) + ")"
                    itemTitle = pattern.sub('', itemTitle)
                    itemTitle = re.sub("\s\s+", '', itemTitle)
                    itemTitle = itemTitle.replace(" ", "")
                    itemTitle = itemTitle.strip().lower()
                    indexedDict[itemTitle] = item
                for synonym in item['synonyms']:
                    synonymTitle = synonym.strip().lower()
                    synonymTitle = pattern.sub('', synonymTitle)
                    synonymTitle = re.sub("\s\s+", '', synonymTitle)
                    synonymTitle = synonymTitle.replace(" ", "")
                    synonymTitle = synonymTitle.strip().lower()
                    indexedDict[synonymTitle] = item
                    if "animeSeason" in item:
                        synonymTitle = synonymTitle + " (" + str(item["animeSeason"]["year"]) + ")"
                        synonymTitle = pattern.sub('', synonymTitle)
                        synonymTitle = re.sub("\s\s+", '', synonymTitle)
                        synonymTitle = re.sub(" ", '', synonymTitle)
                        synonymTitle = synonymTitle.replace(" ", "")
                        synonymTitle = synonymTitle.strip().lower()
                        indexedDict[synonymTitle] = item
        plex_server: PlexServer = self.app.config.get('anime_tools','plex_server')
        anime = plex_server.library.section('Anime')
        animeItem: LibrarySection
        for animeItem in anime.search():
            plexTitle = animeItem.title.strip().lower()
            plexTitle = pattern.sub('', plexTitle)
            plexTitle = re.sub("\s\s+", '', plexTitle)
            plexTitle = plexTitle.replace(" ", "")
            plexTitle = plexTitle.strip().lower()
            if plexTitle in indexedDict:
                indexedItem = indexedDict[plexTitle]
                #self.app.log.info(f"Found {animeItem.title} in json, updating genres.")
                animeItem.addGenre(indexedItem['tags'])
            else:
                self.app.log.info(f"Could not find {animeItem.title}, searching for {plexTitle} in json.")
