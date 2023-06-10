from cedict.cedict import DictionaryData, search
dict_db = DictionaryData()
print(search("apple", dict_db)) # ('apple', 'n.苹果,似苹果的果实')
print(search('large', dict_db))