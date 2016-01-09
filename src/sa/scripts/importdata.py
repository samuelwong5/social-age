from socialage.models import Page
import csv
import sys
import codecs

"""
Script to populate the database with the given frequency data, and relate the facebook page to the
twitter page.
"""


def run():
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    fpath = 'E:/Users/jasper/Desktop/social_age/src/sa/socialage/fixtures/star_age_frequencies.csv'
    lpath = 'E:/Users/jasper/Desktop/social_age/src/sa/socialage/fixtures/fb_twitter_lookup.csv'
    freq = codecs.open(fpath, 'r', 'utf-8')
    freqReader = csv.DictReader(freq)
    count = 0
    for row in freqReader:
        if count >= 2000:
            break
        count += 1
        f = lambda x: float(x)
        ageUnder12 = f(row['under 12'])
        age12to13 = f(row['12-13'])
        age14to15 = f(row['14-15'])
        age16to17 = f(row['16-17'])
        age18to24 = f(row['18-24'])
        age25to34 = f(row['25-34'])
        age35to44 = f(row['35-44'])
        age45to54 = f(row['45-54'])
        age55to64 = f(row['55-64'])
        ageAbove65 = f(row['65+'])
        total = f(row['total'])
        tw_id = row['network_id']
        tw_handle = row['twitter_handle']
        print('Reading page ' + str(count) + ":" + tw_handle)
        page = Page.objects.create(tw_id=tw_id,
                                   tw_handle=tw_handle,
                                   ageUnder12=ageUnder12,
                                   age12to13=age12to13,
                                   age14to15=age14to15,
                                   age16to17=age16to17,
                                   age18to24=age18to24,
                                   age25to34=age25to34,
                                   age35to44=age35to44,
                                   age45to54=age45to54,
                                   age55to64=age55to64,
                                   ageAbove65=ageAbove65,
                                   total=total
                                   )
        page.save()

    lookup = codecs.open(lpath, 'r', 'utf-8')
    r = csv.DictReader(lookup)

    print('Looking for corresponding twitter entries in fb_twitter_lookup.csv...')
    for row in r:
        if row['network'] == 'twitter':
                print('(twitter) Looking at row with star_name:' + row['star_name'])
                pages = Page.objects.filter(tw_id=row['id'])
                pages.update(name=row['star_name'])

    print('Looking for corresponding facebook entries in fb_twitter_lookup.csv...')
    lookup = codecs.open(lpath, 'r', 'utf-8')
    r = csv.DictReader(lookup)

    for row in r:
        if row['network'] == 'facebook':
                print('(facebook) Looking at row with star_name:' + row['star_name'])
                pages = Page.objects.filter(name=row['star_name'])
                pages.update(fb_id=row['id'], fb_handle=row['handle'])







