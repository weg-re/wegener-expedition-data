"""
to run this script, you need the ecmwf api (pip install ecmwf-api-client),
 and you need to have a free ecmwf account and keys setup.
see https://confluence.ecmwf.int/display/WEBAPI/Access+ECMWF+Public+Datasets

"""
import os
import pandas as pd
from ecmwfapi import ECMWFDataServer

server = ECMWFDataServer()

outdir = '/mnt/qnap-storage/sscher/wegre/cera20c/profiles/'
startdate = '1929-01-01'
enddate = '1931-01-31'
area = 'NH'

os.makedirs(outdir, exist_ok=True)

# startyear = 1929
# endyear = 1931
year = 1930
month=8 # 8|9
# for year in range(startyear, endyear + 1):
#     for month in range(1, 12 + 1):
daysinmonth = pd.Period(f'{year}-{month:02d}-01').daysinmonth
datestr = f'{year}{month:02d}01/to/{year}{month:02d}{daysinmonth:02d}'
print(datestr)

# model levels
server.retrieve({
    "class": "ep",
    "dataset": "cera20c",
    "date": datestr,
    "expver": "1",
    "levelist": "53/to/91", #91 are available, 91 is the lowest, 53 at ~10km",
    "levtype": "ml",
    "number": "0/1/2/3/4/5/6/7/8/9",
    "grid": "1/1",
    "param": "t/q/u/v",
    "area": "0/-180/90/180",
    "stream": "enda",
    "time": "00:00:00/03:00:00/06:00:00/09:00:00/12:00:00/15:00:00/18:00:00/21:00:00",
    "type": "an",
    "target": f"{outdir}/cera20c-{year}{month:02d}_{area}_tquv_mlevels.grib",
})
# log of surface pressore
server.retrieve({
    "class": "ep",
    "dataset": "cera20c",
    "date": datestr,
    "expver": "1",
    "levelist": "1",
    "levtype": "ml",
    "number": "0/1/2/3/4/5/6/7/8/9",
    "grid":"1/1",
    "param": "lnsp/z",
    "area": "0/-180/90/180",
    "stream": "enda",
    "time": "00:00:00/03:00:00/06:00:00/09:00:00/12:00:00/15:00:00/18:00:00/21:00:00",
    "type": "an",
    "target": f"{outdir}/cera20c-{year}{month:02d}_{area}_zlnsp_mlevels.grib",
})