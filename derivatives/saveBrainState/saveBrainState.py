#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Saves Redis to an RDB dump file. Minimal version of saveRDB.py for the sandbox."""

import argparse
import logging
import signal
import sys

from brand.redis import RedisLoggingHandler
from redis import ConnectionError, Redis


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-n', '--nickname',    type=str, required=True)
    ap.add_argument('-i', '--redis_host',  type=str, required=True)
    ap.add_argument('-p', '--redis_port',  type=int, required=True)
    ap.add_argument('-s', '--redis_socket', type=str, required=False)
    args = ap.parse_args()

    name = args.nickname

    logging.basicConfig(
        format=f'[{name}] %(levelname)s: %(message)s',
        level=logging.INFO,
        stream=sys.stdout,
    )

    def signal_handler(sig, frame):
        logging.info('SIGINT received. Exiting...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        logging.info(f"Connecting to Redis at {args.redis_host}:{args.redis_port}...")
        r = Redis(args.redis_host, args.redis_port, args.redis_socket, retry_on_timeout=True)
        r.ping()
    except ConnectionError as e:
        logging.error(f"Error with Redis connection: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")
        sys.exit(1)

    logging.getLogger().addHandler(RedisLoggingHandler(r, name))
    logging.info('Redis connection successful.')

    r.save()
    rdb_filename = r.config_get('dbfilename')['dbfilename']
    logging.info(f"RDB data saved to file: {rdb_filename}")


if __name__ == "__main__":
    main()
