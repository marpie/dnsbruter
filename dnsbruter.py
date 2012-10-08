#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" dnsbruter

    DNS Subdomain Brute forcer.

    Hint: Remove the "search" and "domain" directive in 
          /etc/resolv to minimize the DNS requests ;-)

    Author: marpie (marpie@a12d404.net)

    Last Update:  20121008
    Created:      20121008

"""
import argparse
import time
from threading import Thread
from Queue import Queue
from os.path import isfile
import socket

# Version Information
__version__ = "0.0.1"
__program__ = "dnsbruter v" + __version__
__author__ = "marpie"
__email__ = "marpie+dnsbruter@a12d404.net"
__license__ = "BSD License"
__copyright__ = "Copyright 2012, a12d404.net"
__status__ = "Prototype"  # ("Prototype", "Development", "Testing", "Production")

#SCRIPT_PATH = os.path.dirname( os.path.realpath( __file__ ) )

def resolv_worker(domains, input_queue, output_queue):
    while True:
        subdomain = input_queue.get()
        for domain in domains:
            try:
                ip = socket.gethostbyname(subdomain + "." + domain)
                output_queue.put((subdomain + "." + domain, ip))
            except:
                pass
        input_queue.task_done()

def output_thread(q):
    while True:
        domain, ip = q.get()
        print(domain + ";" + ip)
        q.task_done()

# Main
def main(argv):
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('domains', metavar='DOMAIN', type=str, nargs='+',
                        help='Target domains to test.')
    parser.add_argument('--threads', dest='threads', type=int,
                        default=100,
                        help='DNS resolver threads (default: 100)')
    parser.add_argument('--timeout', dest='timeout', type=int,
                        default=0.5,
                        help='DNS resolver timeout in seconds (default: 1)')
    parser.add_argument('--wordlist', dest='wordlist', 
                        default="dns-big.txt",
                        help='Subdomain wordlist (default: dns-big.txt)')
    args = parser.parse_args()

    if not isfile(args.wordlist):
        print("Subdomain wordlist not found: " + args.wordlist)
        return False

    socket.setdefaulttimeout(args.timeout)

    start = int(time.time())
    print("[*] Loding wordlist(s)...")
    in_queue = Queue()
    out_queue = Queue()
    counter = 0
    with open(args.wordlist, 'r') as f:
        for line in f:
            in_queue.put(line.strip())
            counter += 1

    print("[*] Starting DNS resolver...")
    for i in xrange(0,args.threads):
        t = Thread(target=resolv_worker, args=(args.domains, in_queue, out_queue,))
        t.daemon = True
        t.start()

    print("[*] Starting Output Thread...")
    t = Thread(target=output_thread, args=(out_queue,))
    t.daemon = True
    t.start()

    print("[*] Working...")
    in_queue.join()
    out_queue.join()
    tick = int(time.time())-start
    try:
        persec = counter/tick
    except ZeroDivisionError:
        persec = counter
    print("[X] Done (%d seconds for %d requests [%.2f/s])" % (tick, counter, persec))

    return True


if __name__ == "__main__":
    import sys
    print( __doc__ )
    sys.exit( not main( sys.argv ) )
