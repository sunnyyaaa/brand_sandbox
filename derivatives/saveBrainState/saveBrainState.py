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
    ap.add_argument('-n', '--nickname',    type=str, required=True) # require for a nickname to identify the source of logs in the Redis log stream
    ap.add_argument('-i', '--redis_host',  type=str, required=True) # require for the Redis host to connect to
    ap.add_argument('-p', '--redis_port',  type=int, required=True) # require for the Redis port to connect to
    ap.add_argument('-s', '--redis_socket', type=str, required=False) # optional Redis socket path
    args = ap.parse_args() # Parse the command-line arguments and store them in args
    # used later in logging configuration and Redis connection setup
    name = args.nickname

    logging.basicConfig(
        format=f'[{name}] %(levelname)s: %(message)s', # [{name}] is might be the name of the script/ node, %(levelname)s is the log level, and %(message)s is the log message
        level=logging.INFO, # set the logging level to INFO, which means only displayed WARNING, ERROR, CRITICAL logs
        stream=sys.stdout, # print logs to terminal
    )
    # Define what should happen when the user presses Ctrl+C.
    # The script logs a message and exits cleanly.  
    def signal_handler(sig, frame):
        logging.info('SIGINT received. Exiting...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        logging.info(f"Connecting to Redis at {args.redis_host}:{args.redis_port}...")
        r = Redis(args.redis_host, args.redis_port, args.redis_socket, retry_on_timeout=True) # Create a Redis client instance used in things like r.xread() and r.save()
        r.ping() # test the connection
    except ConnectionError as e:
        logging.error(f"Error with Redis connection: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")
        sys.exit(1)

    logging.getLogger().addHandler(RedisLoggingHandler(r, name))
    # RedisLoggingHandler(r, name) send the logs to Redis 
    # same as 
    # redis_handler = RedisLoggingHandler(r, name)
    # logger = logging.getLogger()
    # logger.addHandler(redis_handler)
    logging.info('Redis connection successful.')

    r.save() # save the Redis database to an RDB dump file
    rdb_filename = r.config_get('dbfilename')['dbfilename'] # get the name of the RDB file from Redis config
    logging.info(f"RDB data saved to file: {rdb_filename}")


if __name__ == "__main__":
    main()
