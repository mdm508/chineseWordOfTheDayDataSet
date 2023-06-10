import csv
import json
from cedict_utils.cedict import CedictParser


parser = CedictParser()
parser.read_file('cedict.txt')
entries = parser.parse()

db = {}
duplicates = []
for item in entries:
    if item.meanings != "#":
        if item.traditional in db:
            duplicates.append(item.traditional)
            db[item.traditional].meanings.extend(item.meanings)
        else:
            db[item.traditional] = item
        # db[item.traditional] = item

def main():
    with open('data.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        with open('output.json', 'w', newline='', encoding='utf-8') as write_file:
            out_array = []
            alternates = []
            for row in reader:
                index = row['\ufeffindex']
                trad = row['word']
                level = row['levelNumber']
                context = row['context']
                written_frequency = row['writtenFrequencyPerMillion']
                spoken_frequency = row['spokenFrequencyPerMillion']
                frequency = row['frequencyPerMillion']
                zhuyin = row['zhuyin']
                pinyin = row['pinyin']
                if '/' in trad:
                    #handle special case when word has multiple ways to write it 哥哥/哥 for example
                    #search based off the first one
                    alternates = trad.split('/')
                    trad = alternates[0]
                if trad in db:
                    entry = db[trad]
                    if alternates:
                        entry.meanings.append("same as {}".format(','.join(alternates[1:])))
                    data = [
                        index,
                        trad,
                        zhuyin,
                        entry.simplified,
                        pinyin,
                        level,
                        entry.meanings,
                        level,
                        context,
                        written_frequency,
                        spoken_frequency,
                        frequency
                    ]
                    keys = [
                        'index',
                        'traditional',
                        'zhuyin',
                        'simplified',
                        'pinyin',
                        'level',
                        'meanings',
                        'level',
                        'context',
                        'writtenFrequency',
                        'spokenFrequency',
                        'frequency'
                    ]
                    result = dict(zip(keys, data))
                    out_array.append(result)
                else:
                    print(trad)
            print(len(out_array), 'written')
            json.dump(out_array, write_file, ensure_ascii=False, indent=4)



main()


