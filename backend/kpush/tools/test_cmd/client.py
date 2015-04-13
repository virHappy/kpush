# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from netkit.contrib.tcp_client import TcpClient
from netkit.box import Box
from web.application import create_app
from worker.worker_share import proto
from worker.worker_share.utils import pack_data, unpack_data


worker_client = TcpClient(Box, '115.28.224.64', 29000)


def test_register():
    req = dict(
        device_id=2
    )
    worker_client.write(dict(
        cmd=proto.CMD_REGISTER,
        body=pack_data(req)
    ))

    while not worker_client.closed():
        box = worker_client.read()
        if box:
            print unpack_data(box.body)
        else:
            break


def main():
    worker_client.connect()
    test_register()

if __name__ == '__main__':
    app = create_app()
    with app.test_request_context():
        main()
