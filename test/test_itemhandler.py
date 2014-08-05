__author__ = 'aolixiang'

import unittest
import item
import itemhandler


class ItemHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.item_handler = itemhandler.ItemHandler('./output', '.*\.(gif|png|jpg|bmp)$')

    def test_is_target(self):
        self.assertTrue(self.item_handler._is_target('www.baidu.com/1.bmp'))
        self.assertTrue(self.item_handler._is_target('www.baidu.xx.123.jpg'))
        self.assertFalse(self.item_handler._is_target('www.baidu.com/1.htm'))
        self.assertFalse(self.item_handler._is_target('www.baidu.com/1.jpg.htm'))

    def test_save_to_file(self):
        i = item.Item('', 4)
        i.final_url = 'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/'
        i.content = '''<!DOCTYPE html>
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
            <li><a href='mirror/index.html'>http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/mirror/index.html</a></li>
            <li><a href='javascript:location.href="page4.html"'>page 4</a></li>
        </ul>
    </body>
</html>
'''
        self.item_handler._save_to_file(i)

    def test_get_all_links(self):
        i = item.Item('', 4)
        i.final_url = 'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/'
        i.content = '''<!DOCTYPE html>
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
            <li><a href='mirror/index.html'>http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/mirror/index.html</a></li>
            <li><a href='javascript:location.href="page4.html"'>page 4</a></li>
        </ul>
    </body>
</html>
'''
        for l in self.item_handler._get_all_links(i):
            print l
