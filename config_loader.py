"""
Copyright (c) 2022 Gnifajio None [gnifajio@ya.ru].
All Rights Reserved.
"""

import argparse
import logging
import re
import sys
from collections import namedtuple
import os
import toml

Suffix = namedtuple("Suffix", "word weight distance mode")
Domain = namedtuple("Domain", "domain weight")


def normalize_extension(extension: str) -> str:
    if extension.startswith("."):
        return extension
    else:
        return f".{extension}"


def get_suffix_data(data: str) -> Suffix:
    found = re.match("(['\"])(.+?)\\1", data)
    text = found.group(2)
    data = data[found.end() + 1 :]
    suff_args = dict(
        zip(("weight", "distance", "mode"), (i.strip() for i in data.split(":")))
    )
    distance = [
        int(x) if (x := i.strip()) else 0 for i in suff_args["distance"].split("+")
    ]
    weight = float(suff_args["weight"]) if suff_args["weight"] else 0
    mode = suff_args.get("mode")

    return Suffix(text, weight, Distance(left=distance[0], right=distance[-1]), mode)


def load_domain(data: str, config) -> Domain:
    try:
        domain, weight = data.split(":")
    except ValueError:
        domain, weight = data, config.domains_default_weight

    weight = float(weight)
    return Domain(domain=domain, weight=weight)


class Distance:
    default_left = 0
    default_right = 0

    def __init__(self, default=None, left=None, right=None):
        if left is None:
            left = self._get_default_left(default)
        if right is None:
            right = self._get_default_right(default)

        self.left = left
        self.right = right

    @classmethod
    def _get_default_left(cls, default):
        if default:
            return default
        elif cls.default_left is not None:
            return cls.default_left

    @classmethod
    def _get_default_right(cls, default):
        if default:
            return default
        elif cls.default_right is not None:
            return cls.default_right

    def __repr__(self):
        return f"{self.__class__.__name__}(left = {self.left}, right = {self.right})"


class Config:
    def __init__(self, args, filename: str = "config.toml"):
        config = toml.load(filename)
        config_path = os.path.dirname(filename)
        suffix_space = config.get("suffix", {})
        domains_space = config.get("domains")

        self.extension: str = normalize_extension(config.get("extension", "ggs"))
        self.weight = config["rule"].get("weight", 0)

        try:
            rule_space = config["rule"]
        except KeyError:
            logging.critical("Configuration Error: Rule section not found.")
            sys.exit(2)

        try:
            self.separator: str = config["separator"]
        except KeyError:
            logging.critical(
                "Configuration Error: global parameter separator not found."
            )
            sys.exit(3)

        try:
            _err = False
            field = config["field"]
            if isinstance(field, int):
                self.fields = [field]
            elif isinstance(field, list):
                if all(map(lambda x: isinstance(x, int), field)):
                    self.fields = field
                else:
                    _err = True
            else:
                _err = True
            if _err:
                logging.critical(
                    "Configuration Error: the global parameter field must be a number or a list of numbers."
                )
                sys.exit(4)
        except KeyError:
            logging.critical("Configuration Error: global parameter field not found.")
            sys.exit(5)

        try:
            distance_space = suffix_space["distance"]
            default_distance = distance_space.get("default", 0)
            left_distance = distance_space.get("left")
            right_distance = distance_space.get("right")
            if left_distance is None:
                left_distance = default_distance
            if right_distance is None:
                right_distance = default_distance

            Distance.default_left = left_distance
            Distance.default_right = right_distance
            self.distance = Distance(
                default=default_distance,
            )
        except KeyError:
            logging.critical(
                "Configuration Error: suffix section distance global parameter not found"
            )
            sys.exit(7)

        try:
            self.rule = rule_space["text"].lower()
        except KeyError:
            logging.critical(
                "Configuration Error: the text parameter in the rule section was not found."
            )
            sys.exit(8)

        self.ignore_symbols = rule_space.get("ignore", "")

        dom_filename = domains_space.get("file", args.suffix)
        suf_filename = suffix_space.get("file", args.suffix)
        self.domains_default_weight = domains_space.get("weight", 0)
        try:
            self.domains_field = domains_space["field"]
        except KeyError:
            logging.critical(
                "The configuration file does not specify the required field parameter in the domains section."
            )
            exit(9)

        if dom_filename:
            dom_path = os.path.join(config_path, dom_filename)
            with open(dom_path) as dom_file:
                self.domains = [load_domain(line, self) for line in dom_file]

            if not self.domains:
                logging.warning(f"No domains found in file {repr(filename)}.")
        else:
            logging.warning(f"Domains file not specified.")

        if suf_filename:
            suf_path = os.path.join(config_path, suf_filename)
            with open(suf_path) as suf_file:
                self.suffixes = [get_suffix_data(line) for line in suf_file]

            if not self.suffixes:
                logging.warning(f"No suffix found in file {repr(filename)}.")
        else:
            logging.warning(f"Suffix file not specified.")


arguments_loader = argparse.ArgumentParser()
arguments_loader.add_argument(
    "input", type=str, help="The path to the file or folder to analyze"
)

arguments_loader.add_argument(
    "--config",
    type=str,
    default="config.toml",
    help="The path to the configuration file",
)
arguments_loader.add_argument("--suffix", type=str, help="The path to the suffix file")
arguments_loader.add_argument("--domains", type=str, help="The path to the domain file")
arguments_loader.add_argument(
    "--destination",
    type=str,
    default=".",
    help="The path to the file or folder to output",
)

arguments_loader.add_argument(
    "--log", "-l", type=str, default="info", help="The path to the configuration file"
)
