#!/usr/bin/env python
import os
import sys
import yaml
import json
import logging


# Defined vendors and handlers #
from vendors.dell import DellBios
from vendors.hp import HPBios
BIOS_HANDLERS = {"dell": DellBios}
#


def output_json(path, results):
    with open(path, "w") as result_file:
        result_file.write(json.dumps(results))


def main():
    if len(sys.argv) != 2:
        logging.error("Wrong number of arguments.")
        sys.exit(1)
    arg = sys.argv[1].strip()
    res_path = arg + "/results.json"
    # open JSON results file
    if not os.path.exists(res_path):
        data = {}
    else:
        with open(res_path) as data_file:
            try:
                data = json.load(data_file)
            except:
                data = {}

    path = os.path.dirname(os.path.realpath(__file__))
    with open(path + "/biosconfig.yaml", "r") as config_file:
        d = yaml.load(config_file.read())
        for vendor in d:
            if vendor not in BIOS_HANDLERS:
                logging.warning("Skipping %s, no handler found" % vendor)
                continue
            base_path = os.path.abspath(arg + "/" + d[vendor]["name"])
            if not os.path.exists(base_path):
                os.mkdir(base_path)
                logging.info("Creating folder " + base_path)
            h = BIOS_HANDLERS[vendor](d[vendor], arg)
            if vendor not in data:
                data[vendor] = {}
            h.update(data[vendor])

    output_json(res_path, data)

if __name__ == "__main__":
    main()
