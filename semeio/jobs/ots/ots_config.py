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
            "seabed": {
                MK.Type: types.Number,
                MK.Description: "The depth of the seabead in meters.",
            },
            "rfactor": {
                MK.Type: types.Number,
                MK.Description: "Scales the surface displacement between"
                " base_survey and monitor_survey, eg. 20.",
            },
            "above": {
                MK.Type: types.Number,
                MK.Description: "Distance in meters above the reservoir"
                " where shift is calculated. The distance from the "
                "shallowest cell, eg. 100",
            },
            "convention": {
                MK.Type: types.Number,
                MK.Description: "Positive or negative shift can be either 1 or -1,"
                " where 1 = monitor-base and -1 = base-monitor."
                "The default value is 1.",
                MK.Default: 1,
            },
            "poisson": {
                MK.Type: types.Number,
                MK.Description: "Poisson ratio. Describes the expansion or"
                " contraction of material in ecl_subsidence_eval.",
            },
            "youngs": {
                MK.Type: types.Number,
                MK.Description: "Youngs modulus. The default is 0.",
                MK.Default: 0,
            },
            "output_dir": {
                MK.Type: types.String,
                MK.Description: "Directory(ies) where the shift is written to disk."
                " Post fixed with type of algorithm: ts, ts_simple, dpv and ts_rporv",
            },
            "horizon": {
                MK.Type: types.String,
                MK.Description: "Path to result irap file, the surface mapped to "
                "the velocity grid, with the depth of horizon.",
                MK.Default: None,
            },
            "eclbase": {
                MK.Type: types.String,
                MK.Description: "Path to the Eclipse case.",
            },
            "ascii": {
                MK.Type: types.String,
                MK.Description: "Path to resulting text file, which contains all "
                "computed vintage pair dates: lines of x, y, z, ts1, ts2, ts3....",
                MK.Default: None,
            },
            "velocity_model": {
                MK.Type: types.String,
                MK.Description: "Path to segy file containing the velocity field.",
            },
            "mapaxes": {
                MK.Type: types.Bool,
                MK.Description: "Mapping axes from the global to local geometry."
                " Can be True or False. If False EclGrid will not "
                "apply transformation to the grid",
            },
            "vintages": {
                MK.Type: types.NamedDict,
                MK.ElementValidators: (_min_length,),
                MK.Description: "Vintage date pairs: date of base and monitor survey.",
                MK.Content: {
                    "ts_simple": {
                        MK.Type: types.List,
                        MK.Description: "Simple TimeShift geertsma algorithm."
                        "It assumes a constant velocity and is fast.",
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
                        MK.Type: types.List,
                        MK.Description: "TimeShift geertsma algorithm, which "
                        "uses velocity. Very slow.",
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
                        MK.Type: types.List,
                        MK.Description: "Delta pressure multiplied by cell volume, "
                        "which is a faster implementation.",
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
                        MK.Type: types.List,
                        MK.Description: "Calculates timeshift without using "
                        "velocity. The velocity is only used to get the surface "
                        "on the velocity grid. It uses a change in porevolume "
                        "from Eclipse (RPORV in .UNRST) as input to Geertsma model.",
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
