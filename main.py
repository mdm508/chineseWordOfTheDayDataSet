import csv
import json
import re
from cedict_utils.cedict import CedictParser

def build_db(entries):
    """
    return a dictionary of entries with the traditional character as the key
    as well as list of duplicates
    :param entries: list of entries from cedict
    duplicate meaning will be appended to the existing word.
    """
    db = {}
    duplicates = []
    for item in entries:
        if item.meanings != "#":
            if item.traditional in db:
                duplicates.append(item.traditional)
                db[item.traditional].meanings.extend(item.meanings)
            else:
                db[item.traditional] = item
    return db, duplicates

def filter_rows(reader, db, pattern):
    # filter out rows that are not in the cedict dictionary
    # also filter out rows that have a different number of zhuyin and trad characters
    # also filter out rows that have a meaning of the form ["see 下工夫[xia4 gong1 fu5]"]
    # side effect: modifies the row dictionary to include meanings with the pattern removed
    filtered_rows = []
    filtered_out = []
    for row in reader:
        trad = row['word']
        traditional = trad.split('/')[0]
        if traditional in db:
            entry = db[traditional]
            if len(entry.meanings) == 1 and re.search(pattern, entry.meanings[0]):
                filtered_out.append(trad)
                continue
            # Skip if zhuyin and trad lengths do not match
            if len(row['zhuyin'].split('/')) != len(trad.split('/')):
                filtered_out.append(trad)
                continue
            # passed tests
            # but first filter out any meanings that have the pattern
            filtered_rows.append(row)
        else:
            # definition does not exist in cedict so filter it out.
            filtered_out.append(trad)
    return filtered_rows, filtered_out

def adjust_meanings(row,db, pattern):
    # adjust meanings to remove any meanings that are of the form ["see 下工夫[xia4 gong1 fu5]"]
    # sort the meanings in reverse order so english appears first
    meanings = db[row['word']].meanings
    row['meanings'] = sorted(filter(lambda m: not re.search(pattern, m), meanings), 
                             reverse=True)

def adjust_zhuyin_pinyin(row):
    # adjust zhuyin and pinyin to match the number of characters in the word
    # if there are multiple characters in the word, then the zhuyin and pinyin
    # will be split by a '/'
    row['zhuyin'] = row['zhuyin'].split('/')[0]
    row['pinyin'] = row['pinyin'].split('/')[0]

def main():
    # read cedict file
    parser = CedictParser()
    parser.read_file('cedict.txt')
    db,_ = build_db(parser.parse())
    pattern = r'see.*\[.*\]' 

    # gather rows to write
    with open('data.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        filtered_rows, discarded_rows = filter_rows(reader, db, pattern)
    print(f"Discarded {len(discarded_rows)} rows")
    print(f"Will proccess {len(filtered_rows)} rows")
    # adjust rows
    for row in filtered_rows[100:110]:
        adjust_meanings(row, db, pattern)
        adjust_zhuyin_pinyin(row)
        # print(row['meanings'])
        print(row['word'], row['zhuyin'], row['pinyin'], row['meanings'])
main()

def old_main():
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





