# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

import json
from netkit.contrib.tcp_client import TcpClient
from netkit.box import Box
from web.application import create_app
from maple import Trigger
from share import proto


trigger = Trigger(Box, '115.28.224.64', 28000)


def test_notification():
    trigger.write_to_users((
        ((1, 2), dict(cmd=1000, body='')),
    ))


def main():
    test_notification()

if __name__ == '__main__':
    app = create_app()
    with app.test_request_context():
        main()
