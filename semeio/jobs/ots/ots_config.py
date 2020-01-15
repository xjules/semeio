# -*- coding: utf-8 -*-
import configsuite
import datetime

from configsuite import MetaKeys as MK
from configsuite import types
from copy import deepcopy


@configsuite.validator_msg("List needs to be of size 2")
def _is_length_equal_2(value):
    return len(value) == 2


@configsuite.validator_msg("Vintages must contain at least an entry!")
def _min_length(value):
    return len(value) > 1


@configsuite.transformation_msg("Converting list of strings to list of dates")
def _str2dates(value):
    value = deepcopy(value)
    dates = []
    for x in value:
        if isinstance(x, str):
            dates.append(datetime.datetime.strptime(x, "%Y-%m-%d").date())
        else:
            dates.append(x)
    return dates


@configsuite.validator_msg("OTS vintage date must be present in .UNRST file!")
def _vintage_present_in_rst(elem, context):
    return elem in context


def build_schema():
    return {
        MK.Type: types.NamedDict,
        MK.Description: "Overburden time shift job parameters",
        MK.Content: {
            "seabed": {MK.Required: True, MK.Type: types.Number},
            "rfactor": {MK.Required: True, MK.Type: types.Number},
            "above": {MK.Required: True, MK.Type: types.Number},
            "convention": {MK.Required: False, MK.Type: types.Number},
            "poisson": {MK.Required: True, MK.Type: types.Number},
            "youngs": {MK.Required: True, MK.Type: types.Number},
            "output_dir": {MK.Required: True, MK.Type: types.String},
            "horizon": {MK.Required: False, MK.Type: types.String},
            "eclbase": {MK.Required: True, MK.Type: types.String},
            "ascii": {MK.Required: False, MK.Type: types.String},
            "velocity_model": {MK.Required: True, MK.Type: types.String},
            "mapaxes": {MK.Required: True, MK.Type: types.Bool},
            "vintages": {
                MK.Required: True,
                MK.Type: types.NamedDict,
                MK.ElementValidators: (_min_length,),
                MK.Content: {
                    "ts_simple": {
                        MK.Required: False,
                        MK.Type: types.List,
                        MK.Content: {
                            MK.Item: {
                                MK.Type: types.List,
                                MK.Content: {
                                    MK.Item: {
                                        MK.Type: types.Date,
                                        MK.ContextValidators: (
                                            _vintage_present_in_rst,
                                        ),
                                    }
                                },
                                MK.ElementValidators: (_is_length_equal_2,),
                                MK.LayerTransformation: _str2dates,
                            }
                        },
                    },
                    "ts": {
                        MK.Required: False,
                        MK.Type: types.List,
                        MK.Content: {
                            MK.Item: {
                                MK.Type: types.List,
                                MK.Content: {
                                    MK.Item: {
                                        MK.Type: types.Date,
                                        MK.ContextValidators: (
                                            _vintage_present_in_rst,
                                        ),
                                    }
                                },
                                MK.ElementValidators: (_is_length_equal_2,),
                                MK.LayerTransformation: _str2dates,
                            }
                        },
                    },
                    "dpv": {
                        MK.Required: False,
                        MK.Type: types.List,
                        MK.Content: {
                            MK.Item: {
                                MK.Type: types.List,
                                MK.Content: {
                                    MK.Item: {
                                        MK.Type: types.Date,
                                        MK.ContextValidators: (
                                            _vintage_present_in_rst,
                                        ),
                                    }
                                },
                                MK.ElementValidators: (_is_length_equal_2,),
                                MK.LayerTransformation: _str2dates,
                            }
                        },
                    },
                    "ts_rporv": {
                        MK.Required: False,
                        MK.Type: types.List,
                        MK.Content: {
                            MK.Item: {
                                MK.Type: types.List,
                                MK.Content: {
                                    MK.Item: {
                                        MK.Type: types.Date,
                                        MK.ContextValidators: (
                                            _vintage_present_in_rst,
                                        ),
                                    }
                                },
                                MK.ElementValidators: (_is_length_equal_2,),
                                MK.LayerTransformation: _str2dates,
                            }
                        },
                    },
                },
            },
        },
    }


def get_default_values():
    default_values = {
        "vintages": {"ts_simple": [], "ts_rporv": [], "ts": [], "dpv": []},
        "youngs": 0,
        "convention": 1,
        "ascii": None,
        "horizon": None,
    }
    return default_values
