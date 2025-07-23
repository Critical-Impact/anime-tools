import os
import time
import urllib.request
import shutil
import time

from cement import fs

DB_URL = "https://github.com/manami-project/anime-offline-database/releases/latest/download/anime-offline-database.json"

def download_database(app):
    app.log.info('Checking offline database')
    db_cache_path = fs.abspath('~/.config/anime_tools/db-cache')
    app.log.info('Checking in ' + db_cache_path)
    fs.ensure_dir_exists(db_cache_path)
    offline_database = os.path.join(db_cache_path, "offline_database.json")

    should_download_database = (
        not os.path.exists(offline_database) or
        (time.time() - os.path.getmtime(offline_database)) > 86400
    )

    if should_download_database:
        app.log.info('Downloading offline database...')
        with urllib.request.urlopen(DB_URL) as resp, open(offline_database, 'wb') as out_f:
            shutil.copyfileobj(resp, out_f)
        app.log.info('Offline database downloaded')
    else:
        app.log.info('Cached database is up to date')
