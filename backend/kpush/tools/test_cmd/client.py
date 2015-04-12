# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

import json
from netkit.contrib.tcp_client import TcpClient
from netkit.box import Box
from web.application import create_app
from share import proto


worker_client = TcpClient(Box, '115.28.224.64', 29000)


def test_register():
    req = dict(
        device_id=2
    )
    worker_client.write(dict(
        cmd=proto.CMD_REGISTER,
        body=json.dumps(req)
    ))

    while not worker_client.closed():
        print worker_client.read()
        

def main():
    worker_client.connect()
    test_register()

if __name__ == '__main__':
    app = create_app()
    with app.test_request_context():
        main()
