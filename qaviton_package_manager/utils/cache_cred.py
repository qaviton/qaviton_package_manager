import os
import json
import socket
import psutil
from time import time, sleep
from multiprocessing.connection import Listener, Client
from qaviton_package_manager.utils.functions import find_free_port
from traceback import format_exc
from qaviton_package_manager.conf import ignore_list
from qaviton_package_manager.utils.git_wrapper import get_root


class ServerDownError(ConnectionAbortedError):
    ...


class Cache:
    authkey = b'qaviton is cool'
    root = get_root()
    file = root + os.sep + ignore_list[1]
    errors = root + os.sep + ignore_list[2]
    class method:
        get = 'GET'
        delete = 'DELETE'
        post = 'POST'

    def remove_file(self):
        os.remove(self.file)

    def wait_for_file(self, timeout):
        t = time()
        while not os.path.exists(self.file):
            if time()-t > timeout:
                raise TimeoutError("timed out while waiting for server details")
            sleep(0.1)

    def server_is_alive(self, timeout=5):
        if not os.path.exists(self.file):
            return False
        try:
            self.client(timeout, self.method.get)
            return True
        except ServerDownError:
            return False

    def server(self, cache_timeout, **kwargs):
        timeout = cache_timeout
        port = find_free_port()
        server_address = ('localhost', port)
        with Listener(server_address, authkey=self.authkey) as listener:
            listener._listener._socket.settimeout(timeout if timeout < 60*60*24 else 60*60*24)  # avoid OverflowError: timeout doesn't fit into C timeval
            t = time()
            server_data = {
                'key': self.authkey.decode('utf-8'),
                'address': list(server_address),
                'time': t,
                'timeout': timeout,
                'pid': os.getpid()
            }
            with open(self.file, 'w') as f:
                json.dump(server_data, f, indent=2)
            while True:
                if timeout > time() or timeout == -1:
                    if time() > t + 1:
                        t = time()
                        server_data['time'] = t
                        with open(self.file, 'w') as f:
                            json.dump(server_data, f, indent=2)
                try:
                    conn = listener.accept()
                except socket.timeout:
                    break
                try:
                    data: dict = conn.recv()
                    client_address = tuple(data['address'])
                    token = data['token'].encode('utf-8')
                    if data['method'] == self.method.get:
                        with Client(client_address, authkey=token) as conn:
                            try:
                                conn.send({key: kwargs[key] for key in data['kwargs']})
                            except:
                                conn.send({'error': format_exc()})
                    elif data['method'] == self.method.post:
                        kwargs.update(data['kwargs'])
                    elif data['method'] == self.method.delete:
                        break
                    else:
                        conn.send({'error': 'unsupported method'})
                except:
                    if not os.path.exists(self.errors):
                        open(self.errors, 'w').close()
                    with open(self.errors, 'a') as f:
                        f.write('\n\n'+format_exc())
                finally:
                    conn.close()
                if time() > timeout + 5 != -1:
                    break

    def client(self, timeout, method, **kwargs):
        self.wait_for_file(timeout)
        with open(self.file) as f:
            d = json.load(f)

        key, server_address, t, server_timeout, pid = d['key'], tuple(d['address']), d['time'], d['timeout'], d['pid']
        if time() > server_timeout != -1 and time() - t < 4 and psutil.pid_exists(pid):
            connections = [c for c in psutil.Process(pid).connections() if c.status == psutil.CONN_LISTEN]
            for c in connections:
                if server_address[1] == c[3][1]:  # check process is listening to port
                    client_address = ('localhost', find_free_port())
                    with Client(server_address, authkey=key.encode('utf-8')) as conn:
                        conn.send({
                            'token': self.authkey.decode('utf-8'),
                            'address': list(client_address),
                            'method': method,
                            'kwargs': kwargs
                        })
                    with Listener(client_address, authkey=self.authkey) as listener:
                        listener._listener._socket.settimeout(timeout)
                        conn = listener.accept()
                        data: dict = conn.recv()
                        if 'error' in data:
                            raise ConnectionError(data['error'])
                    return data
        raise ServerDownError("the cache server is down")
