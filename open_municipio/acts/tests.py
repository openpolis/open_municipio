from django.utils import unittest
from open_municipio.acts.models import Act

class ActTestCase(unittest.TestCase):
    def setUp(self):
        self.a = Act.objects.create(idnum="2012/MX/00001", title="testActs")

    def test_unicode(self):
        """Unicode string is produced correctly"""
        self.assertEqual(self.a.__unicode__(), u'2012/MX/00001 - testActs')
