from django.test import TestCase
from . import models
# Create your tests here.


class PageTestCase(TestCase):

    def setUp(self):
        models.Page.objects.create(tw_id="123", tw_handle="test")

    def test_Page_default_value(self):
        p = models.Page.objects.get(tw_id="123")
        self.assertEqual(p.ageUnder12, 0)
