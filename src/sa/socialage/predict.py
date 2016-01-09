import numpy as np
from .models import Page

# Precomputed prior distribution (P(agegroup))
PRIOR = np.array([0.008, 0.02, 0.029, 0.023, 0.14, 0.23, 0.22, 0.23, 0.06, 0.04])
# For debugging
TEST_IDS = ["813286", "15846407"]


def predict(test_ids, network, limit_search=True, debug=False):
    """
    Predict user's social age using Naive Bayes classifier
    Calculating P(page1,page2,...pagen|agegroup) * P(agegroup)
    which under assumption that liking different pages are independent(clearly false but necessary
    for efficiency) = P(page1|agegroup)*P(page2|ageggroup)*...*P(pagen|agegroup)*P(agegroup)
    and using the normalized value of this to determine his probability to belong to each respective
    age gorup.
    :param test_ids: ids of pages the user liked
    :param limit_search: if setted true, limit search to top 1000 entries, else search through all.
    :param network: string 'fb' or 'tw'(facebook or twitter)
    :return: predicted age.
    """
    if debug:
        test_ids = TEST_IDS
    # Retrieve all pages
    pages = Page.objects.order_by('total')
    if limit_search:
        # Search through top 1000 entries
        pages = pages[:1000]
    if network == 'fb':
        test_stars = pages.filter(fb_id__in=test_ids)
    else:
        test_stars = pages.filter(tw_id__in=test_ids)
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
    age = age_prob[0]*10 + age_prob[1]*12.5 + age_prob[2]*14.5 + age_prob[3]*16.5 + age_prob[4]*21 + age_prob[5]*29.5 + age_prob[6]*39.5 + age_prob[7]*49.5 + age_prob[8]*59.5 + age_prob[9]*70
    return age


def extract_prob(test_stars):
    """
    :param test_stars: pages to be tested
    :return: probabilities of different age groups given the pages P(page|agegroup) in a np.ndarray
    """

    freq = np.empty(shape=(test_stars.count(), 10), dtype=float)
    i = 0
    for s in test_stars:
        freq[i][0] = s.ageUnder12
        freq[i][1] = s.age12to13
        freq[i][2] = s.age14to15
        freq[i][3] = s.age16to17
        freq[i][4] = s.age18to24
        freq[i][5] = s.age25to34
        freq[i][6] = s.age35to44
        freq[i][7] = s.age45to54
        freq[i][8] = s.age55to64
        freq[i][9] = s.ageAbove65
        freq[i, :] = freq[i, :] / s.total
        i += 1
    return freq



