from socialage.models import Page
from socialage.predict import page_avg_age
"""
compute all pages average age.
"""


def run():
    pages = Page.objects.all()
    count = 0
    for p in pages:

        print("Updating page" + str(count))
        count += 1
        p.avg_age = page_avg_age(p)
        p.save()
