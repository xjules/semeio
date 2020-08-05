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
            "seabed": {MK.Type: types.Number},
            "rfactor": {MK.Type: types.Number},
            "above": {MK.Type: types.Number},
            "convention": {MK.Type: types.Number, MK.Default: 1},
            "poisson": {MK.Type: types.Number},
            "youngs": {MK.Type: types.Number, MK.Default: 0},
            "output_dir": {MK.Type: types.String},
            "horizon": {MK.Type: types.String, MK.Default: None},
            "eclbase": {MK.Type: types.String},
            "ascii": {MK.Type: types.String, MK.Default: None},
            "velocity_model": {MK.Type: types.String},
            "mapaxes": {MK.Type: types.Bool},
            "vintages": {
                MK.Type: types.NamedDict,
                MK.ElementValidators: (_min_length,),
                MK.Content: {
                    "ts_simple": {
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
                        # MK.Default: [],
                    },
                    "ts": {
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
                        # MK.Default: [],
                    },
                    "dpv": {
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
                        # MK.Default: [],
                    },
                    "ts_rporv": {
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
                        # MK.Default: [],
                    },
                },
            },
        },
    }


# def get_default_values():
#     default_values = {
#         "vintages": {"ts_simple": [], "ts_rporv": [], "ts": [], "dpv": []},
#         "youngs": 0,
#         "convention": 1,
#         "ascii": None,
#         "horizon": None,
#     }
#     return default_values
