#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import getopt
import logging

import sys
import scheduler
import downloader
import itemhandler


def usage():
    print >> sys.stderr, '''Usage: python mini_spider.py -c <conf file>'''


def setup_log():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                        format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * "
                               "%(thread)d %(message)s",
                        datefmt="%m-%d %H:%M:%S")


def get_config(config_file):
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    conf_dict = {}
    for k, v in config.items('spider'):
        conf_dict[k] = v
    return conf_dict


def main():
    config_file = ''
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'c:')
        for o, a in optlist:
            if o == '-c':
                config_file = a
                break
        else:
            raise getopt.GetoptError('Missing conf file')
    except getopt.GetoptError as error:
        print >> sys.stderr, error
        usage()
        exit(1)
    conf_dict = get_config(config_file)
    try:
        url_list_file = conf_dict['url_list_file']
        output_directory = conf_dict['output_directory']
        max_depth = conf_dict['max_depth']
        crawl_interval = conf_dict['crawl_interval']
        crawl_timeout = conf_dict['crawl_timeout']
        target_url = conf_dict['target_url']
        thread_count = conf_dict['thread_count']
    except KeyError as error:
        print >> sys.stderr, error
        exit(1)

    seeds = []
    try:
        with open(url_list_file) as seed_file:
            seeds.append(seed_file.readline())
    except EnvironmentError as error:
        print >> sys.stderr, error
        exit(1)

    setup_log()
    sched = scheduler.Scheduler(int(max_depth), seeds)
    dldr = downloader.Downloader(int(thread_count), float(crawl_interval), float(crawl_timeout))
    hdlr = itemhandler.ItemHandler(output_directory, target_url)
    sched.set_downloader(dldr)
    dldr.set_handler(hdlr)
    hdlr.set_scheduler(sched)

    dldr.start()
    hdlr.start()
    sched.start()


if __name__ == '__main__':
    main()
