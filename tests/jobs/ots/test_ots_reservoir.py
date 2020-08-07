import numpy as np
from semeio.jobs.ots.ots_res_surface import OTSResSurface
from ecl.grid import EclGrid, EclGridGenerator
import os
import pytest


def get_source_ert(grid):
    x = np.zeros(grid.getNumActive(), np.float64)
    y = np.zeros(grid.getNumActive(), np.float64)
    z = np.zeros(grid.getNumActive(), np.float64)
    v = np.zeros(grid.getNumActive(), np.float64)
    for i in range(grid.getNumActive()):
        (x[i], y[i], z[i]) = grid.get_xyz(active_index=i)
        v[i] = grid.cell_volume(active_index=i)

    return x, y, z, v


def test_res_surface(ots_tmpdir_enter):
    eclcase_dir = ots_tmpdir_enter
    grid_path = os.path.join(eclcase_dir, "NORNE_ATW2013.EGRID")
    grid = EclGrid(grid_path, apply_mapaxes=False)

    rec = OTSResSurface(grid=grid, above=100)

    assert rec.nx == 46
    assert rec.ny == 112

    assert 453210.38 == pytest.approx(np.min(rec.x))
    assert 465445.16 == pytest.approx(np.max(rec.x))

    assert 7316018.5 == pytest.approx(np.min(rec.y))
    assert 7330943.5 == pytest.approx(np.max(rec.y))

    assert 2177.6484 == pytest.approx(np.min(rec.z))
    assert 3389.567 == pytest.approx(np.max(rec.z))


def test_surface(tmpdir):
    grid = EclGridGenerator.createRectangular(
        dims=(2, 2, 2), dV=(100, 100, 100), actnum=[0, 0, 0, 0, 1, 1, 1, 1]
    )

    surface = OTSResSurface(grid=grid)

    z = np.ones(4) * 100
    assert np.all(z == surface.z)


def test_surface_above(tmpdir):
    grid = EclGridGenerator.createRectangular(
        dims=(2, 2, 2), dV=(100, 100, 100), actnum=[0, 0, 0, 0, 1, 1, 1, 1]
    )

    surface = OTSResSurface(grid=grid, above=10)

    z = np.ones(4) * (100 - 10)
    assert np.all(z == surface.z)
