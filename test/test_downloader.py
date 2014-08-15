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
                            format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * "
                                   "%(thread)d %(message)s",
                            datefmt="%m-%d %H:%M:%S")
        self.handler = self.MockHandler()
        self.dldr = downloader.Downloader(thread_count=2, crawl_interval=2, crawl_timeout=10.0,
                                          item_handler=self.handler)

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

    def test_do_download(self):
        i = item.Item("http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000", 3)
        self.dldr._do_download(i)
        self.assertTrue(i.is_requested)

        i = item.Item("http://www.sina.com", 3)
        self.dldr._do_download(i)
        self.assertTrue(i.is_requested)

        i = item.Item("http://cq02-spi-ssd2p-bak10.cq02.baidu.com:13246", 3)
        self.assertRaises(requests.RequestException, self.dldr._do_download, i)

        i = item.Item("http://cq02-spi-ssd2p-bak10.cq02.baidu-this-is-a-fake-one-xxx.com", 3)
        self.assertRaises(requests.RequestException, self.dldr._do_download, i)

    def test_wait_in_line(self):
        for i in xrange(10):
            threading.Thread(target=self.dldr._wait_in_line).start()

    class MockHandler(object):
        def __init__(self):
            self._in_queue = Queue.Queue()

        def add_item(self, item):
            logging.debug('Mock handler added %s', item.url)
            self._in_queue.put(item)
