#-*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import Client

from arara import model
from arara import arara_engine
from warara import warara_middleware


class WararaTestBase(TestCase):

    def setUp(self):
        super(WararaTestBase, self).setUp()

        # TEST 용 Backend 생성
        model.init_test_database()
        self.arara_engine = arara_engine.ARAraEngine()
        warara_middleware.set_server(self.arara_engine)
        self.client = Client()

    def test_main(self):
        response = self.client.get('/main/')
        self.assertEquals(response.status_code, 200)
