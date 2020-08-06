#!/usr/bin/env python

from semeio.jobs.ots import ots_run
import argparse
from semeio import valid_file

description = (
    "Overburden timeshift (OTS) generates evolution of reservoir surfaces"
    "based on eclipse models and seismic velocity volume."
    "Input yml needs to contains vintages section, where at least one of the four categories"
    "for the surface computation needs to be set."
)

category = "modeling.surface"


def _get_args_parser():
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-c", "--config", help="ots config file, yaml format required", type=valid_file
    )
    return parser


def main_entry_point(args=None):
    parser = _get_args_parser()
    options = parser.parse_args(args)
    ots_run(options.config)


if __name__ == "__main__":
    main_entry_point()
