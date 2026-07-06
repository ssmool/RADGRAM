def suggest_chords(key='C', mood='cinematic'):
    table={'C':{'happy':['C','G','Am','F'], 'sad':['Am','F','C','G'], 'cinematic':['C','Am','F','G']}}
    return table.get(key, table['C']).get(mood, table['C']['cinematic'])

def parse_chord_line(line):
    return [x.strip() for x in line.replace('|',' ').split() if x.strip()]
