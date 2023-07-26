"""
Copyright (c) 2022 Gnifajio None [gnifajio@ya.ru].
All Rights Reserved.
"""

from genericpath import isfile
import logging
import sys
from os.path import exists as exists_data
import os
from datetime import datetime
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

    if args.destination:
        destination = args.destination
    else:
        destination = f"{args.input}_{config.extension}"
    if not exists_data(destination):
        os.makedirs(destination)
    filter_time = [s if s.isalnum() else "_" for s in str(datetime.utcnow())]
    unique_time = "".join(filter_time)
    logging.basicConfig(
        filename=os.path.join(
            destination,
            f"log_{unique_time}.log",
        ),
        level=log_level,
        format="{asctime} {levelname}: {module}: {message}",
        datefmt="%m/%d/%Y %H:%M:%S",
        style="{",
    )
    logging.debug(f"args: {repr(args)}")
    logging.debug(f"input is dir: {os.path.isdir(args.input)}")
    logging.info(f"Config path: {args.config}")

    logging.debug(f"destination: {repr(destination)}")
    if os.path.isfile(args.input):
        logging.debug(f"input file: {repr(args.input)}")
        analyse_file(args.input, config, unique_time, destination=destination)
    else:
        logging.critical(f"Path or file {repr(args.input)} does not exist.")
        sys.exit(1)
