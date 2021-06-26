
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal

from anime_tools.controllers.genres import Genres
from .download_database import download_database
from .plex import connect_plex
from .core.exc import AnimeToolsError
from .controllers.base import Base

# configuration defaults
CONFIG = init_defaults('anime_tools')
CONFIG['anime_tools']['foo'] = 'bar'


class AnimeTools(App):
    """Anime Tools primary application."""

    class Meta:
        label = 'anime_tools'

        # configuration defaults
        config_defaults = CONFIG



        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
        ]

        hooks = [
            ('post_setup', download_database, 0),
            ('pre_run', connect_plex, 0),
        ]


        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        # register handlers
        handlers = [
            Base,
            Genres
        ]


class AnimeToolsTest(TestApp,AnimeTools):
    """A sub-class of AnimeTools that is better suited for testing."""

    class Meta:
        label = 'anime_tools'


def main():
    with AnimeTools() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except AnimeToolsError as e:
            print('AnimeToolsError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
