import Queue
import sys
import threading
import time
import requests
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
        self.schduler = self.MockScheduler()
        self.dldr = downloader.Downloader(10, 10.0, self.handler, self.schduler)

    def tearDown(self):
        pass

    def test_start(self):
        self.dldr.start()
        urls = ['http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000',
                'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page1.html',
                'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/1/page1_1.html']

        for i in urls:
            self.dldr.add_item(item.Item(i, 3))
            time.sleep(1)

        while self.handler._in_queue.qsize() != len(urls):
            pass

    # def test_do_download(self):
    #     i = item.Item("http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000", 3)
    #     self.dldr._do_download(i)
    #     self.assertTrue(i.is_requested)
    #
    #     i = item.Item("http://www.sina.com", 3)
    #     self.dldr._do_download(i)
    #     self.assertTrue(i.is_requested)
    #
    #     i = item.Item("http://cq02-spi-ssd2p-bak10.cq02.baidu.com:13246", 3)
    #     self.assertRaises(requests.RequestException, self.dldr._do_download, i)

    class MockHandler(object):
        def __init__(self):
            self.count = 0
            self._in_queue = Queue.Queue()

        def add_item(self, item):
            logging.debug('Mock handler added %s', item.url)
            self._in_queue.put(item)

    class MockScheduler(object):
        def __init__(self):
            self.finished = False
