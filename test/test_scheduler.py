#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试调度器
"""
import logging
import sys
import item


import unittest
import scheduler


class SchedulerTestCase(unittest.TestCase):
    """
    测试调度器类
    """
    def setUp(self):
        """
        初始设置
        :return:
        """
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                            format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d *"
                                   " %(thread)d %(message)s",
                            datefmt="%m-%d %H:%M:%S")
        self.init_scheduler()

    def init_scheduler(self):
        """
        初始化
        :return:
        """
        self.downloader = self.MockDownloader()
        self.scheduler = scheduler.Scheduler(2, ['http://www.baidu.com'], self.downloader)
        self.downloader.scheduler = self.scheduler

    def test_finish(self):
        """
        测试_finish方法
        :return:
        """
        self.init_scheduler()
        test_url = 'http://www.baidu.com/'
        self.scheduler._in_progress.add(test_url)
        finishing_item = item.Item(test_url, 5)
        finishing_item.final_url = finishing_item.url
        self.scheduler._finish(finishing_item)
        self.assertEqual(len(self.scheduler._in_progress), 0)
        self.assertEqual(len(self.scheduler._finished), 1)
        self.assertIn(test_url, self.scheduler._finished)

        self.init_scheduler()
        redirected_url = 'http://xxx.baidu.com/'
        self.scheduler._in_progress.add(test_url)
        redirected_item = item.Item(test_url, 5)
        redirected_item.final_url = redirected_url
        self.scheduler._finish(redirected_item)
        self.assertEqual(len(self.scheduler._in_progress), 0)
        self.assertEqual(len(self.scheduler._finished), 2)
        self.assertIn(test_url, self.scheduler._finished)
        self.assertIn(redirected_url, self.scheduler._finished)

    def test_create_item(self):
        """
        测试_create_item方法
        :return:
        """
        self.init_scheduler()
        urls = ['http://www.baidu.com/', 'http://w1.baidu.com/',
                'http://w2.baidu.com/', 'http://w3.baidu.com/',
                'http://w4.baidu.com/', 'http://w5.baidu.com/']
        self.scheduler._in_progress.add(urls[1])
        redundant = 2
        self.scheduler._finished[urls[redundant]] = item.Item(urls[redundant], 3)
        for u in urls:
            self.scheduler._create_item(u, 5)

        urls.remove(urls[redundant])
        for u in urls:
            self.assertIn(u, self.scheduler._in_progress)
        self.assertEqual(len(self.scheduler._in_progress), len(urls))

    def test_handle_feedback(self):
        """
        测试_handle_feedback方法
        :return:
        """
        self.init_scheduler()

        item_handled_5 = item.Item('http://www.baidu.com/', 5)
        item_handled_5.is_handled = True
        item_handled_5.links = ['http://baike.baidu.com/']

        item_handled_0 = item.Item('http://w2.baidu.com/', 0)
        item_handled_0.is_handled = True
        item_handled_0.links = ['http://w2baike.baidu.com/']

        item_unhandled = item.Item('http://w4.baidu.com/', 0)
        item_unhandled.is_handled = False
        item_unhandled.links = ['http://w4baike.baidu.com/']

        items = [item_handled_5, item_handled_0, item_unhandled]
        for i in items:
            self.scheduler._in_queue.put(i)
            self.scheduler._handle_feedback()

    def test_scheduler(self):
        """
        测试Scheduler
        :return:
        """
        self.init_scheduler()
        final_url = 'http://new.baidu.com'
        links = ['http://w1.baidu.com', 'http://w2.baidu.com', 'http://w3.baidu.com']
        mock_downloader_and_handler = self.MockDownloaderAndHandler(final_url, links)
        mock_downloader_and_handler._scheduler = self.scheduler
        self.scheduler._downloader = mock_downloader_and_handler
        self.scheduler.start()

        self.assertIn('http://www.baidu.com', self.scheduler._finished)
        self.assertIn(final_url, self.scheduler._finished)
        for l in links:
            self.assertIn(l, self.scheduler._finished)
        self.assertEqual(2 + len(links), len(self.scheduler._finished))

    class MockDownloader(object):
        """
        模拟下载工具
        """
        def __init__(self):
            self.scheduler = None

        def add_item(self, item):
            """
            模拟添加下载项
            :param item: 下载项
            :return:
            """
            logging.debug('MockDownloader add %s', item.url)
            self.scheduler.feedback(item)

    class MockDownloaderAndHandler(object):
        """
        模拟下载工具和项目处理器环路
        """
        def __init__(self, final_url, links):
            self._scheduler = None
            self._final_url = final_url
            self._links = links

        def add_item(self, item):
            """
            模拟添加下载项，下载、处理项目以及反馈回Scheduler
            :param item: 项目
            :return:
            """
            logging.debug('MockDownloaderAndHandler add %s', item.url)
            item.is_handled = True
            item.final_url = self._final_url
            item.links = self._links
            self._scheduler.feedback(item)
