#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Item(object):
    """
    下载项目
    在初始化和解析链接后创建于Scheduler，随后沿着Scheduler->Downloader->ItemHandler->Scheduler路径流动
    """
    def __init__(self, url, TTL):
        self.url = url
        self.TTL = TTL
        self.is_requested = False
        self.headers = None
        self.encoding = None
        self.content = None
        self.final_url = None
        self.is_finished = False
        self.children = []
