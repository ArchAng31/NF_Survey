import Queue
import os
import socket
import thread

import MITMProxy
from libmproxy import proxy
from libmproxy.proxy.server import ProxyServer

# deploys an instance of mitmproxy
# <db_query_query> is the queue used to pass down query strings and arguments to the DataAggregator
# <crawl_id> is the id set by the TaskManager

def init_proxy(db_socket_address, crawl_id):
    proxy_site_queue = Queue.Queue()  # queue for crawler to communicate with proxy

    # gets local port from one of the free ports
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    proxy_port = sock.getsockname()[1]
    sock.close()

    #config = proxy.ProxyConfig(cacert=os.path.join(os.path.dirname(__file__), 'mitmproxy.pem'),)
    #config = proxy.ProxyConfig(port=proxy_port)
    config = proxy.ProxyConfig(cadir=os.path.join(os.path.dirname(__file__), 'cert'),port=proxy_port)
    server = ProxyServer(config)
    print 'Intercepting Proxy listening on ' + str(proxy_port)
    m = MITMProxy.InterceptingMaster(server, crawl_id, proxy_site_queue, db_socket_address)
    thread.start_new_thread(m.run, ())
    return proxy_port, proxy_site_queue
