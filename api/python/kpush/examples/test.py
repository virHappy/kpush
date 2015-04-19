# -*- coding: utf-8 -*-

from kpush import KPush


def main():
    kpush = KPush('127.0.0.1:5000', '7d357c9b4ce1414fb27f077b54fb5a8f', '9ae9c6782db54aaba1d17f339daabd48')

    print kpush.push(u'我爱', '我', dict(
        all=True,
        #alias='dante'
        #tags_or=[['x']],
    ), silent=True)

main()