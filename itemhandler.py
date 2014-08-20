#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
处理下载项工具，包含一个ItemHandler类
"""
import Queue
import logging
import os
import threading
import re
import bs4
import urlparse
import urllib
import sys


class ItemHandler(object):
    """
    处理下载项类，负责处理Downloader下载项目，包括解析连接，保存项目等，再反馈给Scheduler
    """

    def __init__(self, output_directory, target_url, scheduler=None, thread_count=5):
        self._in_queue = Queue.Queue()
        self._output_directory = os.path.normpath(output_directory)
        self._target_url = target_url
        self._scheduler = scheduler
        self._threads = []
        self._init_threads(thread_count)
        self._create_dir_lock = threading.Lock()
        self._create_output_dir()

    def need_parse(self, item):
        """
        判断item是否需要解析，即是否是html
        :param item: 需要判断的项目
        :return: 布尔值
        """
        return item.headers['content-type'].find('text/html') >= 0

    def get_all_links(self, item):
        """
        获取item中所有超链接
        :param item: 需要获取的item
        :return: 包含所有已解析链接的列表
        """
        soup = bs4.BeautifulSoup(item.content)
        links = []

        for a in soup.find_all('a'):
            try:
                href = a.get('href')
                if href:
                    if href.startswith('javascript:location.href='):
                        href = re.search('".*"$', href).group(0)[1:-1]
                    href = urlparse.urljoin(item.final_url, href)
                    links.append(href)
            except (AttributeError, IndexError) as err:
                logging.error(a)
                logging.error(err.message)
                continue

        for img in soup.find_all('img'):
            try:
                src = img.get('src')
                if src:
                    href = urlparse.urljoin(item.final_url, src)
                    links.append(href)
            except (AttributeError, IndexError) as err:
                logging.error(img)
                logging.error(err.message)
                continue

        for script in soup.find_all('script'):
            try:
                text = re.search('location.href=".*"', script.text)
                if text:
                    href = re.search('".*"', text.group(0)).group(0)[1:-1]
                    href = urlparse.urljoin(item.final_url, href)
                    links.append(href)
            except (AttributeError, IndexError) as err:
                logging.error(script)
                logging.error(err.message)
                continue

        for meta in soup.find_all('meta'):
            try:
                if meta.get('http-equiv') == 'refresh':
                    href = meta.get('content')
                    href = href.split('url=')[1]
                    href = urlparse.urljoin(item.final_url, href)
                    links.append(href)
            except (AttributeError, IndexError) as err:
                logging.error(meta)
                logging.error(err.message)
                continue

        return links

    def set_scheduler(self, scheduler):
        """
        设置Scheduler对象
        :param scheduler: Scheduler对象
        :return:
        """
        self._scheduler = scheduler

    def start(self):
        """
        启动处理器，需在scheduler设置之后才能调用该方法
        :return:
        """
        if not self._scheduler:
            logging.critical('Scheduler not found, terminating program')
            sys.exit(1)
        logging.info('Starting item handler, with %s threads', len(self._threads))
        for t in self._threads:
            t.start()

    def add_item(self, item):
        """
        添加处理项
        :param item: 需要处理的项目
        :return:
        """
        self._in_queue.put(item)

    def _init_threads(self, thread_count):
        if thread_count < 1:
            logging.critical('Item handler thread number must be more than zero, '
                             'terminating program')
            sys.exit(1)
        for i in xrange(thread_count):
            t = threading.Thread(target=self._handle)
            t.daemon = True
            self._threads.append(t)

    def _handle(self):
        while True:
            item = self._in_queue.get()
            logging.debug('Handler received item: %s', item.url)
            if item.is_requested:
                if self._is_target(item):
                    self._save_to_file(item)
                if self.need_parse(item):
                    item.links += self.get_all_links(item)
                item.is_handled = True
            self._scheduler.feedback(item)

    def _is_target(self, item):
        return re.match(self._target_url, item.final_url)

    def _get_save_path(self, url):
        return os.path.join(self._output_directory, urllib.quote(url, ''))

    def _save_to_file(self, item):
        pathname = self._get_save_path(item.final_url)
        try:
            if not os.path.exists(self._output_directory):
                self._create_output_dir()
            with open(pathname, 'wb') as f:
                f.write(item.content)
            logging.info('Item %s saved', item.final_url)
        except EnvironmentError as err:
            logging.error('Failed to save %s: %s', item.final_url, err.message)

    def _create_output_dir(self):
        with self._create_dir_lock:
            try:
                if not os.path.exists(self._output_directory):
                    logging.warning('Output dir not existing')
                    os.makedirs(self._output_directory)
                    logging.info('Output dir created')
            except EnvironmentError as err:
                logging.error('Creating output dir: %s', err.message)