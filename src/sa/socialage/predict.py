import numpy as np
from .models import Page
from django.db.models import Sum
from itertools import chain
# Precomputed prior distribution (P(agegroup))
PRIOR = np.array([0.008, 0.02, 0.029, 0.023, 0.14, 0.23, 0.22, 0.23, 0.06, 0.04])
# Middle value of each age group
AGE_GROUP = [10, 12.5, 14.5, 16.5, 21, 30, 40, 50, 60, 70]
# For debugging tw:obama, ellenshow fb:michael jackson, league of legends
TEST_IDS_TW = ["813286", "15846407"]
TEST_IDS_FB = ["19691681472", "21785951839"]
# Minimum number of test stars required
MIN_TESTSTARS = 1


def predict(test_ids_fb, test_ids_tw, debug=False):
    """
    Predict user's social age using Naive Bayes classifier
    Calculating P(page1,page2,...pagen|agegroup) * P(agegroup)
    which under assumption that liking different pages are independent(clearly false but necessary
    for efficiency) = P(page1|agegroup)*P(page2|ageggroup)*...*P(pagen|agegroup)*P(agegroup)
    and using the normalized value of this to determine his probability to belong to each respective
    age gorup.
    :param test_ids: ids of pages the user liked
    :return: predicted age.
    """
    if debug:
        test_ids_tw = TEST_IDS_TW
        test_ids_fb = TEST_IDS_FB
    prob, test_stars = extract_prob(test_ids_fb, test_ids_tw, missing_link=30)
    # if the amount of test_stars is less than MIN_TESTSTARS,
    # return -1 and tell user that the pages they provided are
    # insufficient to compute an accurate social age
    if len(test_stars) < MIN_TESTSTARS:
        return -1
    # Log the probabilities
    log_prob = np.log(prob)
    # Sum the log prob of all stars
    joint = np.sum(log_prob, 0)
    # Multiply with the prior i.e. add to the log prob
    joint += np.log(PRIOR)
    # Unnormalize before unlogging to prevent underflow
    joint -= max(joint)
    # Convert back to probability
    age_prob = np.exp(joint)
    # Normalize
    total = np.sum(age_prob)
    age_prob = age_prob / total
    return sum(map(lambda x, y: x * y, age_prob.tolist(), AGE_GROUP))


def extract_prob(test_ids_fb, test_ids_tw, missing_link=0, debug=False):
    """
    :param test_stars: pages to be tested, type: Django QuerySet
    :param missing_link: number of top stars to calculate the probability of not following
    :return: probabilities of following the page given different age groups P(page|agegroup) in a np.ndarray
    """
    if debug:
        test_ids_tw = TEST_IDS_TW
        test_ids_fb = TEST_IDS_FB
    # Retrieve test stars pages as test_stars
    pages = Page.objects.order_by('-total')
    test_stars_fb = pages.filter(fb_id__in=test_ids_fb, total__gte=20)
    test_stars_tw = pages.filter(tw_id__in=test_ids_tw, total__gte=20)
    test_stars = test_stars_fb | test_stars_tw
    # Retrieve top stars that are not followed
    inner_q = Page.objects.order_by('-total').values('id')[:missing_link]
    top_not_followed = Page.objects.filter(id__in=inner_q).exclude(fb_id__in=test_ids_fb).exclude(tw_id__in=test_ids_tw)
    prob = np.zeros(shape=(len(test_stars) + len(top_not_followed), 10), dtype=float)
    all_test_pages = list(chain(test_stars, top_not_followed))
    i = 0
    # Calculate the total number of number sample follows made by each age groups,
    #  save them in a list.
    f = lambda x: list(Page.objects.aggregate(Sum(x)).values())[0]
    totals = [f('ageUnder12'), f('age12to13'), f('age14to15'), f('age16to17'), f('age18to24'),
              f('age25to34'), f('age35to44'), f('age45to54'), f('age55to64'), f('ageAbove65')]

    # (f + 1) / (F + 10)
    for s in all_test_pages:
        prob[i][0] += s.ageUnder12
        prob[i][1] += s.age12to13
        prob[i][2] += s.age14to15
        prob[i][3] += s.age16to17
        prob[i][4] += s.age18to24
        prob[i][5] += s.age25to34
        prob[i][6] += s.age35to44
        prob[i][7] += s.age45to54
        prob[i][8] += s.age55to64
        prob[i][9] += s.ageAbove65
        i += 1
    prob += 1
    for k in range(10):
        prob[:, k] /= (totals[k] + 10)
        # prob of not following = 1 - prob of following
        prob[len(test_stars):len(all_test_pages), k] = 1 - prob[len(test_stars):len(all_test_pages), k]

    return prob, test_stars


def page_avg_age(page):
    # Calculate the page average age based on single star posterior.
    prob = extract_prob([page])[0]
    prob /= sum(prob)
    return round(sum(map(lambda x, y: x * y, prob.tolist(), AGE_GROUP)))


def recommend(user_age, exclude_twids=[], exclude_fbids=[], bound=3, page_needed=10):
    # Recommend 5 pages based on user's actual age or social age excluding the ones they have already liked.
    # Return the 5 random pages with decent popularity and same/similar page_avg_age as user_age.
    # Criteria: (page's average age - user_age) <= |bound| && both tw_id and fb_id exist.
    # Possible improvement: random based on the distribution on total instead of uniform distribution.
    pages = Page.objects.order_by('-total').filter(avg_age__lte=(user_age + bound)).filter(
        avg_age__gte=(user_age - bound))
    pages = pages.exclude(tw_id="").exclude(fb_id="").filter(total__gte=200)
    pages = pages.exclude(tw_id__in=exclude_twids).exclude(fb_id__in=exclude_fbids)
    return pages.order_by('?')[:page_needed]
