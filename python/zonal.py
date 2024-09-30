import numpy as np
import pandas as pd

#' Sanitize Column Inclusions
#' @param exe executed zonal product
#' @param drop colnames to drop from table
#' @return DataFrame
def sanitize(exe, drop=None):
    if drop is None:
        drop = []

    drop += ["cell", "coverage_fraction"]
    drop = [col for col in drop if col in exe.columns]

    exe.drop(columns=drop, inplace=True)
    return exe


#' Prep Incoming Data
#' @param data raster, file path, or numpy array
#' @param subds subdatasets
#' @return raster or numpy array
def prep_input(data, subds=0, lyrs=None, win=None):
    if isinstance(data, np.ndarray):  # Assuming numpy array as the raster object
        if lyrs is None and subds == 0:
            lyrs = data.shape[0]  # If layers not provided, consider the first dimension

        if win is None:
            r = data
        else:
            r = data[win]  # Assuming win is a slicing window

    if subds != 0:
        r = r[subds]

    return r


#' Prep Geometry
#' @param geom geometry object or file path
#' @param crs coordinate reference system
#' @return geometry object
def prep_geom(geom, crs=None):
    if not isinstance(geom, pd.DataFrame):  # Assuming DataFrame for spatial geometries
        geom = pd.DataFrame(geom)  # Converting geom to DataFrame

    if crs is not None:
        geom['crs'] = crs  # Projecting geom (simplified for the example)
    
    return geom


#' Execute Zonal Stats
#' 
#' @param data raster or file path
#' @param geom geometry object with polygonal geometries
#' @param w a weight grid (produced with weight_grid)
#' @param ID the grouping ID
#' @param fun an optional function or character vector, as described below
#' @param subds subdatasets
#' @param na_rm remove NA values?
#' @param progress if True, display a progress bar during processing
#' @param join if True the geometry will be joined to the results
#' @param drop colnames to drop from table
#' @return DataFrame
def execute_zonal(data=None, 
                  geom=None, 
                  w=None, 
                  ID=None, 
                  fun=np.mean, 
                  subds=0, 
                  progress=False,
                  join=True,
                  drop=None,
                  **kwargs):
    
    if data is None:
        raise ValueError("`data` cannot be left None")
    if ID is None:
        raise ValueError("`ID` cannot be left None")
    if geom is None and w is None:
        raise ValueError("`geom` and `w` cannot both be None")

    exe = []
    data = [data] if not isinstance(data, list) else data

    n = [data[i].shape[0] for i in range(len(data))]

    ee = False if any(np.array(n) > 5) else True
    
    if w is not None:
        ee = False

    if ee:
        for i in range(len(data)):
            exe.append(zone_by_ee(data=data[i], geom=geom, ID=ID, fun=fun, subds=subds, progress=progress, join=False, **kwargs))
    else:
        if w is None:
            w = weight_grid(prep_input(data[0], subds=0, win=None), geom, ID, progress)

        for i in range(len(data)):
            exe.append(zone_by_weights(data=prep_input(data[i], subds=0, win=None), w=w, ID=ID, fun=fun, **kwargs))

    if join and geom is not None:
        exe = pd.merge(geom, exe, on=ID)

    for i in range(len(exe)):
        exe[i] = sanitize(exe[i], drop=drop)

    return exe[0] if len(exe) == 1 else exe

# Placeholder functions to simulate behavior
def zone_by_ee(data, geom, ID, fun, subds, progress, join, **kwargs):
    # Placeholder function for zone by ee
    pass

def zone_by_weights(data, w, ID, fun, **kwargs):
    # Placeholder function for zone by weights
    pass

def weight_grid(data, geom, ID, progress):
    # Placeholder function for weight_grid
    pass
