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


class ItemHandler(threading.Thread):
    def __init__(self, output_directory, target_url):
        threading.Thread.__init__(self)
        self._in_queue = Queue.Queue()
        self.output_directory = os.path.normpath(output_directory)
        self.target_url = target_url
        try:
            if not os.path.exists(self.output_directory):
                logging.warning('Output dir not existing')
                os.makedirs(self.output_directory)
                logging.info('Output dir created')
        except EnvironmentError as err:
            logging.error('Creating output dir: %s', err.message)

    @staticmethod
    def is_html(item):
        return item.headers['content-type'].find('text') >= 0

    @staticmethod
    def get_all_links(item):
        soup = bs4.BeautifulSoup(item.content)
        links = []
        for link in soup.findAll("a"):
            l = link.get("href")
            if l.startswith('javascript:location.href='):
                l = re.search('".*"$', l).group(0)[1:-1]
            l = urlparse.urljoin(item.final_url, l)
            links.append(l)
        return links

    def run(self):
        while True:
            item = self._in_queue.get()
            if self._is_target(item):
                self._save_to_file(item)

    def add_item(self, item):
        self._in_queue.put(item)

    def _save_to_file(self, item):
        pathname = os.path.join(self.output_directory,
                                urllib.quote(item.final_url, ''))
        try:
            with open(pathname, 'w') as f:
                f.write(item.content)
            logging.debug('Item %s saved', item.final_url)
        except EnvironmentError as err:
            logging.error('Failed to save %s: %s', item.final_url, err.message)

    def _is_target(self, item):
        return re.match(self.target_url, item.final_url)
