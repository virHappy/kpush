# -*- coding: utf-8 -*-

proc_name = 'kpush_site'
# sync/gevent
worker_class = 'sync'
bind = ['127.0.0.1:16200']
workers = 1
# for debug
#accesslog = '-'
#loglevel = 'debug'
#debug=True
