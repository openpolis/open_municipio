# -*- coding: utf-8 -*-

from django.utils import unittest
from open_municipio.acts.models import Act
from open_municipio.people.models import Institution
from django.test.client import Client
from os import sys


class ActTestCase(unittest.TestCase):
    def setUp(self):
        self.i = Institution.objects.get(slug='consiglio-comunale')
        self.a = Act.objects.create(idnum="2012/MX/00001", title="testActs", emitting_institution=self.i)

    def test_unicode(self):
        """Unicode strings are produced correctly"""
        self.a2 = Act.objects.create(
            idnum="2012/MX/00002", title="testActs", emitting_institution=self.i,
            adj_title=u'An adjoint title here'
        )

        self.assertEqual(self.a.__unicode__(), u'2012/MX/00001 - testActs')
        self.assertEqual(self.a2.__unicode__(), u'2012/MX/00002 - testActs (An adjoint title here)')

    def test_act_page(self):
        """Act pages are correctly retrieved, redirected or missed by web browsers"""
        client = Client()

        # an existing act, requested with a trailing slash
        # is correctly retrieved
        response = client.get('/acts/%s/' % self.a.id)
        self.assertEqual(response.status_code, 200)

        # an existing act, requested with no trailing slash
        # is redirected to the right URL
        response = client.get('/acts/%s' % self.a.id, follow=True)
        self.assertListEqual(response.redirect_chain, [('http://testserver/acts/5/', 301)])

        # a non existing act returns a 404 code
        response = client.get('/acts/99999/')
        self.assertEqual(response.status_code, 404)

