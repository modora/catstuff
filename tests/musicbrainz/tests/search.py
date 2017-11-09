import catstuff.tools.common
import os
import catstuff.modules.musicbrainz.main
import yaml

__dir__ = os.path.dirname(os.path.realpath(__file__))

filelist = catstuff.tools.common.import_file_list(os.path.join(__dir__, 'files'),
                                                  mode='blacklist', include=('*.flac', '*.mp3', '*/'), max_depth=-1)

mb = catstuff.modules.musicbrainz.main.Musicbrainz()
result = mb.search('release_groups', query='Songs about jane', artist='Maroon 5', primarytype='ep')

result['release-group-list'] = result['release-group-list'][:4]  # top 5

for i,r in enumerate(result['release-group-list']):
    result['release-group-list'][i] = {
        'artist-credit-phrase': r.get('artist-credit-phrase'),
        'score': r.get('ext:score'),
        'id': r.get('id'),
        'title': r.get('title'),
        'type': r.get('type')
    }

method = 'exp'

scores = [int(r['score']) for r in result['release-group-list']]
rel_scores = {
    'linear': [score / sum(map(lambda x: x, scores)) for score in scores],
    'exp': [2**score / sum(map(lambda x: 2**x, scores)) for score in scores],
}.get(method)

for res, r_score in zip(result['release-group-list'], rel_scores):
    res.update({
        'rel_score': r_score
    })

print(yaml.dump(result, indent=2, default_flow_style=False))