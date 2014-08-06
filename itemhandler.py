#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Queue
import logging
import os
import threading
import re
import bs4
import urlparse
import urllib
import sys


class ItemHandler():
    """
    处理已下载项目，包括解析连接，保存项目等
    """
    def __init__(self, output_directory, target_url, scheduler=None, thread_count=1):
        self._in_queue = Queue.Queue()
        self._output_directory = os.path.normpath(output_directory)
        self._target_url = target_url
        self._scheduler = scheduler
        self._threads = []
        self._init_threads(thread_count)
        try:
            if not os.path.exists(self._output_directory):
                logging.warning('Output dir not existing')
                os.makedirs(self._output_directory)
                logging.info('Output dir created')
        except EnvironmentError as err:
            logging.error('Creating output dir: %s', err.message)

    @staticmethod
    def need_parse(item):
        return item.headers['content-type'].find('text/html') >= 0

    @staticmethod
    def get_all_links(item):
        soup = bs4.BeautifulSoup(item.content)
        links = []

        for a in soup.find_all('a'):
            href = a.get('href')
            if href.startswith('javascript:location.href='):
                href = re.search('".*"$', href).group(0)[1:-1]
            href = urlparse.urljoin(item.final_url, href)
            links.append(href)

        for script in soup.find_all('script'):
            text = re.search('location.href=".*"', script.text)
            if text:
                href = re.search('".*"', text.group(0)).group(0)[1:-1]
                href = urlparse.urljoin(item.final_url, href)
                links.append(href)

        for meta in soup.find_all('meta'):
            if meta.get('http-equiv') == 'refresh':
                href = meta.get('content')
                href = href.split('url=')[1]
                href = urlparse.urljoin(item.final_url, href)
                links.append(href)

        return links

    def set_scheduler(self, scheduler):
        self._scheduler = scheduler

    def start(self):
        if not self._scheduler:
            logging.critical('Scheduler not found, terminating program')
            sys.exit(1)
        logging.info('Starting item handler, with %s threads', len(self._threads))
        for t in self._threads:
            t.start()

    def add_item(self, item):
        self._in_queue.put(item)

    def _init_threads(self, thread_count):
        if thread_count < 1:
            logging.critical('Item handler thread number must be more than 1, terminating program')
            sys.exit(1)
        for i in xrange(thread_count):
            t = threading.Thread(target=self._handle)
            t.daemon = True
            self._threads.append(t)

    def _handle(self):
        while True:
            item = self._in_queue.get()
            if self._is_target(item):
                self._save_to_file(item)
            if self.need_parse(item):
                for l in self.get_all_links(item):
                    self._scheduler.add_url(l)
            self._scheduler.feedback(item)

    def _save_to_file(self, item):
        pathname = os.path.join(self._output_directory,
                                urllib.quote(item.final_url, ''))
        try:
            with open(pathname, 'w') as f:
                f.write(item.content)
            logging.debug('Item %s saved', item.final_url)
        except EnvironmentError as err:
            logging.error('Failed to save %s: %s', item.final_url, err.message)

    def _is_target(self, item):
        return re.match(self._target_url, item.final_url)
