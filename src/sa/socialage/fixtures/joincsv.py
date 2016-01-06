#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import sys
from collections import OrderedDict

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
freq = codecs.open('star_age_frequencies_test.csv', 'r', 'utf-8')
lookUp = codecs.open('fb_twitter_lookup_test.csv', 'r', 'utf-8')
join = codecs.open('joindata.csv', 'w', 'utf-8')


freqReader = csv.reader(freq)
lookUpReader = csv.reader(lookUp)

freqDict = OrderedDict()
lookUpDict = OrderedDict()
i = 0
for row in freqReader:
    if i != 0:
        freqDict.update({row[0]: row[1:]})
    i += 1

i = 0
for row in lookUpReader:
    if i != 0:
        lookUpDict.update({row[2]: row[0:2] + row[3:]})
    i += 1

result = OrderedDict()

w = csv.DictWriter(join, 'w')
for key, value in result.items():
    w.writerow([key] + value)

