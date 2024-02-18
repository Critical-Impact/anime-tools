import plexapi.exceptions
from cement import Controller, ex, fs
import os
import json
import re, string
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

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
        library_name = self.app.pargs.library_name
        show_name = self.app.pargs.show_name
        self.app.log.info('Attempting to update show %s on library %s' % (show_name, library_name))

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


        indexed_dict = self.parse_offline_database()
        self.parse_results(indexed_dict, results)

    @ex(
        help='update genres on shows that have been added within a certain time',
        arguments=[
            (['library_name'], {'help': 'the name of the library to update', 'action': 'store'}),
            (['relative_date'],
             {'help': 'the relative day formatted like 30s, 20m, 2h, 1d, 1w, 3mon, 2y', 'action': 'store'})
        ],
    )
    def update_date_relative(self):
        library_name = self.app.pargs.library_name
        relative_date = self.app.pargs.relative_date
        self.app.log.info('Attempting to update shows added within %s on library %s' % (relative_date, library_name))
        plex_server: PlexServer = self.app.config.get('anime_tools', 'plex_server')
        try:
            library = plex_server.library.section(library_name)

        except plexapi.exceptions.NotFound as e:
            self.app.log.info(f"Plex library {library_name} not found.")
            self.app.close(1)
            return

        results = library.search(filters={"addedAt>>": relative_date})
        indexed_dict = self.parse_offline_database()
        self.parse_results(indexed_dict, results)

    @ex(
        help='update genres for an entire library',
        arguments=[
            (['library_name'], {'help': 'the name of the library to update', 'action': 'store'})
        ],
    )
    def update_all(self):
        library_name = self.app.pargs.library_name
        self.app.log.info('Updating all shows on %s' % (library_name))
        plex_server: PlexServer = self.app.config.get('anime_tools', 'plex_server')
        try:
            library = plex_server.library.section(library_name)

        except plexapi.exceptions.NotFound as e:
            self.app.log.info(f"Plex library {library_name} not found.")
            self.app.close(1)
            return

        results = library.search()
        indexed_dict = self.parse_offline_database()
        self.parse_results(indexed_dict, results)

    def parse_offline_database(self):
        indexed_dict = {}
        db_cache_path = fs.abspath('~/.config/anime_tools/db-cache')
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
                    if "year" in item["animeSeason"]:
                        item_title = item['title'] + " (" + str(item["animeSeason"]["year"]) + ")"
                        item_title = self.sanitize_title(item_title)
                        indexed_dict[item_title] = item
                for synonym in item['synonyms']:
                    synonym_title = synonym
                    synonym_title = self.sanitize_title(synonym_title)
                    indexed_dict[synonym_title] = item
                    if "animeSeason" in item:
                        if "year" in item["animeSeason"]:
                            synonym_title = synonym + " (" + str(item["animeSeason"]["year"]) + ")"
                            synonym_title = self.sanitize_title(synonym_title)
                            indexed_dict[synonym_title] = item
        return indexed_dict

    def parse_results(self, indexed_dict, results):
        fuzzy_matching = self.app.config.get('anime_tools', 'use_fuzzy_matching')
        fuzzy_ratio = self.app.config.get('anime_tools', 'fuzzy_ratio')

        if fuzzy_matching:
            for library_item in results:
                plex_title = self.sanitize_title(library_item.title)
                self.app.log.info(f"Using fuzzy matching.")
                match_found = False
                match = {}
                fuzz_match = False
                ratio = 0
                if plex_title in indexed_dict:
                    indexed_item = indexed_dict[plex_title]
                    self.app.log.info(
                        f"Found {library_item.title} directly matching in json, updating genres.")
                    library_item.addGenre(indexed_item['tags'])
                else:
                    for key, item in indexed_dict.items():
                        ratio = fuzz.ratio(plex_title, key)
                        self.app.log.debug(f"Compared {plex_title} and {key}, ratio = {ratio}.")
                        if ratio >= fuzzy_ratio:
                            match_found = True
                            match = item
                            fuzz_match = key
                            break
                    if match_found:
                        self.app.log.info(
                            f"Found {library_item.title} matching {fuzz_match} with a {ratio}% certainty in json, updating genres.")
                        library_item.addGenre(match['tags'])
                    else:
                        self.app.log.info(f"Could not find {library_item.title}, searching for {plex_title} in json.")
        else:
            for library_item in results:
                plex_title = self.sanitize_title(library_item.title)
                if plex_title in indexed_dict:
                    indexed_item = indexed_dict[plex_title]
                    self.app.log.info(f"Found {library_item.title} in json, updating genres.")
                    library_item.addGenre(indexed_item['tags'])
                else:
                    self.app.log.info(f"Could not find {library_item.title}, searching for {plex_title} in json.")

    def sanitize_title(self, title):
        fuzzy_matching = self.app.config.get('anime_tools', 'use_fuzzy_matching')
        if fuzzy_matching:
            return title.strip().lower()
        else:
            pattern = re.compile('[\W_]+')
            title = pattern.sub('', title)
            title = re.sub("\s\s+", '', title)
            title = title.replace(" ", "")
            title = title.strip().lower()
            return title
