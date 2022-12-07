
yearmonth=193008

python compute_geopotential_on_ml.py cera20c-${yearmonth}_NH_tquv_mlevels.grib cera20c-${yearmonth}_NH_zlnsp_mlevels.grib -o cera20c-${yearmonth}_NH_height_of_mlevels.grib
grib_to_netcdf cera20c-${yearmonth}_NH_height_of_mlevels.grib -o cera20c-${yearmonth}_NH_height_of_mlevels.nc
grib_to_netcdf  cera20c-${yearmonth}_NH_tquv_mlevels.grib -o cera20c-${yearmonth}_NH_tquv_mlevels.nc -k 3
