# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from netkit.box import Box
from web.application import create_app
from maple import Trigger
from share.utils import pack_data


trigger = Trigger(Box, '115.28.224.64', 28000)


def test_notification():
    trigger.write_to_users((
        ((-1, ), dict(cmd=1000, body=pack_data(dict(
            title=u'我是标题',
            content=u'我是内容',
        )))),
    ))


def main():
    test_notification()

if __name__ == '__main__':
    app = create_app()
    with app.test_request_context():
        main()
