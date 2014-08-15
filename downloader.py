#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
下载工具，包含一个下载类Downloader
"""
import logging
import Queue
import threading
import requests
import sys


class Downloader(object):
    """
    下载类，负责接收从Scheduler发来的下载请求，下载网页，并发送给ItemHandler
    """

    def __init__(self, thread_count, crawl_interval, crawl_timeout, item_handler=None):
        self._item_handler = item_handler
        self._crawl_interval = crawl_interval
        self._wait_semaphore = threading.Semaphore()
        self._crawl_timeout = crawl_timeout
        self._in_queue = Queue.Queue()
        self._threads = []
        self._init_threads(thread_count)

    def set_handler(self, handler):
        """
        设置ItemHandler对象
        :param handler: ItemHandler对象
        :return:
        """
        self._item_handler = handler

    def add_item(self, item):
        """
        添加下载项目，进入下载队列
        :param item: 需要下载的项目
        :return:
        """
        self._in_queue.put(item)

    def start(self):
        """
        启动下载器，需在设置handler之后才能调用该方法
        :return:
        """
        if not self._item_handler:
            logging.critical('ItemHandler not found, exiting')
            sys.exit(1)
        logging.info('Starting downloader, with %s threads', len(self._threads))
        for t in self._threads:
            t.start()

    def _init_threads(self, thread_count):
        for i in xrange(thread_count):
            t = threading.Thread(target=self._download)
            t.daemon = True
            self._threads.append(t)

    def _download(self):
        logging.info('Downloader thread %s started', threading.current_thread().name)
        while True:
            try:
                item = self._in_queue.get()
                logging.debug('Downloader thread %s start downloading: %s',
                              threading.current_thread().name, item.url)
                self._do_download(item)
            except requests.RequestException as error:
                logging.error(str(error.message) + ': ' + item.url)
            finally:
                self._item_handler.add_item(item)

    def _do_download(self, item):
        logging.debug('Item %s start downloading', item.url)
        self._wait_in_line()
        r = requests.get(item.url, timeout=self._crawl_timeout)
        item.final_url = r.url
        r.raise_for_status()
        logging.debug('Item %s downloaded', item.final_url)
        item.headers = r.headers
        item.encoding = r.apparent_encoding
        item.content = r.content
        item.is_requested = True

    def _wait_in_line(self):
        logging.debug('Start waiting in line')
        self._wait_semaphore.acquire()
        t = threading.Timer(self._crawl_interval, self._wait_semaphore.release)
        t.daemon = True
        t.start()
        logging.debug('Here we go')
