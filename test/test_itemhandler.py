#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试下载项处理器
"""
import copy
import logging
import unittest
import sys
import item
import itemhandler


class ItemHandlerTestCase(unittest.TestCase):
    """
    下载项处理器测试类
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
        self.scheduler = self.MockScheduler()
        self.item_handler = itemhandler.ItemHandler('./output', '.*',
                                                    self.scheduler, 5)

        self.test_item = item.Item('http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/', 4)
        self.test_item.is_requested = True
        self.test_item.headers = {'content-type': 'text/html'}
        self.test_item.final_url = 'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/'
        self.test_item.content = '''
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <meta charset=utf8>
                            <title>Crawl Me</title>
                        </head>
                        <body>
                            <ul>
                                <li><a href=page1.html>page 1</a></li>
                                <li><a href="page2.html">page 2</a></li>
                                <li><a href='page3.html'>page 3</a></li>
                                <li><a href='mirror/index.html'>
                                http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/mirror/index.html
                                </a></li>
                                <li><a href='javascript:location.href="page4.html"'>page 4</a></li>
                                <script>location.href="page1_1.html";</script>
                                <meta http-equiv="refresh" content="0;url=page1_2.html">
                            </ul>
                        </body>
                    </html>
                    '''

    def test_need_parse(self):
        """
        测试need_parse方法
        :return:
        """
        i = item.Item('www.baidu.com', 3)
        i.headers = {'content-type': 'text/html'}
        self.assertTrue(self.item_handler.need_parse(i))
        i.headers = {'content-type': 'text/plain'}
        self.assertFalse(self.item_handler.need_parse(i))
        i.headers = {'content-type': 'application/pdf'}
        self.assertFalse(self.item_handler.need_parse(i))
        i.headers = {'content-type': 'video/mp4'}
        self.assertFalse(self.item_handler.need_parse(i))

    def test_get_all_links(self):
        """
        测试get_all_links方法
        :return:
        """
        i = copy.deepcopy(self.test_item)
        l = self.item_handler.get_all_links(i)
        expected = [
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page1.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page2.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page3.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/mirror/index.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page4.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page1_1.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page1_2.html', ]
        self.assertListEqual(sorted(expected), sorted(l))

    def test_is_target(self):
        """
        测试is_target方法
        :return:
        """
        item_handler = itemhandler.ItemHandler('./output', '.*\.(gif|png|jpg|bmp)$',
                                               self.scheduler, 5)

        i = item.Item('www.baidu.com/1.bmp', 3)
        i.final_url = 'www.baidu.com/1.bmp'
        self.assertTrue(item_handler._is_target(i))
        i.final_url = 'www.baidu.xx.123.jpg'
        self.assertTrue(item_handler._is_target(i))
        i.final_url = 'www.baidu.com/1.htm'
        self.assertFalse(item_handler._is_target(i))
        i.final_url = 'www.baidu.com/1.jpg.htm'
        self.assertFalse(item_handler._is_target(i))

    def test_save_to_file(self):
        """
        测试save_to_file方法
        :return:
        """
        i = copy.deepcopy(self.test_item)
        self.item_handler._save_to_file(i)
        self.assertIsNotNone(open(self.item_handler._get_save_path(self.test_item.final_url), 'rb'))

    def test_start(self):
        """
        测试启动下载项处理器
        :return:
        """
        self.item_handler.start()

        i1 = copy.deepcopy(self.test_item)
        i2 = copy.deepcopy(self.test_item)
        i2.final_url = 'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page1_2.html'
        i3 = copy.deepcopy(self.test_item)
        i3.final_url = 'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page1_3.html'
        i3.is_requested = False

        item_list = [i1, i2, i3]
        for i in item_list:
            self.item_handler.add_item(i)

        while self.scheduler.count != len(item_list):
            pass

        self.assertIsNotNone(open(self.item_handler._get_save_path(i1.final_url), 'rb'))
        self.assertIsNotNone(open(self.item_handler._get_save_path(i2.final_url), 'rb'))

    class MockScheduler(object):
        """
        模拟调度器类
        """
        def __init__(self):
            self.count = 0

        def feedback(self, item):
            """
            模拟反馈调度器
            :param item: 反馈item
            :return:
            """
            logging.info('MockScheduler received feedback: %s', item.url)
            self.count += 1
