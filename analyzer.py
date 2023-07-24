import logging
import os.path
import re
from urllib.parse import urlparse

from config_loader import Config


def get_field_weight(line: str, config: Config) -> int:
    line = line.lower()
    _temp_split = [i for x in re.split(r"\b", line) if (i := x.strip())]
    line_split = []
    i = 0
    while i < len(_temp_split):
        if _temp_split[i] in config.ignore_symbols:
            if len(_temp_split) > i + 1:
                line_split[-1] += _temp_split[i] + _temp_split[i + 1]
            else:
                line_split[-1] += _temp_split[i]
            i += 1
        else:
            line_split.append(_temp_split[i])
        i += 1
    weight = 0
    keywords = []
    for n, word in enumerate(line_split):
        if word == config.rule:
            keywords.append(n)
            weight += config.weight

    for suffix in config.suffixes:
        suffix_low = suffix.word.lower()
        for kw in keywords:
            l: int = kw - suffix.distance.left
            r: int = kw + suffix.distance.right
            if l < 0:
                l: int = 0
            if r >= len(line_split):
                r: int = len(line_split)
            suffix_found = line_split[l:r]
            if suffix.mode == "i":  # inaccurate
                _w = sum([1 for word in suffix_found if (word.find(suffix_low) > -1)])
            else:  # accurate
                _w = suffix_found.count(suffix_low)

            weight += _w * suffix.weight
    # print(weight)
    return weight


def analyse_file(filename: str, config: Config, destination: str = ".") -> None:
    logging.info(f"Started parsing file {repr(filename)}.")
    file_path = os.path.join(
        destination,
        f"{(os.path.splitext(os.path.basename(filename))[0])}{config.extension}",
    )
    logging.info(f"The result will be saved with the name {repr(file_path)}.")
    open(file_path, "w").close()
    saved_lines = 0
    with open(filename, "r", encoding="cp1251", errors="ignore") as input_file:
        for line in input_file:
            line = line.strip()
            all_fields = line.split(config.separator)
            weight = 0

            domain_field = all_fields[config.domains_field]
            text_fields = [all_fields[i] for i in config.fields]

            for field in text_fields:
                weight += get_field_weight(field, config)

            if weight > 0:
                netloc = urlparse(domain_field).netloc
                for domain in config.domains:
                    if domain.domain == ".".join(
                        netloc.split(".")[-len(domain.domain.split(".")) :]
                    ):
                        weight *= domain.weight
                        break
                else:
                    weight *= config.domains_default_weight

                saved_lines += 1
                with open(file_path, "a") as res_file:
                    res_file.write(config.separator.join([line, str(weight)]) + "\n")
    logging.info(f"Rows saved: {saved_lines}.")
    logging.info(f"Analysis of file {repr(filename)} completed.")
