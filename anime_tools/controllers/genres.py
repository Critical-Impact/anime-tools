import plexapi.exceptions
from cement import Controller, ex, fs
import os
import json
import re, string

from plexapi.server import PlexServer


class Genres(Controller):
    class Meta:
        label = 'genres'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(
        help='update genres on a single show',
        arguments=[
            (['library_name'], {'help': 'the name of the library to update', 'action': 'store'}),
            (['show_name'], {'help': 'the name of the show to update', 'action': 'store'})
        ],
    )
    def update(self):
        indexed_dict = {}
        library_name = self.app.pargs.library_name
        show_name = self.app.pargs.show_name
        db_cache_path = fs.abspath('~/.config/anime_tools/db-cache')
        self.app.log.info('Attempting to update show %s on library %s' % (show_name, library_name))
        offline_database = os.path.join(db_cache_path, "offline_database.json")

        # Sanitize all the titles of the shows and their other given titles in the offline database and index them
        with open(offline_database, encoding='utf-8') as json_file:
            data = json.load(json_file)
            actual_data = data['data']
            for item in actual_data:
                item_title = item['title']
                item_title = self.sanitize_title(item_title)
                indexed_dict[item_title] = item
                if "animeSeason" in item:
                    item_title = item['title'] + " (" + str(item["animeSeason"]["year"]) + ")"
                    item_title = self.sanitize_title(item_title)
                    indexed_dict[item_title] = item
                for synonym in item['synonyms']:
                    synonym_title = synonym
                    synonym_title = self.sanitize_title(synonym_title)
                    indexed_dict[synonym_title] = item
                    if "animeSeason" in item:
                        synonym_title = synonym + " (" + str(item["animeSeason"]["year"]) + ")"
                        synonym_title = self.sanitize_title(synonym_title)
                        indexed_dict[synonym_title] = item

        plex_server: PlexServer = self.app.config.get('anime_tools', 'plex_server')
        try:
            library = plex_server.library.section(library_name)

        except plexapi.exceptions.NotFound as e:
            self.app.log.info(f"Plex library {library_name} not found.")
            self.app.close(1)
            return

        results = library.search(title=show_name)

        if len(results) == 0:
            self.app.log.info(f"Show {show_name} could not be found in library {library_name}.")

        for library_item in results:
            plex_title = self.sanitize_title(library_item.title)
            if plex_title in indexed_dict:
                indexed_item = indexed_dict[plex_title]
                self.app.log.info(f"Found {library_item.title} in json, updating genres.")
                library_item.addGenre(indexed_item['tags'])
            else:
                self.app.log.info(f"Could not find {library_item.title}, searching for {plex_title} in json.")

    @ex(
        help='update genres for an entire library',
        arguments=[
            (['library_name'], {'help': 'the name of the library to update', 'action': 'store'})
        ],
    )
    def update_all(self):
        indexed_dict = {}
        library_name = self.app.pargs.library_name
        db_cache_path = fs.abspath('~/.config/anime_tools/db-cache')
        self.app.log.info('Updating all shows on %s' % (library_name))
        offline_database = os.path.join(db_cache_path, "offline_database.json")

        # Sanitize all the titles of the shows and their other given titles in the offline database and index them
        with open(offline_database, encoding='utf-8') as json_file:
            data = json.load(json_file)
            actual_data = data['data']
            for item in actual_data:
                item_title = item['title']
                item_title = self.sanitize_title(item_title)
                indexed_dict[item_title] = item
                if "animeSeason" in item:
                    item_title = item['title'] + " (" + str(item["animeSeason"]["year"]) + ")"
                    item_title = self.sanitize_title(item_title)
                    indexed_dict[item_title] = item
                for synonym in item['synonyms']:
                    synonym_title = synonym
                    synonym_title = self.sanitize_title(synonym_title)
                    indexed_dict[synonym_title] = item
                    if "animeSeason" in item:
                        synonym_title = synonym + " (" + str(item["animeSeason"]["year"]) + ")"
                        synonym_title = self.sanitize_title(synonym_title)
                        indexed_dict[synonym_title] = item

        plex_server: PlexServer = self.app.config.get('anime_tools', 'plex_server')
        try:
            library = plex_server.library.section(library_name)

        except plexapi.exceptions.NotFound as e:
            self.app.log.info(f"Plex library {library_name} not found.")
            self.app.close(1)
            return

        for library_item in library.search():
            plex_title = self.sanitize_title(library_item.title)
            if plex_title in indexed_dict:
                indexed_item = indexed_dict[plex_title]
                self.app.log.info(f"Found {library_item.title} in json, updating genres.")
                library_item.addGenre(indexed_item['tags'])
            else:
                self.app.log.info(f"Could not find {library_item.title}, searching for {plex_title} in json.")

    def sanitize_title(self, title):
        pattern = re.compile('[\W_]+')
        title = pattern.sub('', title)
        title = re.sub("\s\s+", '', title)
        title = title.replace(" ", "")
        title = title.strip().lower()
        return title
