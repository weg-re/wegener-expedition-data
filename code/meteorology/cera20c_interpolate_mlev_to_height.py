# https://confluence.ecmwf.int/display/CKB/ERA5%3A+compute+pressure+and+geopotential+on+model+levels%2C+geopotential+height+and+geometric+height
# https://confluence.ecmwf.int/display/ECC/Compute+geopotential+on+model+levels


import xarray as xr
# coordindates station Eismitte (Band 4,1 p198)" 70°54'N, 40°42'W, H=3000m
station_north = 70.9
station_east = -40.7

ifile_mlevels = '/home/sscher/data/weg_re/cera20c/cera20c-193009_NH_mlevels.nc'
ifile_lsp = '/home/sscher/data/weg_re/cera20c/cera20c-193009_NH_lsp_mlevels.nc'

interpolation_method = 'linear'
data_mlevs = xr.open_dataset(ifile_mlevels)
data_lsp = xr.open_dataset(ifile_lsp)

data_mlevs = data_mlevs.interp(latitude=station_north, longitude=station_east, method='linear')
data_lsp = data_lsp.interp(latitude=station_north, longitude=station_east, method='linear')

data_mlevs['lnsp'] = data_lsp['lnsp']
data_mlevs.to_netcdf('merged_point.nc')

