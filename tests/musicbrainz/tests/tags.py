import mutagen
import os
import matplotlib.pyplot as plt
import catstuff.tools.common
import yaml

__dir__ = os.path.dirname(os.path.realpath(__file__))

# path = os.path.join(_dir, r'files/Songs About Jane (2002)/Maroon 5 - Songs About Jane (2002) [FLAC]/01 Harder To Breathe.flac')
path = r'C:\Users\S\PycharmProjects\catstuff\catstuff\modules\musicbrainz\tests\files\Overexposed (2012)\Maroon 5 - Overexposed (2012) [MP3 V0]\01 - One More Night.mp3'
tags = mutagen.File(path)

def title(name):
    print('-' * 100)
    print(name)
    print('-' * 100)


if os.path.splitext(path)[1] == '.flac':
    flac = mutagen.flac.FLAC(path)

    title('FLAC repre')
    print(flac)

    title('FLAC vars')
    catstuff.tools.common.print_vars(flac)

    title('FLAC methods')
    catstuff.tools.common.print_methods(flac)

    title('FLAC info attr')
    catstuff.tools.common.print_vars(flac.info)

    title('FLAC properties')
    print(flac.pprint())
else:
    ezid3 = mutagen.easyid3.EasyID3(path)

    title('EZID3 repre')
    print(ezid3)

    title('EZID3 vars')
    catstuff.tools.common.print_vars(ezid3)

    title('EZID3 methods')
    catstuff.tools.common.print_methods(ezid3)

    title('EZID3 properties')
    print(ezid3.pprint())

    title('EZID get')
    for key in ezid3.keys():
        print(key, ":", ezid3.get(key))