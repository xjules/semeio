import pytest
import datetime
from collections import namedtuple

from ecl.grid import EclGridGenerator
from ecl.util.geometry import Surface
import segyio

from semeio.jobs.ots import OTS
from ots_util import create_init, create_restart, create_segy_file

parms = namedtuple(
    "Parms",
    [
        "seabed",
        "above",
        "youngs",
        "poisson",
        "rfactor",
        "mapaxes",
        "convention",
        "output_dir",
        "horizon",
        "ascii",
        "velocity_model",
        "eclbase",
    ],
)


@pytest.fixture()
def setUp():
    spec = segyio.spec()
    spec.format = 5
    spec.sorting = 2
    spec.samples = range(0, 40, 4)
    spec.ilines = range(2)
    spec.xlines = range(2)

    actnum = [0, 0, 0, 0, 1, 1, 1, 1]

    parms.output_dir = None
    parms.horizon = None
    parms.ascii = None
    parms.velocity_model = None
    parms.seabed = 10
    parms.above = 10
    parms.youngs = 0.5
    parms.poisson = 0.3
    parms.rfactor = 20
    parms.convention = 1
    parms.eclbase = "TEST"

    yield spec, actnum, parms


@pytest.mark.usefixtures("setup_tmpdir")
def test_create(setUp):
    spec, actnum, parms = setUp
    grid = EclGridGenerator.createRectangular(dims=(10, 10, 10), dV=(1, 1, 1))

    create_init(grid, "TEST")

    with pytest.raises(IOError):
        OTS(
            parms.eclbase,
            parms.mapaxes,
            parms.seabed,
            parms.youngs,
            parms.poisson,
            parms.rfactor,
            parms.convention,
            parms.above,
            parms.velocity_model,
            verbose=False,
        )

    with pytest.raises(IOError):
        OTS(
            parms.eclbase,
            parms.mapaxes,
            parms.seabed,
            parms.youngs,
            parms.poisson,
            parms.rfactor,
            parms.convention,
            parms.above,
            parms.velocity_model,
            verbose=False,
        )

    grid = EclGridGenerator.createRectangular(dims=(10, 10, 10), dV=(1, 1, 1))

    create_init(grid, "TEST")
    create_restart(grid, "TEST")

    with pytest.raises(IOError):
        OTS(
            parms.eclbase,
            parms.mapaxes,
            parms.seabed,
            parms.youngs,
            parms.poisson,
            parms.rfactor,
            parms.convention,
            parms.above,
            parms.velocity_model,
            verbose=False,
        )

    grid = EclGridGenerator.createRectangular(dims=(10, 10, 10), dV=(1, 1, 1))
    grid.save_EGRID("TEST.EGRID")

    create_init(grid, "TEST")
    create_restart(grid, "TEST")

    parms.velocity_model = "missing.segy"

    with pytest.raises(IOError):
        OTS(
            parms.eclbase,
            parms.mapaxes,
            parms.seabed,
            parms.youngs,
            parms.poisson,
            parms.rfactor,
            parms.convention,
            parms.above,
            parms.velocity_model,
            verbose=False,
        )

    grid = EclGridGenerator.createRectangular(dims=(10, 10, 10), dV=(1, 1, 1))

    grid.save_EGRID("TEST.EGRID")
    create_init(grid, "TEST")
    create_restart(grid, "TEST")

    parms.velocity_model = "TEST.segy"
    create_segy_file(parms.velocity_model, spec)

    OTS(
        parms.eclbase,
        parms.mapaxes,
        parms.seabed,
        parms.youngs,
        parms.poisson,
        parms.rfactor,
        parms.convention,
        parms.above,
        parms.velocity_model,
        verbose=False,
    )


@pytest.mark.usefixtures("setup_tmpdir")
def test_eval(setUp):
    spec, actnum, parms = setUp
    grid = EclGridGenerator.createRectangular(
        dims=(2, 2, 2), dV=(100, 100, 100), actnum=actnum
    )

    grid.save_EGRID("TEST.EGRID")
    create_init(grid, "TEST")
    create_restart(grid, "TEST")

    parms.velocity_model = "TEST.segy"
    create_segy_file(parms.velocity_model, spec)

    ots = OTS(
        parms.eclbase,
        parms.mapaxes,
        parms.seabed,
        parms.youngs,
        parms.poisson,
        parms.rfactor,
        parms.convention,
        parms.above,
        parms.velocity_model,
        verbose=False,
    )
    with pytest.raises(ValueError):
        ots.add_survey("S1", datetime.date(2000, 1, 15))

    vintage_pairs = [(datetime.date(1900, 1, 1), datetime.date(2010, 1, 1))]

    with pytest.raises(ValueError):
        ots.geertsma_ts_simple(vintage_pairs)

    vintage_pairs = [(datetime.date(2010, 1, 1), datetime.date(1900, 1, 1))]

    with pytest.raises(ValueError):
        ots.geertsma_ts_simple(vintage_pairs)

    vintage_pairs = [(datetime.date(2000, 1, 1), None)]
    with pytest.raises(ValueError):
        ots.geertsma_ts_simple(vintage_pairs)

    vintage_pairs = [(datetime.date(2000, 1, 1), datetime.date(2010, 1, 1))]

    ots.geertsma_ts_simple(vintage_pairs)


@pytest.mark.usefixtures("setup_tmpdir")
def test_geertsma_TS_simple(setUp):
    spec, actnum, parms = setUp
    grid = EclGridGenerator.createRectangular(
        dims=(2, 2, 2), dV=(100, 100, 100), actnum=actnum
    )

    create_restart(grid, "TEST")
    create_init(grid, "TEST")
    grid.save_EGRID("TEST.EGRID")

    parms.velocity_model = "TEST.segy"

    l = [50, 150]
    create_segy_file(parms.velocity_model, spec, xl=l, il=l, cdp_x=l, cdp_y=l)

    ots = OTS(
        parms.eclbase,
        parms.mapaxes,
        parms.seabed,
        parms.youngs,
        parms.poisson,
        parms.rfactor,
        parms.convention,
        parms.above,
        parms.velocity_model,
        verbose=False,
    )

    vintage_pairs = [
        (datetime.date(2000, 1, 1), datetime.date(2010, 1, 1)),
        (datetime.date(2010, 1, 1), datetime.date(2011, 1, 1)),
    ]

    tshift = ots.geertsma_ts_simple(vintage_pairs)
    assert tshift[0][0] == pytest.approx(-0.01006, abs=0.0001)

    parms.convention = -1
    ots = OTS(
        parms.eclbase,
        parms.mapaxes,
        parms.seabed,
        parms.youngs,
        parms.poisson,
        parms.rfactor,
        parms.convention,
        parms.above,
        parms.velocity_model,
        verbose=False,
    )

    vintage_pairs = [
        (datetime.date(2000, 1, 1), datetime.date(2010, 1, 1)),
        (datetime.date(2010, 1, 1), datetime.date(2011, 1, 1)),
    ]

    tshift = ots.geertsma_ts_simple(vintage_pairs)
    assert tshift[0][0] == pytest.approx(0.01006, abs=0.0001)


@pytest.mark.usefixtures("setup_tmpdir")
def test_geertsma_TS_rporv(setUp):
    spec, actnum, parms = setUp
    grid = EclGridGenerator.createRectangular(
        dims=(2, 2, 2), dV=(100, 100, 100), actnum=actnum
    )

    create_restart(grid, "TEST", rporv=[10 for i in range(grid.getNumActive())])
    create_init(grid, "TEST")
    grid.save_EGRID("TEST.EGRID")

    parms.velocity_model = "TEST.segy"

    l = [50, 150]
    create_segy_file(parms.velocity_model, spec, xl=l, il=l, cdp_x=l, cdp_y=l)

    ots = OTS(
        parms.eclbase,
        parms.mapaxes,
        parms.seabed,
        parms.youngs,
        parms.poisson,
        parms.rfactor,
        parms.convention,
        parms.above,
        parms.velocity_model,
        verbose=False,
    )

    vintage_pairs = [
        (datetime.date(2000, 1, 1), datetime.date(2010, 1, 1)),
        (datetime.date(2010, 1, 1), datetime.date(2011, 1, 1)),
    ]

    tshift = ots.geertsma_ts_rporv(vintage_pairs)


@pytest.mark.usefixtures("setup_tmpdir")
def test_geertsma_TS(setUp):
    spec, actnum, parms = setUp
    grid = EclGridGenerator.createRectangular(
        dims=(2, 2, 2), dV=(100, 100, 100), actnum=actnum
    )

    create_restart(grid, "TEST")
    create_init(grid, "TEST")
    grid.save_EGRID("TEST.EGRID")

    parms.velocity_model = "TEST.segy"

    l = [50, 150]
    create_segy_file(parms.velocity_model, spec, xl=l, il=l, cdp_x=l, cdp_y=l)

    ots = OTS(
        parms.eclbase,
        parms.mapaxes,
        parms.seabed,
        parms.youngs,
        parms.poisson,
        parms.rfactor,
        parms.convention,
        parms.above,
        parms.velocity_model,
        verbose=False,
    )

    vintage_pairs = [
        (datetime.date(2000, 1, 1), datetime.date(2010, 1, 1)),
        (datetime.date(2010, 1, 1), datetime.date(2011, 1, 1)),
    ]

    tshift = ots.geertsma_ts(vintage_pairs)

    assert tshift[0][0] == pytest.approx(-0.00104, abs=0.0001)

    parms.convention = -1

    ots = OTS(
        parms.eclbase,
        parms.mapaxes,
        parms.seabed,
        parms.youngs,
        parms.poisson,
        parms.rfactor,
        parms.convention,
        parms.above,
        parms.velocity_model,
        verbose=False,
    )

    vintage_pairs = [
        (datetime.date(2000, 1, 1), datetime.date(2010, 1, 1)),
        (datetime.date(2010, 1, 1), datetime.date(2011, 1, 1)),
    ]

    tshift = ots.geertsma_ts(vintage_pairs)
    assert tshift[0][0] == pytest.approx(0.00104, abs=0.0001)


@pytest.mark.usefixtures("setup_tmpdir")
def test_dPV(setUp):
    spec, actnum, parms = setUp
    grid = EclGridGenerator.createRectangular(
        dims=(2, 2, 2), dV=(100, 100, 100), actnum=actnum
    )

    grid.save_EGRID("TEST.EGRID")
    create_restart(grid, "TEST")
    create_init(grid, "TEST")

    ots = OTS(
        parms.eclbase,
        parms.mapaxes,
        parms.seabed,
        parms.youngs,
        parms.poisson,
        parms.rfactor,
        parms.convention,
        parms.above,
        parms.velocity_model,
        verbose=False,
    )

    vintage_pairs = [
        (datetime.date(2000, 1, 1), datetime.date(2010, 1, 1)),
        (datetime.date(2010, 1, 1), datetime.date(2011, 1, 1)),
    ]

    tshift = ots.dpv(vintage_pairs)
    assert tshift[0][0] == pytest.approx(((20 - 10) * 1e6 + (0 - 0) * 1e6) / 1e9)
    assert tshift[0][2] == pytest.approx(((20 - 10) * 1e6 + (0 - 0) * 1e6) / 1e9)

    assert tshift[1][0] == pytest.approx(((25 - 20) * 1e6 + (0 - 0) * 1e6) / 1e9)
    assert tshift[1][2] == pytest.approx(((25 - 20) * 1e6 + (0 - 0) * 1e6) / 1e9)

    parms.convention = -1

    ots = OTS(
        parms.eclbase,
        parms.mapaxes,
        parms.seabed,
        parms.youngs,
        parms.poisson,
        parms.rfactor,
        parms.convention,
        parms.above,
        parms.velocity_model,
        verbose=False,
    )
    tshift_b_m = ots.dpv(vintage_pairs)
    assert tshift[0][0] == pytest.approx(-tshift_b_m[0][0])


@pytest.mark.usefixtures("setup_tmpdir")
def test_irap_surface(setUp):
    spec, actnum, parms = setUp
    grid = EclGridGenerator.createRectangular(
        dims=(2, 2, 2), dV=(100, 100, 100), actnum=actnum
    )

    # with TestAreaContext("test_irap_surface"):
    create_restart(grid, "TEST")
    create_init(grid, "TEST")
    grid.save_EGRID("TEST.EGRID")

    parms.velocity_model = "TEST.segy"
    create_segy_file(parms.velocity_model, spec)

    ots = OTS(
        parms.eclbase,
        parms.mapaxes,
        parms.seabed,
        parms.youngs,
        parms.poisson,
        parms.rfactor,
        parms.convention,
        parms.above,
        parms.velocity_model,
        verbose=False,
    )

    f_name = "irap.txt"
    s = ots._create_surface()
    s.write(f_name)
    s = Surface(f_name)

    assert s.getNX() == 2
    assert s.getNY() == 2

    for val in s:
        assert val == 90
