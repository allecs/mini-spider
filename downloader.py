#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import Queue
import threading
import requests
import sys
import time
import item


class Downloader(object):
    """
    下载器
    """

    def __init__(self, thread_count, item_handler=None):
        self._item_handler = item_handler
        self._in_queue = Queue.Queue()
        self._threads = []

        for i in xrange(thread_count):
            t = threading.Thread(target=self._download)
            t.daemon = True
            self._threads.append(t)

    def set_handler(self, hdlr):
        self._item_handler = hdlr

    def _download(self):
        logging.info('Downloader thread %s started', threading.current_thread().name)
        while True:
            try:
                item = self._in_queue.get()
                logging.debug('Downloader thread %s start downloading: %s', threading.current_thread().name, item.url)
                self._do_download(item)
            except requests.HTTPError as error:
                logging.error(error.message)
            finally:
                self._item_handler.add_item(item)


    def _do_download(self, item):
        logging.debug('Item %s start downloading', item.url)
        r = requests.get(item.url)
        item.final_url = r.url
        r.raise_for_status()
        logging.debug('Item %s downloaded', item.url)
        item.headers = r.headers
        item.encoding = r.apparent_encoding
        item.content = r.content
        item.is_requested = True

    def start(self):
        logging.info('Starting downloader, with %s threads', len(self._threads))
        for t in self._threads:
            t.start()

    def stop(self):
        pass

    def add_item(self, item):
        self._in_queue.put(item)
