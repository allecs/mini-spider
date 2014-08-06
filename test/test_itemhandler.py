
import unittest
import item
import itemhandler


class ItemHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.item_handler = itemhandler.ItemHandler('./output', '.*\.(gif|png|jpg|bmp)$')

    def test_is_text(self):
        i = item.Item('www.baidu.com', 3)
        i.headers = {'content-type': 'text/html'}
        self.assertTrue(self.item_handler.need_parse(i))
        i.headers = {'content-type': 'text/plain'}
        self.assertFalse(self.item_handler.need_parse(i))
        i.headers = {'content-type': 'application/pdf'}
        self.assertFalse(self.item_handler.need_parse(i))
        i.headers = {'content-type': 'video/mp4'}
        self.assertFalse(self.item_handler.need_parse(i))

    def test_get_all_links(self):
        i = item.Item('', 4)
        i.final_url = 'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/'
        i.content = '''
                    <!DOCTYPE html>
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
                                <script>location.href="page1_1.html";</script>
                                <meta http-equiv="refresh" content="0;url=page1_2.html">
                            </ul>
                        </body>
                    </html>
                    '''
        l = self.item_handler.get_all_links(i)
        expected = [
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page1.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page2.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page3.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/mirror/index.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page4.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page1_1.html',
            'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/page1_2.html', ]
        self.assertListEqual(sorted(expected), sorted(l))

    def test_is_target(self):
        i = item.Item('www.baidu.com/1.bmp', 3)
        i.final_url = 'www.baidu.com/1.bmp'
        self.assertTrue(self.item_handler._is_target(i))
        i.final_url = 'www.baidu.xx.123.jpg'
        self.assertTrue(self.item_handler._is_target(i))
        i.final_url = 'www.baidu.com/1.htm'
        self.assertFalse(self.item_handler._is_target(i))
        i.final_url = 'www.baidu.com/1.jpg.htm'
        self.assertFalse(self.item_handler._is_target(i))

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
