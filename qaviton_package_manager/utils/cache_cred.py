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
from qaviton_package_manager.utils.system import pythonCIO
from qaviton_package_manager.utils.functions import try_to


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

    def kill_server(self):
        pid = self.get_file_content()['pid']
        try_to(psutil.Process(pid).kill)
        self.remove_file()

    def get_file_content(self):
        with open(self.file) as f:
            content = json.load(f)
        return content

    def is_file(self):
        return os.path.exists(self.file)

    def remove_file(self):
        if self.is_file():
            os.remove(self.file)

    def wait_for_file(self, timeout):
        t = time()
        while not self.is_file():
            if time()-t > timeout:
                raise TimeoutError("timed out while waiting for server details")
            sleep(0.1)

    def server_is_alive(self, timeout=5):
        if not self.is_file():
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
            pid = os.getpid()
            p = psutil.Process(pid)
            with open(self.file, 'w') as f:
                json.dump({
                    'key': self.authkey.decode('utf-8'),
                    'address': list(server_address),
                    'timeout': timeout,
                    'pid': pid,
                    'name': p.name(),
                    'created': p.create_time()
                }, f, indent=2)
            del pid
            del p
            while True:
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
        d = self.get_file_content()
        server_key = d['key']
        server_address = tuple(d['address'])
        server_timeout = d['timeout']
        server_pid = d['pid']
        server_name = d['name']
        server_created = d['created']

        if time() > server_timeout != -1 and psutil.pid_exists(server_pid):
            server_process = psutil.Process(server_pid)
            connections = [c for c in server_process.connections() if c.status == psutil.CONN_LISTEN]
            for c in connections:
                # check process is listening to port
                if server_address[1] == c[3][1]\
                and server_process.name() == server_name\
                and server_process.create_time() == server_created:
                    client_address = ('localhost', find_free_port())
                    with Client(server_address, authkey=server_key.encode('utf-8')) as conn:
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

    def create_server(self, cache_timeout, **kwargs):
        self.remove_file()
        p = pythonCIO(
            'from qaviton_package_manager.utils.cache_cred import Cache',
            'cache = Cache()',
            f'cache.server({cache_timeout}, **{kwargs})'
        )
        self.wait_for_file(timeout=10)
        return p
