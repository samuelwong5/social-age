import numpy as np
from .models import Page

# Precomputed prior distribution (P(agegroup))
PRIOR = np.array([0.008, 0.02, 0.029, 0.023, 0.14, 0.23, 0.22, 0.23, 0.06, 0.04])
# For debugging
TEST_IDS = ["813286", "15846407"]
MIN_TESTSTARS = 2


def predict(test_ids, network, debug=False):
    """
    Predict user's social age using Naive Bayes classifier
    Calculating P(page1,page2,...pagen|agegroup) * P(agegroup)
    which under assumption that liking different pages are independent(clearly false but necessary
    for efficiency) = P(page1|agegroup)*P(page2|ageggroup)*...*P(pagen|agegroup)*P(agegroup)
    and using the normalized value of this to determine his probability to belong to each respective
    age gorup.
    :param test_ids: ids of pages the user liked
    :param network: string 'fb' or 'tw'(facebook or twitter)
    :return: predicted age.
    """
    if debug:
        test_ids = TEST_IDS
    # Retrieve all pages
    pages = Page.objects.order_by('-total')
    if network == 'fb':
        test_stars = pages.filter(fb_id__in=test_ids)
    else:
        test_stars = pages.filter(tw_id__in=test_ids)

    # if the amount of test_stars is less than MIN_TESTSTARS,
    # return -1 and tell user that the pages they provided are
    # insufficient to compute an accurate social age
    if len(test_stars) < MIN_TESTSTARS:
        return -1

    prob = extract_prob(test_stars)
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
    age_groups = [10, 12.5, 14.5, 16.5, 21, 30, 40, 50, 60, 0]
    return sum(map(lambda x,y:x*y,age_prob.tolist(), age_groups))



def extract_prob(test_stars):
    """
    :param test_stars: pages to be tested
    :return: probabilities of different age groups given the pages P(page|agegroup) in a np.ndarray
    """


    prob = np.zeros(shape=(1, 10), dtype=float)
    i = 0
    total = 0
    for s in test_stars:
        prob[i][0] += s.ageUnder12
        prob[i][1] += s.age12to13
        prob[i][2] += s.age14to15
        prob[i][3] += s.age16to17
        prob[i][4] += s.age18to24
        prob[i][5] += s.age25to34
        prob[i][6] += s.age35to44
        prob[i][7] += s.age45to54
        prob[i][8] += s.age55to64
        #prob[i][9] += 0
        # m-estimates, equivalent sample size m = 10, adding m virtual samples
        # according to PRIOR
        total += s.total - s.ageAbove65

    for k in range(10):
        prob[0][k] /= total
    return prob



