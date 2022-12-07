"""
extract vertical profiles for eismitte station from ncep data
for 1930

"""

from pylab import plt
import xarray as xr
import pandas as pd
import seaborn as sns
import numpy as np
from dask.diagnostics import ProgressBar

pbar = ProgressBar()
pbar.register()

ncep_folder = '/home/sscher/data/weg_re/ncep/'

lat = 71.183333  # 71°11'   39°56'  3010m
lon = -39.933333
alt = 3010
# ncep works with 0-360 longitudes
if lon < 0:
    lon_ncep = 360 + lon
else:
    lon_ncep = lon

# hgt above surface data (goes from 12m to 500m). here the coordinate is height above surface!
print('reading hgtabvsfc')
ifile_mean = f'{ncep_folder}/mean/air.hgtAbvSfc.1930.nc'
ifile_spread = f'{ncep_folder}/spread/air.hgtAbvSfc.1930.nc'
ncep_hgtavbsfc = xr.open_dataset(ifile_mean)['air']
ncep_hgtavbsfc_spread = xr.open_dataset(ifile_spread)['air']
# combine
ncep_hgtavbsfc = xr.Dataset({'t': ncep_hgtavbsfc, 't_spread': ncep_hgtavbsfc_spread})
# extract eismitte point
ncep_hgtavbsfc = ncep_hgtavbsfc.interp(lat=lat, lon=lon_ncep)

# T2m
print('reading t2m')
ifile_mean = f'{ncep_folder}/mean/air.2m.1930.nc'
ifile_spread = f'{ncep_folder}/spread/air.2m.1930.nc'
ncep_t2m = xr.open_dataset(ifile_mean)['air']
ncep_t2m_spread = xr.open_dataset(ifile_spread)['air']
ncep_t2m = xr.Dataset({'t': ncep_t2m, 't_spread': ncep_t2m_spread})
ncep_t2m = ncep_t2m.interp(lat=lat, lon=lon_ncep)
# add level coordinate with value 2m
ncep_t2m = ncep_t2m.expand_dims(dim={'level': [2.]})

# combine t2m with hgtabovesfc
ncep = xr.concat([ncep_t2m, ncep_hgtavbsfc], dim='level')
# convert K to C
ncep['t'] = ncep['t'] - 273.15

# t on pressure levels
print('reading t on plev')
ifile_mean = f'{ncep_folder}/mean/air.1930.nc'
ifile_spread = f'{ncep_folder}/spread/air.1930.nc'
ncep_t_plev = xr.open_dataset(ifile_mean)['air'].interp(lat=lat, lon=lon_ncep)
ncep_t_plev_spread = xr.open_dataset(ifile_spread)['air'].interp(lat=lat, lon=lon_ncep)
# corresponding height (here we dont use the spread). this is absolute height, not above surface!
print('reading z on plev')
ifile_mean = f'{ncep_folder}/mean/hgt.1930.nc'
ncep_z_plev = xr.open_dataset(ifile_mean)['hgt'].interp(lat=lat, lon=lon_ncep)
# combine
ncep_plevs = xr.Dataset({'t': ncep_t_plev, 'z': ncep_z_plev, 't_spread': ncep_t_plev_spread})
ncep_plevs['t'] = ncep_plevs['t'] - 273.15

# orography
orog_ncep_file = f'{ncep_folder}/hgt.sfc.nc'
orog_ncep = xr.open_dataset(orog_ncep_file)['hgt']
orog_ncep = orog_ncep.interp(lat=lat, lon=lon_ncep)

# compute height above surface
ncep_plevs['z_abvsfc'] = ncep_plevs['z'] - orog_ncep.squeeze().values

# save
ncep.to_netcdf('data/ncep_profiles_eismitte_hgtlevs.nc')
ncep_plevs.to_netcdf('data/ncep_profiles_eismitte_plevs.nc')
