import catstuff.tools.modules
import os
import musicbrainzngs

default_version = '0.1'

__dir__ = os.path.dirname(os.path.realpath(__file__))
__plugin_file__ = os.path.join(__dir__, "musicbrainz.plugin")
__mod__, __build__, _ = catstuff.tools.modules.import_core(__plugin_file__)
__version__ = catstuff.tools.modules.import_documentation(__plugin_file__).get('Version') or default_version

username = 'dersal'
password = '$G0M4KrvG60sFsO7'


class Musicbrainz(catstuff.tools.modules.CSCollection):
    def __init__(self, **kwargs):
        super().__init__(__mod__, __build__)
        self.version = __version__

        musicbrainzngs.set_useragent(app='.'.join(('catstuff', __mod__)),
                                     version=self.version)

        defaults = {
            "username": '',
            "password": '',

            'host': 'musicbrainz.org',
            'caa_host': 'coverartarchive.org'
        }

        for (attr, default) in defaults.items():
            setattr(self, attr, kwargs.get(attr, default))

    def auth(self, username, password):
        assert isinstance(username, str)
        assert isinstance(password, str)

        self.username = username
        self.password = password

    def main(self, username, password, **kwargs):
        self.auth(username, password)

    def search(self, service, query='', limit=None, offset=None, strict=False, **fields):
        func = {
            'annotations': musicbrainzngs.search_annotations,
            'areas': musicbrainzngs.search_areas,
            'artists': musicbrainzngs.search_artists,
            'events': musicbrainzngs.search_events,
            'instruments': musicbrainzngs.search_instruments,
            'labels': musicbrainzngs.search_labels,
            'places': musicbrainzngs.search_places,
            'recordings': musicbrainzngs.search_recordings,  # songs
            'release_groups': musicbrainzngs.search_release_groups,
            'releases': musicbrainzngs.search_releases,  # albums
            'series': musicbrainzngs.search_series,
            'works': musicbrainzngs.search_works
        }.get(service)
        if func is None:
            raise NotImplementedError("{} not a search option".format(service))
        return func(query=query, limit=limit, offset=offset, strict=strict,
                    **fields)