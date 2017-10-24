import argparse
import os, platform

sys = platform.system()

defaults = {
    "Windows": {
        'config': '~/My Documents/config/catstuff.yml'
    },
    "Linux": {
        'config': '~/.config/catstuff.yml'
    }
}

d = defaults.get(sys,'Linux')

parser = argparse.ArgumentParser(description='Opens the default editor', prog='catstuff config')

parser.add_argument('-c', '--config', default=d['config'])
parser.add_argument('action', choices=['edit', 'check'])
