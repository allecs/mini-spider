#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试下载工具
"""
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
    """
    测试下载工具
    """
    def setUp(self):
        """
        初始化
        :return:
        """
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                            format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * "
                                   "%(thread)d %(message)s",
                            datefmt="%m-%d %H:%M:%S")
        self.handler = self.MockHandler()
        self.dldr = downloader.Downloader(thread_count=2, crawl_interval=2, crawl_timeout=10.0,
                                          item_handler=self.handler)

    def test_start(self):
        """
        测试运行下载工具
        把三个Item传给Downloader，
        :return:
        """
        self.dldr.start()
        urls = ['http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000',
                'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page1.html',
                'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/1/page1_1.html']
        # urls = ['http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000']
        for i in urls:
            self.dldr.add_item(item.Item(i, 3))
            time.sleep(1)

        while self.handler._in_queue.qsize() != len(urls):
            pass

        logging.debug('All items downloaded')
        self.assertEqual(self.handler._in_queue.qsize(), len(urls))

        while self.handler._in_queue.qsize():
            logging.debug('Try to get another item from handler')
            self.assertIn(self.handler._in_queue.get(block=False).url, urls)

    def test_do_download(self):
        """
        测试执行下载动作，直接调用_do_downloader
        :return:
        """
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
        """
        测试排队等待
        """
        for i in xrange(10):
            threading.Thread(target=self.dldr._wait_in_line).start()

    class MockHandler(object):
        """
        模拟处理下载项类
        """
        def __init__(self):
            self._in_queue = Queue.Queue()

        def add_item(self, item):
            """
            模拟添加下载项
            :param item:
            :return:
            """
            logging.debug('Mock handler added %s', item.url)
            self._in_queue.put(item)
