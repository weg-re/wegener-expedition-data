"""

prperocesing of cera20c data:
from the downloaded grib files:
using  https://confluence.ecmwf.int/display/ECC/compute_geopotential_on_ml.py
python compute_geopotential_on_ml.py cera20c-193009_NH_tquv_mlevels.grib cera20c-193009_NH_zlnsp_mlevels.grib -o cera20c-193009_NH_height_of_mlevels.grib
grib_to_netcdf cera20c-193009_NH_height_of_mlevels.grib -o cera20c-193009_NH_height_of_mlevels.nc
grib_to_netcdf  cera20c-193009_NH_tquv_mlevels.grib -o cera20c-193009_NH_tquv_mlevels.nc -k 3

"""

import xarray as xr
import dask
from dask.diagnostics import ProgressBar

dask.config.set(**{'array.slicing.split_large_chunks': True})
pbar = ProgressBar()
pbar.register()


cera20c_path = '/mnt/qnap-storage/sscher/wegre/cera20c/'

dates = ['193008', '193009']

# t on model levels
ifiles_t = [f'{cera20c_path}/profiles/cera20c-{date}_NH_tquv_mlevels.nc' for date in dates]
# geopotential on mode levels
ifiles_z = [f'{cera20c_path}/profiles/cera20c-{date}_NH_height_of_mlevels.nc' for date in dates]

t = xr.open_mfdataset(ifiles_t)
z = xr.open_mfdataset(ifiles_z, combine='nested') # when not set to nested, error "ValueError: Coordinate variable time is neither monotonically increasing nor monotonically decreasing on all datasets"
# but manual checking showed that the time coordinates are actually monotonically increasing

lat = 71.183333  # 71°11'   39°56'  3010m
lon = -39.933333

t = t.interp(latitude=lat, longitude=lon)
z = z.interp(latitude=lat, longitude=lon)
# convert from geopotential to m
z = z / 9.81

# orography

orogfile = '/home/sscher/projects/wegre/data/cera20c-orography.nc'

orog = xr.open_dataset(orogfile)['z']
# convert from geopotential to m
orog = orog / 9.81
orog = orog.interp(latitude=lat, longitude=lon)
orog = orog.squeeze().values
combined = xr.Dataset({'t': t['t'], 'z': z['z'], 'z_abvsfc': z['z'] - orog})
combined.to_netcdf('data/cera20c_profiles_eismitte_mlevs.nc')
