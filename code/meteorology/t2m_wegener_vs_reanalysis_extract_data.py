"""
read in wegener station data
read in cera20c t2m ensemble data
read in ncep 20th century reanalysis mean and spread
optionally: apply height correction
compute daily mean of reanalysis same way as wegener

input: data downloaded with
    data-download/download_ncep_reanalysis.sh
    data-download/downloac_era20c_t2m.py
    data-download/downloac_era20c_orography.py

daymean in wegener data (Band4,1 p412): measured 3 times daily (8h, 14h, 21h MEZ (UTC+1))
mean = (2*8h+2*14h+5*21h)/9

in UTC: 7, 13, 20
reanalysis: utc, 0,3,6,9,12,15,18,21

closest match: using 6,12,21 from reanalysis, and apply same weighting as wegener
reanalysis mean=(2*6h+2*12h+5*21h)/9

output: .csv file with all data for both stations


NOTE: this script generates a lot of FutureWarnings . be carefuel if you use it in the future with new library versions

@author: Sebastian Scher, Nov 2022

"""

import pandas as pd
import xarray as xr
import seaborn as sns
from pylab import plt
import dask
import numpy as np
from dask.diagnostics import ProgressBar

dask.config.set(**{'array.slicing.split_large_chunks': True})
pbar = ProgressBar()
pbar.register()

wegenerfile = 'data-wegener/stations/dig_met_data.xlsx'

wegdata = pd.read_excel(wegenerfile)

cera20c_folder = '/home/sscher/data/weg_re/cera20c/'
ncep_folder = '/home/sscher/data/weg_re/ncep/'

station_coords = {
    'AT_Weststation': {'lat': 71.2, 'lon': -51.133333, 'alt': 940
                       },
    'AT_Qameruj': {'lat': 71.140556, 'lon': -51.128333, 'alt': 0},
}

interp_method = 'linear'  # nearest | linear
height_correction = True

res_df = []

for station in ('AT_Qameruj', 'AT_Weststation'):

    lat = station_coords[station]['lat']
    lon = station_coords[station]['lon']

    # cera20c
    ifiles = [f'{cera20c_folder}/cera20c-{year}{month:02d}_NH_t2m.nc' for year in
              range(1930, 1931 + 1) for month in range(1, 12 + 1)]
    orogfile = f'{cera20c_folder}/cera20c-orography.nc'

    cera20c = xr.open_mfdataset(ifiles)
    orog = xr.open_dataset(orogfile)['z']
    # convert from geopotential to m
    orog = orog / 9.81
    cera20c = cera20c.interp(latitude=lat, longitude=lon, method=interp_method)
    orog = orog.interp(latitude=lat, longitude=lon, method=interp_method)
    cera20c = cera20c['t2m']
    # K to C
    cera20c = cera20c - 273.15

    ## ncep reanalysis
    ifiles_mean = [f'{ncep_folder}/mean/air.2m.{year}.nc' for year in range(1930, 1931 + 1)]
    ifiles_spread = [f'{ncep_folder}/spread/air.2m.{year}.nc' for year in range(1930, 1931 + 1)]
    orog_ncep_file = f'{ncep_folder}/hgt.sfc.nc'
    ncep_mean = xr.open_mfdataset(ifiles_mean)['air']
    ncep_spread = xr.open_mfdataset(ifiles_spread)['air']

    orog_ncep = xr.open_dataset(orog_ncep_file)['hgt']

    # ncep works with 0-360 longitudes
    if lon < 0:
        lon_ncep = 360 + lon
    else:
        lon_ncep = lon
    ncep_mean = ncep_mean.interp(lat=lat, lon=lon_ncep, method=interp_method)
    ncep_spread = ncep_spread.interp(lat=lat, lon=lon_ncep, method=interp_method)
    orog_ncep = orog_ncep.interp(lat=lat, lon=lon_ncep, method=interp_method)

    ncep_mean = ncep_mean - 273.15
    cera20c.load()
    ncep_mean.load()
    ncep_spread.load()

    x = cera20c
    x = (2 * x[x.time.dt.hour == 6] + 2 * x[x.time.dt.hour == 12].data + 5 * x[x.time.dt.hour == 21].data) / 9
    # datetime is now from hour 6, set hour to zero by shifting 6 hours
    x['time'] = x['time'] + pd.to_timedelta(-6, unit='hours')
    cera20c = x
    x = ncep_mean
    x = (2 * x[x.time.dt.hour == 6] + 2 * x[x.time.dt.hour == 12].data + 5 * x[x.time.dt.hour == 21].data) / 9
    # datetime is now from hour 6, set hour to zero by shifting 6 hours
    x['time'] = x['time'] + pd.to_timedelta(-6, unit='hours')
    ncep_mean = x
    x = ncep_spread
    x = (2 * x[x.time.dt.hour == 6] + 2 * x[x.time.dt.hour == 12].data + 5 * x[x.time.dt.hour == 21].data) / 9
    # datetime is now from hour 6, set hour to zero by shifting 6 hours
    x['time'] = x['time'] + pd.to_timedelta(-6, unit='hours')
    ncep_spread = x

    # height correction
    if height_correction:
        z_model = orog.squeeze().data
        z_station = station_coords[station]['alt']
        delta_T = (z_model - z_station) / 1000 * 6.5  # correction with 6.5K/km
        print(f'cera20c: correcting height difference of {z_station - z_model}m with {delta_T}K')
        cera20c = cera20c + delta_T

        z_model = orog_ncep.squeeze().data
        z_station = station_coords[station]['alt']
        delta_T = (z_model - z_station) / 1000 * 6.5  # correction with 6.5K/km
        print(f'cera20c: correcting height difference of {z_station - z_model}m with {delta_T}K')
        ncep_mean = ncep_mean + delta_T

    mean = cera20c.mean('number')
    qs = [0, 0.25, 0.75, 1]
    ceramax = cera20c.max('number')
    ceramin = cera20c.min('number')
    spread = cera20c.std('number')

    # convert to dataframe
    df = pd.DataFrame({'date':mean['time'], 'cera20c':mean, 'ncep':ncep_mean, 'cera20c_spread':spread,
                       'ncep_spread':spread})

    # add station data, filling in nan for the dates that are not available
    df['wegener'] = wegdata.set_index('date').reindex(pd.DatetimeIndex(df.date))[station].values

    df['station'] = station
    res_df.append(df)

res_df = pd.concat(res_df)
res_df.to_csv(f'data/wegener_ncep_cera20c_bothstations_{interp_method}.csv', index=False)

