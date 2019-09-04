import os
import json
import socket
import psutil
from uuid import uuid4
from time import time, sleep
from multiprocessing.connection import Listener, Client
from traceback import format_exc
from qaviton_helpers import try_to
# from qaviton_package_manager.conf import ignore_list
from qaviton_package_manager.utils.functions import find_free_port
from qaviton_git.git_wrapper import get_root
from qaviton_processes import python_code_async


class ServerDownError(ConnectionAbortedError):
    ...


class Cache:
    authkey = bytes(str(uuid4()), 'utf-8')
    root = get_root()
    file = root + os.sep + '.qaviton_package_manager_cache'
    errors = root + os.sep + '.qaviton_package_manager_cache.errors'
    request_timeout = 30

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

    def server_is_alive(self):
        if not self.is_file():
            return False
        try:
            self.get()
            return True
        except ServerDownError:
            return False

    def log_server_error(self):
        if not os.path.exists(self.errors):
            open(self.errors, 'w').close()
        with open(self.errors, 'a') as f:
            f.write('\n\n' + format_exc())

    def server(self, cache_timeout, **kwargs):
        try:
            def send_response(response: dict):
                with Client(client_address, authkey=token) as conn:
                    try:
                        conn.send(response)
                    except:
                        conn.send({'error': format_exc()})

            timeout = cache_timeout
            port = find_free_port()
            server_address = ('localhost', port)
            with Listener(server_address, authkey=self.authkey) as listener:
                if timeout != -1:
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
                            send_response({key: kwargs[key] for key in data['kwargs'] if key in kwargs})

                        elif data['method'] == self.method.post:
                            kwargs.update(data['kwargs'])
                            send_response({})

                        elif data['method'] == self.method.delete:
                            send_response({})
                            if len(data['kwargs']) == 0:
                                break
                            for key in data['kwargs']:
                                if key in kwargs:
                                    del kwargs[key]
                        else:
                            send_response({'error': 'unsupported method'})
                    except:
                        self.log_server_error()
                    finally:
                        conn.close()
                    if time() > timeout + 5 and timeout != -1:
                        break
        except:
            self.log_server_error()

    def create_server(self, cache_timeout, **kwargs):
        self.remove_file()
        p = python_code_async(
            'from qaviton_package_manager.utils.cache_cred import Cache',
            'cache = Cache()',
            f'cache.server({cache_timeout}, **{kwargs})'
        )
        self.wait_for_file(timeout=10)
        return p

    def request(self, method, **kwargs)->dict:
        self.wait_for_file(self.request_timeout)
        d = self.get_file_content()
        server_key = d['key']
        server_address = tuple(d['address'])
        server_timeout = d['timeout']
        server_pid = d['pid']
        server_name = d['name']
        server_created = d['created']

        if (time() > server_timeout or server_timeout == -1) and psutil.pid_exists(server_pid):
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
                        listener._listener._socket.settimeout(self.request_timeout)
                        conn = listener.accept()
                        data: dict = conn.recv()
                        if 'error' in data:
                            raise ConnectionError(data['error'])
                    return data
        raise ServerDownError("the cache server is down")

    def get(self, *args) -> dict: return self.request(self.method.get, **{key: True for key in args})
    def post(self, **kwargs) -> dict: return self.request(self.method.post, **kwargs)
    def delete(self, *args) -> dict: return self.request(self.method.delete, **{key: True for key in args})
