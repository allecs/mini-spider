#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Item(object):
    def __init__(self, url, TTL):
        self.url = url
        self.TTL = TTL
        self.is_requested = False
        self.headers = None
        self.encoding = None
        self.content = None
        self.final_url = None
        self.is_finished = False
