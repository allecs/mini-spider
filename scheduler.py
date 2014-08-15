#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
任务调度器
"""
import Queue
import item


class Scheduler(object):
    """
    任务调度器
    负责维护任务队列（已下载和正在下载的），分派下载任务
    """

    def __init__(self, max_depth, seed, dldr=None):
        self._max_depth = max_depth
        self._seed = seed
        self._downloader = dldr
        self._in_queue = Queue.Queue()
        self._in_progress = set()
        self._finished = {}

    def set_downloader(self, dldr):
        """
        设置下载工具
        :param dldr: 下载工具对象
        :return:
        """
        self._downloader = dldr

    def start(self):
        """
        启动调度器，必须在Downloader和ItemHandler均启动之后调用
        :return:
        """
        for seed in self._seed:
            self._create_item(seed, self._max_depth)
        while True:
            if self._all_task_done():
                return
            self._handle_feedback()

    def feedback(self, item):
        """
        将item对象反馈回Scheduler
        :param item: item对象
        :return:
        """
        self._in_queue.put(item)

    def _all_task_done(self):
        return len(self._in_progress) == 0

    def _finish(self, item):
        self._in_progress.discard(item.url)
        self._finished[item.url] = item
        if item.url != item.final_url:  # redirected
            self._finished[item.final_url] = item

    def _create_item(self, url, TTL):
        if url in self._finished or url in self._in_progress:  # scheduled already
            return
        new_item = item.Item(url, TTL)
        self._in_progress.add(url)
        self._downloader.add_item(new_item)

    def _handle_feedback(self):
        item = self._in_queue.get()
        self._finish(item)
        if item.is_handled:
            if item.TTL >= 1:
                for l in item.links:
                    self._create_item(l, item.TTL - 1)
