import os
from urllib.request import URLopener
import time

from cement import fs

def download_database(app):
    app.log.info('Checking offline database')
    db_cache_path = fs.abspath('~/.config/anime_tools/db-cache')
    app.log.info('Checking in ' + db_cache_path)
    fs.ensure_dir_exists(db_cache_path)
    offline_database = os.path.join(db_cache_path,"offline_database.json")
    should_download_database: bool = False
    if os.path.exists(offline_database):
        age = time.time() - os.path.getmtime(offline_database)
        if(age > 86400):
            should_download_database = True
    else:
        should_download_database = True
    if should_download_database:
        testfile = URLopener()
        testfile.retrieve("https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json", offline_database)
        app.log.info('Offline database downloaded')
    else:
        app.log.info('Cached database is up to date')
