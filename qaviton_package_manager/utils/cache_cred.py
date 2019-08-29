import os
import json
import socket
import psutil
from time import time
from multiprocessing.connection import Listener, Client
from qaviton_package_manager.utils.functions import find_free_port
from traceback import format_exc
from qaviton_package_manager.conf import ignore_list
from qaviton_package_manager.utils.git_wrapper import get_root


class Cache:
    authkey = b'qaviton is cool'
    root = get_root()
    file = root + os.sep + ignore_list[1]
    errors = root + os.sep + ignore_list[2]

    def server(self, timeout, **kwargs):
        port = find_free_port()
        server_address = ('localhost', port)
        with Listener(server_address, authkey=self.authkey) as listener:
            listener._listener._socket.settimeout(timeout)
            t = time()
            server_data = {
                'key': self.authkey.decode('utf-8'),
                'address': list(server_address),
                'time': t,
                'timeout': timeout,
                'pid': os.getpid()
            }
            with open(self.file, 'w') as f:
                json.dump(server_data, f)
            while True:
                if timeout > time() or timeout == -1:
                    if time() > t + 1:
                        t = time()
                        server_data['time'] = t
                        with open(self.file, 'w') as f:
                            json.dump(server_data, f)
                try:
                    conn = listener.accept()
                except socket.timeout:
                    break
                try:
                    data: dict = conn.recv()
                    client_address = tuple(data['address'])
                    token = data['token'].encode('utf-8')
                    if data['method'] == 'get':
                        with Client(client_address, authkey=token) as conn:
                            try:
                                conn.send({key: kwargs[key] for key in data['kwargs']})
                            except:
                                conn.send({'error': format_exc()})
                    if data['method'] == 'delete'\
                    or time() > timeout+5 != -1:
                        break
                except:
                    if not os.path.exists(self.errors):
                        open(self.errors, 'w').close()
                    with open(self.errors, 'a') as f:
                        f.write('\n\n'+format_exc())
                finally:
                    conn.close()

    def client(self, timeout, method, **kwargs):
        assert method in ('get', 'delete')
        with open(self.file) as f:
            d = json.load(f)

        key, server_address, t, server_timeout, pid = d['key'], tuple(d['address']), d['time'], d['timeout'], d['pid']
        if time() > server_timeout != -1 and time() - t < 4 and psutil.pid_exists(pid):
            connections = [c for c in psutil.Process(pid).connections() if c.status == psutil.CONN_LISTEN]
            for c in connections:
                if server_address[1] == c[3][1]:  # check process is listening to port

                    client_port = find_free_port()
                    client_address = ('localhost', client_port)

                    with Client(server_address, authkey=key.encode('utf-8')) as conn:
                        conn.send({
                            'token': self.authkey.decode('utf-8'),
                            'address': list(client_address),
                            'method': method,
                            'kwargs': kwargs
                        })
                    with Listener(server_address, authkey=self.authkey) as listener:
                        listener._listener._socket.settimeout(timeout)
                        conn = listener.accept()
                        data: dict = conn.recv()
                        if 'error' in data:
                            raise ConnectionError(data['error'])
                    return data
        raise ConnectionAbortedError("the cache server is down")
