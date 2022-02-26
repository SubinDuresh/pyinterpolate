import geopandas as gpd
import numpy as np
import pandas as pd

from geopandas import points_from_xy


def read_txt(
        path: str, lon_col_pos=0, lat_col_pos=1, val_col_pos=2, delim=',', skip_header=True, epsg='4326', crs=None
) -> gpd.GeoDataFrame:
    """Function reads data from a text file.

    Provided data format should include: longitude (x), latitude (y), value. You should provide crs or epsg,
    if it's not provided then epsg:4326 is used as a default value (https://epsg.io/4326).
    Data read by a function is converted into GeoDataFrame.

    Parameters
    ----------
    path : str
           Path to the file.

    lon_col_pos : int, default=0
                  Position of the longitude column.

    lat_col_pos : int, default=1
                  Position of the latitude column.

    val_col_pos : int, default=2
                  Position of the value column.

    delim : str, default=','
            Delimiter that separates columns.

    skip_header : bool, default=True
                  Skips the first row of a file if set to True.

    epsg : str, optional, default='epsg:4326'
           Sets epsg for a given dataset.

    crs : str or None, optional, default=None
          Sets CRS for a given dataset. If not None then it overwrites EPSG.

    Returns
    -------
    gdf : GeoDataFrame

    Examples
    --------
    >>> path_to_the_data = 'path_to_the_data.txt'
    >>> data = read_txt(path_to_the_data, skip_header=False)
    >>> print(data.head(2))
    +---+---------------------------+-----------+
    |   |         geometry          |   value   |
    +---+---------------------------+-----------+
    | 0 | POINT (15.11524 52.76515) | 91.275597 |
    | 1 | POINT (15.11524 52.74279) | 96.548294 |
    +---+---------------------------+-----------+
    """

    data_arr = np.loadtxt(path, delimiter=delim)

    if skip_header:
        data_arr = data_arr[1:, :]

    gdf = gpd.GeoDataFrame(data=data_arr)
    gdf['geometry'] = points_from_xy(gdf[lon_col_pos], gdf[lat_col_pos])
    gdf.set_geometry('geometry', inplace=True)

    if crs is None:
        gdf.set_crs(epsg=epsg, inplace=True)
    else:
        gdf.set_crs(crs=crs, inplace=True)

    gdf = gdf[['geometry', val_col_pos]]
    gdf.columns = ['geometry', 'value']

    return gdf


def read_csv(
        path: str,
        val_col_name: str,
        lat_col_name: str,
        lon_col_name: str,
        delim=',',
        epsg=4326,
        crs=None
) -> gpd.GeoDataFrame:
    """Function reads data from a csv file.

    Provided data format should include: latitude, longitude, value. You should provide crs or epsg,
    if it's not provided then epsg:4326 is used as a default value (https://epsg.io/4326).
    Data read by a function is converted into GeoDataFrame.

    Parameters
    ----------

    path : str
           Path to the file.

    val_col_name : str
                   Name of the value column (header title).

    lat_col_name : str
                   Name of the latitude column (header title).

    lon_col_name : str
                   Name of the longitude column (header title).

    delim : str, default=','
            Delimiter that separates columns.

    epsg : str, optional, default='epsg:4326'
           Sets epsg for a given dataset.

    crs : str or None, optional, default=None
          Sets CRS for a given dataset. If not None then it overwrites EPSG.

    Returns
    -------

    gdf : GeoDataFrame

    Examples
    --------
    >>> path_to_the_data = 'path_to_the_data.csv'
    >>> data = read_csv(path_to_the_data, val_col_name='value', lat_col_name='y', lon_col_name='x')
    >>> print(data.head(2))
    +---+---------------------------+-----------+
    |   |         geometry          |   value   |
    +---+---------------------------+-----------+
    | 0 | POINT (15.11524 52.76515) | 91.275597 |
    | 1 | POINT (15.11524 52.74279) | 96.548294 |
    +---+---------------------------+-----------+
    """

    df = pd.read_csv(
        path, sep=delim
    )

    gdf = gpd.GeoDataFrame(df[[val_col_name, lat_col_name, lon_col_name]])

    # Very low possibility but check if there is a geometry column in the data
    if 'geometry' in gdf.columns:
        geometry_col_name = '_geometry'
    else:
        geometry_col_name = 'geometry'

    gdf[geometry_col_name] = points_from_xy(gdf[lon_col_name], gdf[lat_col_name])
    gdf.set_geometry(geometry_col_name, inplace=True)

    if crs is None:
        gdf.set_crs(epsg=epsg, inplace=True)
    else:
        gdf.set_crs(crs=crs, inplace=True)

    gdf = gdf[[geometry_col_name, val_col_name]]
    gdf.columns = ['geometry', 'value']

    return gdf


def read_block(
        path: str,
        val_col_name: str,
        geometry_col_name='geometry',
        id_col_name=None,
        centroid_col_name=None,
        epsg=None,
        crs=None
) -> gpd.GeoDataFrame:
    """Function reads block data from files supported by fiona / geopandas.

    Value column name must be provided. If geometry column has different name than 'geometry' then
    it must be provided too. ID column name is optional, if not given then GeoDataFrame index is
    treated as an id column. Optional parameters are epsg and crs. If any is set then data is reprojected
    into a specific crs/epsg. Function return GeoDataFrame with columns: id, value, geometry, centroid.

    Parameters
    ----------
    path : str
           Path to the file.

    val_col_name : str
                   Name of the value column (header title).

    geometry_col_name : str, default='geometry'
                        Name of the column with blocks - polygons.

    id_col_name: str or None, default=None, optional
                 Name of the colum with unique indexes.


    centroid_col_name: str or None, default=None, optional
                       Name of the column with block centroid. Centroids are calculated
                       from MultiPolygons or Polygons later on but their accuracy may be limited.
                       For most applications it does not matter.

    epsg : str or None, default=None, optional
           If provided then GeoDataFrame projection is set to it. You should choose if you provide EPSG or CRS.

    crs : str or None, default=None, optional
          If provided then GeoDataFrame projection is set to. You should choose if you provide CRS or EPSG.

    Returns
    -------
    gpd : GeoDataFrame
          columns=['id', 'geometry', 'value', 'centroid']

    Raises
    ------
    TypeError
        - EPSG and CRS are provided both (should be one),
        - Provided column name does not exist in a dataset.

    Examples
    --------
    >>> bblock = 'path_to_the_shapefile.shp'
    >>> bdf = read_block(bblock, val_col_name='rate', id_col_name='id')
    >>> print(bdf.columns)
    Index(['id', 'geometry', 'rate', 'centroid'], dtype='object')
    """

    # INPUT TESTS

    # Check if id column is given
    if id_col_name is not None:
        columns = [id_col_name, geometry_col_name, val_col_name]
    else:
        columns = [geometry_col_name, val_col_name]

    # Check if crs | epsg is set that minimum one of those values is None
    check_geometry_params = np.array([True if x is None else False for x in [crs, epsg]]).any()
    if check_geometry_params:
        pass
    else:
        raise TypeError(f'Only one value CRS or EPSG should be provided but both are given: crs {crs}; epsg: {epsg}')

    # FUNCTION'S BODY

    gdf = gpd.read_file(path)

    # Check if columns exist
    gdf_cols = gdf.columns
    for c in columns:
        if c not in gdf_cols:
            raise TypeError(f'Given column {c} is not present in a dataset. Available columns: {gdf_cols}')

    ndf = gdf[columns].copy()
    ndf.geometry = ndf[geometry_col_name]

    # Check crs and epsg
    if (crs is not None) or (epsg is not None):
        if ndf.crs is None:
            ndf.set_crs(crs=crs, epsg=epsg, inplace=True)
        else:
            ndf.to_crs(crs=crs, epsg=epsg, inplace=True)

    # Get centroids
    c_col_name = 'centroid'
    if centroid_col_name is None:
        ndf[c_col_name] = ndf.centroid
    else:
        ndf[c_col_name] = gdf[centroid_col_name]

    # Add id column if not given
    if id_col_name is None:
        id_col_name = 'id'
        ndf[id_col_name] = ndf.index

    # Set columns
    output = ndf[[id_col_name, geometry_col_name, val_col_name, c_col_name]]

    return output
