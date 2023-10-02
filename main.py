import csv
import json
import re
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
    pattern = r'see.*\[.*\]'
    with open('data.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        with open('output.json', 'w', newline='', encoding='utf-8') as write_file:
            out_array = []
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
                traditional = trad.split('/')[0]
                if traditional in db:
                    entry = db[traditional]
                    # skip any words whose only meaning is of the form ["see 下工夫[xia4 gong1 fu5]"]'
                    # these dont provide any definitions
                    if len(entry.meanings) == 1:
                        if re.search(pattern, entry.meanings[0]):
                            continue
                    if len(zhuyin.split('/')) != len(trad.split('/')):
                        print(trad, pinyin)
                    # i also dont want these types of strings appearing in meaning section
                    meanings = list(filter(lambda m: not re.search(pattern, m), entry.meanings))
                    data = [
                        int(index),
                        traditional,
                        zhuyin.split('/')[0],
                        entry.simplified,
                        pinyin.split('/')[0],
                        float(level),
                        meanings,
                        context,
                        int(written_frequency),
                        int(spoken_frequency),
                        int(frequency),
                        # handle special case when word has multiple ways to write it 哥哥/哥 for example
                        # search based off the first one
                        trad.split('/')[1:],
                        #zhuyin.split('/')[1:],
                        #pinyin.split('/')[1:]


                    ]
                    keys = [
                        'index',
                        'traditional',
                        'zhuyin',
                        'simplified',
                        'pinyin',
                        'level',
                        'meanings',
                        'context',
                        'writtenFrequency',
                        'spokenFrequency',
                        'frequency',
                        'synonyms',
                        'synonymsZhuyin',
                        'synonymsPinyin'
                    ]
                    result = dict(zip(keys, data))
                    out_array.append(result)
                else:
                    pass
                    #print(trad)
            print(len(out_array), 'written')
            json.dump(out_array, write_file, ensure_ascii=False, indent=4)



main()


