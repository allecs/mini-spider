
import unittest
import mini_spider


class MiniSpiderTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_read_config(self):
        conf_dict = mini_spider.get_config('../spider.conf')
        print conf_dict
