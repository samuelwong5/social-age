from django.test import TestCase
from . import models
from . import predict
# Create your tests here.


class SaTestCase(TestCase):

    def setUp(self):
        models.Page.objects.create(tw_id="123", tw_handle="test")
        models.Page.objects.create(tw_id="1234", tw_handle="test2")

    def test_Page_default_value(self):
        p = models.Page.objects.get(tw_id="123")
        self.assertEqual(p.ageUnder12, 0)

    def test_predicted_Age_for_zero_total_no_error(self):
        age = predict.predict(["123", "1234"], 'tw')
        self.assertIsInstance(age, float)

    def test_predicted_Age_one_entry_return_minusone(self):
        age = predict.predict(["123", "12345"], 'tw')
        self.assertEqual(age, -1)

    def test_predicted_Age_multiple_entries(self):
        age = predict.predict(["123", "1234", "12345", "432"], 'tw')
        self.assertIsInstance(age, float)

    def test_predicted_age_multiple_entries_insufficient_teststars(self):
        age = predict.predict(["1223", "12534", "12345", "432"], 'tw')
        self.assertEqual(age, -1)








