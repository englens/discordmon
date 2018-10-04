import poke_data
from pathlib import Path
all = []
for move in  [Path(name).stem for name in Path('./data/move_reference/').iterdir()]:
    for e in poke_data.get_move(move)['effect_entries']:
        all.append(e['effect'])