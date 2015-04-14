# -*- coding: utf-8 -*-

from worker.worker_share import proto


def login_required(func):
    import functools
    @functools.wraps(func)
    def func_wrapper(request, *args, **kwargs):
        if request.gw_box.uid <= 0:
            request.write_to_client(dict(
                ret=proto.RET_NOT_LOGIN,
            ))
            return

        return func(request, *args, **kwargs)
    return func_wrapper

