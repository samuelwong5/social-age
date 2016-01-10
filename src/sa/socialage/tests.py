from django.test import TestCase
from . import models
from . import predict
# Create your tests here.


class SaTestCase(TestCase):

    def setUp(self):
        models.Page.objects.create(tw_id="1", tw_handle="test")
        models.Page.objects.create(tw_id="2", tw_handle="test2")
        models.Page.objects.create(tw_id="3", tw_handle="test3", ageUnder12=20, age12to13=30,
                                   age14to15=20, age16to17=30, age18to24=50, age25to34=40,
                                   age35to44=30, age45to54=20, age55to64=10, ageAbove65=10, total=260)
        models.Page.objects.create(tw_id="4", tw_handle="test4", ageUnder12=20, age12to13=30,
                                   age14to15=20, age16to17=30, age18to24=50, age25to34=40,
                                   age35to44=30, age45to54=20, age55to64=10, ageAbove65=10, total=260,
                                   fb_id="4", fb_handle="fbtest4")
        models.Page.objects.create(ageUnder12=20, age12to13=30,
                                   age14to15=20, age16to17=30, age18to24=50, age25to34=40,
                                   age35to44=30, age45to54=20, age55to64=10, ageAbove65=10, total=260,
                                   fb_id="5", fb_handle="fbtest5")

    def test_Page_default_value(self):
        p = models.Page.objects.get(tw_id="1")
        self.assertEqual(p.ageUnder12, 0)

    def test_Page_average_age(self):
        p = models.Page.objects.get(tw_id="4")
        self.assertEqual(p.avg_age(), 25.6)

    def test_predicted_Age_one_entry_return_minusone(self):
        age = predict.predict(["3"], 'tw')
        self.assertEqual(age, -1)

    def test_predicted_Age_multiple_entries(self):
        age = predict.predict(["1", "2", "3", "4"], 'tw')
        self.assertIsInstance(age, float)

    def test_predicted_age_multiple_entries_insufficient_teststars(self):
        age = predict.predict(["1", "2", "3", "5"], 'fb')
        self.assertEqual(age, -1)

    def test_predicted_age_multiple_fb(self):
        age = predict.predict(["1", "2", "4", "5"], 'fb')
        self.assertIsInstance(age, float)

    def test_extract_prob_no_zero_prob(self):
        p = models.Page.objects.get(tw_id="1")
        probs = predict.extract_prob([p])
        for prob in probs:
            self.assertNotEqual(prob.all(), 0)












