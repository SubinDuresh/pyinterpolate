import numpy as np
import geopandas as gpd
from pyinterpolate.data_processing.data_preparation.get_points_within_area import get_points_within_area
from pyinterpolate.data_processing.data_preparation.prepare_areal_shapefile import prepare_areal_shapefile

from pyinterpolate.semivariance.areal_semivariance.areal_semivariance import ArealSemivariance


def test_areal_semivariance():
    # Data prepration
    areal_dataset = 'sample_data/test_areas_pyinterpolate.shp'
    subset = 'sample_data/test_points_pyinterpolate.shp'

    a_id = 'id'
    areal_val = 'value'
    points_val = 'value'

    # Get maximum range and set step size

    gdf = gpd.read_file(areal_dataset)

    total_bounds = gdf.geometry.total_bounds
    total_bounds_x = np.abs(total_bounds[2] - total_bounds[0])
    total_bounds_y = np.abs(total_bounds[3] - total_bounds[1])

    max_range = min(total_bounds_x, total_bounds_y)
    step_size = max_range / 8
    lags = np.arange(0, max_range, step_size * 2)

    areal_data_prepared = prepare_areal_shapefile(areal_dataset, a_id, areal_val)
    points_in_area = get_points_within_area(areal_dataset, subset, areal_id_col_name=a_id,
                                            points_val_col_name=points_val)

    # Set areal semivariance class
    areal_semivariance = ArealSemivariance(areal_data_prepared, lags, step_size,
                                           points_in_area)
    output = areal_semivariance.regularize_semivariogram()
    test_d = output[:, 1].astype(np.int)
    correct_output = np.array([0, 0, 245, 205])
    assert (test_d == correct_output).all()


if __name__ == '__main__':
    test_areal_semivariance()
