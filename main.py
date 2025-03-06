import csv
import json
import re
from cedict_utils.cedict import CedictParser

def build_db(entries):
    """
    Return a dictionary of entries with the traditional character as the key
    as well as a list of duplicates.
    :param entries: list of entries from cedict
    Duplicate meaning will be appended to the existing word.
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
    """
    Filter out rows that are not in the cedict dictionary.
    Also filter out rows that have a different number of zhuyin and trad characters.
    Also filter out rows that have a meaning of the form ["see 下工夫[xia4 gong1 fu5]"].
    Side effect: modifies the row dictionary to include meanings with the pattern removed.
    """
    filtered_rows = []
    filtered_out = []
    for row in reader:
        trad = row['word']
        tradParts = trad.split('/')
        traditional = tradParts[0]
        if traditional in db:
            entry = db[traditional]
            # If there is only 1 definition and it is of the form ["see 下工夫[xia4 gong1 fu5]"] then filter entire character
            if len(entry.meanings) == 1 and re.search(pattern, entry.meanings[0]):
                filtered_out.append(trad)
                continue
            row['word'] = traditional
            row['meanings'] = entry.meanings
            if len(tradParts) > 1:
                # Some words have multiple ways to write them.
                # Append the additional ways to write the word to the meanings and ignore the additional zhuyin and pinyin
                row['meanings'] += tradParts[1:]
                row['zhuyin'] = row['zhuyin'].split('/')[0]
                row['pinyin'] = row['pinyin'].split('/')[0]
            clean_and_sort_meanings(row, pattern)
            filtered_rows.append(row)
        else:
            # Definition does not exist in cedict so filter it out.
            filtered_out.append(trad)
    return filtered_rows, filtered_out

def clean_and_sort_meanings(row, pattern):
    """
    Adjust meanings to remove any meanings that are of the form ["see 下工夫[xia4 gong1 fu5]"].
    Sort the meanings with the least number of characters appearing first.
    """
    meanings = row['meanings']
    row['meanings'] = sorted(filter(lambda m: not re.search(pattern, m), meanings),
                             key=lambda m: (len(m), m),
                             reverse=False)

def main():
    """
    Main function to process Chinese word data from a CEDICT file and a CSV file, 
    filter and sort the data, and write the results to a JSON file.
    Steps:
    1. Read and parse the CEDICT file.
    2. Build a database from the parsed data.
    3. Read rows from a CSV file and filter them based on a specified pattern.
    4. Sort the filtered rows based on spoken frequency, level number, frequency, and written frequency.
    5. Reassign indexes to the sorted rows and remove unneeded keys.
    6. Write the final processed rows to a JSON file.
    Input:
    - 'cedict.txt': A file containing Chinese-English dictionary data. (used by cedict_utils)
    - 'data.csv': A CSV file containing rows of data from a Taiwan Ministry of Education dataset.
    Output:
    - 'output.json': A JSON file containing the processed and sorted rows.
    Returns:
    None
    """
    # Read cedict file
    parser = CedictParser()
    parser.read_file('cedict.txt')
    db, _ = build_db(parser.parse())
    pattern = r'see.*\[.*\]'  # Pattern to filter out meanings that are of the form ["see 下工夫[xia4 gong1 fu5]"]
    
    # Gather rows
    with open('data.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        filtered_rows, discarded_rows = filter_rows(reader, db, pattern)
    print(f"Discarded {len(discarded_rows)} rows")
    print(f"Will process {len(filtered_rows)} rows")
    
    # Final adjustments to the rows    
    # Reassign indexes based on spoken frequency, if tie then frequency, if tie then written frequency
    filtered_rows = sorted(filtered_rows, key=lambda d: (int(d['spokenFrequencyPerMillion']),
                                                         float(d['levelNumber']), 
                                                         int(d['frequencyPerMillion']), 
                                                         int(d['writtenFrequencyPerMillion'])),
                           reverse=True)
    
    # Add sequential index based on sorted order specified above
    # Drop unneeded keys from row (writtenFrequencyPerMillion, spokenFrequencyPerMillion, frequencyPerMillion, levelNumber)
    for index, row in enumerate(filtered_rows, start=1):
        row['index'] = index
        del row['writtenFrequencyPerMillion']
        del row['spokenFrequencyPerMillion']
        del row['frequencyPerMillion']
        del row['levelNumber']
        del row['\ufeffindex']
    
    # Write to json
    with open('output.json', 'w', newline='', encoding='utf-8') as write_file:
        json.dump(filtered_rows, write_file, ensure_ascii=False, indent=4)
        print(f"Finished writing {len(filtered_rows)} rows to output.json")

main()