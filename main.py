"""
Copyright (c) 2022 Gnifajio None [gnifajio@ya.ru].
All Rights Reserved.
"""

from genericpath import isfile
import logging
import sys
from os.path import exists as exists_data
import os

from analyzer import analyse_file
from config_loader import arguments_loader, Config

if __name__ == "__main__":
    args = arguments_loader.parse_args()
    config = Config(args, filename=args.config)

    if args.log.lower() == "info":
        log_level = logging.INFO
    elif args.log.lower() == "debug":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        filename="grep_logs.log",
        level=log_level,
        format="{asctime} {levelname}: {module}: {message}",
        datefmt="%m/%d/%Y %H:%M:%S",
        style="{",
    )
    logging.debug(f"args: {repr(args)}")
    logging.debug(f"input is dir: {os.path.isdir(args.input)}")
    if args.destination:
        destination = args.destination
    else:
        destination = f"{args.input}_{config.extension}"
    if not exists_data(destination):
        os.makedirs(destination)
    logging.debug(f"destination: {repr(destination)}")
    if os.path.isfile(args.input):
        logging.debug(f"input file: {repr(args.input)}")
        analyse_file(args.input, config, destination=destination)
    else:
        logging.critical(f"Path or file {repr(args.input)} does not exist.")
        sys.exit(1)
