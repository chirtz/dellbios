#!/usr/bin/env python
import argparse
import json
import logging
import os
import sys
import yaml


# Defined vendors and handlers #
from vendors.dell import DellBios
BIOS_HANDLERS = {"dell": DellBios}
#


def output_json(path, results):
    with open(path, "w") as result_file:
        result_file.write(json.dumps(results))


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    with open(path + "/biosconfig.yaml", "r") as config_file:
        d = yaml.load(config_file.read())

    if "vendors" not in d:
        logging.error("No vendors defined")
        sys.exit(1)


    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o','--output_folder',
        help='Output folder for files',
        required=False)
    parser.add_argument('-s','--single_sysid',
                         help='Single System ID', required=False)
    parser.add_argument('-l','--list',
                         help='List available System IDs', required=False,
                         action='store_true')
    parser.add_argument('-x','--show',
                         help='List available System IDs', required=False)
    args = vars(parser.parse_args())

    if args["output_folder"] is None:
        if "output_folder" in d:
            args["output_folder"] = d["output_folder"]
        else:
            logging.error("No output folder defined")
            sys.exit(1)

    res_path = args["output_folder"] + "/results.json"

    if not os.path.exists(res_path):
        data = {}
    else:
        with open(res_path) as data_file:
            try:
                data = json.load(data_file)
            except:
                data = {}

    if args["list"]:
        print yaml.dump(d["vendors"], default_flow_style=False, default_style='')
        sys.exit(0)

    vendors = d["vendors"]

    if args["show"]:
        for vendor in data:
            v = data[vendor]
            if args["show"] in v:
                print(json.dumps(v[args["show"]], indent=2))
                sys.exit(0)
        sys.exit(1)








    for vendor in vendors:
        if vendor not in BIOS_HANDLERS:
            logging.warning("Skipping %s, no handler found" % vendor)
            continue
        base_path = os.path.abspath(args["output_folder"] + "/" + vendors[vendor]["name"])
        if not os.path.exists(base_path):
            os.mkdir(base_path)
            logging.info("Creating folder " + base_path)
        h = BIOS_HANDLERS[vendor](vendors[vendor], args["output_folder"])
        if vendor not in data:
            data[vendor] = {}
        h.update(data[vendor], 
            sid=args["single_sysid"])

    output_json(res_path, data)
