import csv
import json
import sys
import codecs
from collections import OrderedDict

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
freq = codecs.open('star_age_frequencies.csv', 'r', 'utf-8')
jsonFile = open('star_age_frequencies.json', 'w')


freqReader = csv.DictReader(freq)
pk = 0
jsonFile.write('[\n')

for row in freqReader:
    entry = OrderedDict()
    fields = OrderedDict()

    f = lambda x: float(x)
    fields['ageUnder12'] = f(row['under 12'])
    fields['age12to13'] = f(row['12-13'])
    fields['age14to15'] = f(row['14-15'])
    fields['age16to17'] = f(row['16-17'])
    fields['age18to24'] = f(row['18-24'])
    fields['age25to34'] = f(row['25-34'])
    fields['age35to44'] = f(row['35-44'])
    fields['age45to54'] = f(row['45-54'])
    fields['age55to64'] = f(row['55-64'])
    fields['ageAbove65'] = f(row['65+'])
    fields['tw_handle'] = row['twitter_handle']
    fields['name'] = row['twitter_handle']
    fields['fb_id'] = '0'
    fields['tw_id'] = row['network_id']
    fields['fb_handle'] = '0'
    fields['total'] = f(row['total'])
    entry['model'] = 'socialage.page'
    entry['pk'] = hash(row['twitter_handle'])

    lookUp = codecs.open('fb_twitter_lookup.csv', 'r', 'utf-8')
    lookUpReader = csv.DictReader(lookUp)
    lookForFb = False
    for d in lookUpReader:
        if (d['network'] == 'twitter') & (fields['tw_id'] == d['id']):
            fields['name'] = d['name']
            entry['pk'] = d['star_id']
            lookForFb = True
            print('look up found. Tw_handle:' + row['twitter_handle'] + ' star name:' + d['name'])
            break

    if lookForFb:
        lookUp = codecs.open('fb_twitter_lookup.csv', 'r', 'utf-8')
        lookUpReader = csv.DictReader(lookUp)
        for d in lookUpReader:
            if (d['network'] == 'facebook') & (d['star_id'] == entry['pk']):
                fields['fb_id'] = d['id']
                fields['fb_handle'] = d['handle']
                break

    entry['fields'] = fields

    json.dump(entry, jsonFile)
    jsonFile.write(',\n')

jsonFile.seek(0, 2)
size = jsonFile.tell()
jsonFile.truncate(size-3)
jsonFile.seek(0, 2)
jsonFile.write('\n]')


