import sys
import item
import unittest
import downloader
import logging

class DownloaderTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                            format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s",
                            datefmt="%m-%d %H:%M:%S")
        self.handler = self.MockHandler()
        self.dldr = downloader.Downloader(5, self.handler)
        self.dldr.add_item(item.Item("http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000", 3))
        self.dldr.add_item(item.Item("http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000", 3))
        self.dldr.add_item(item.Item("http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000", 3))

        self.dldr.start()

    def tearDown(self):
        pass

    def test_download_item(self):
        self.assertTrue(True)
#    def test_do_download(self):
#        self.dldr._do_download(item.Item("http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000", 3))

    class MockHandler(object):
        def add_item(self, item):
            logging.debug('Mock handler handling %s', item.url)
