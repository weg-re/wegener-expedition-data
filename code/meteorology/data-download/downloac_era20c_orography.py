import os
import pandas as pd
from ecmwfapi import ECMWFDataServer

server = ECMWFDataServer()

outdir = '/mnt/qnap-storage/sscher/wegre/'

server.retrieve({
    "class": "ep",
    "dataset": "cera20c",
    "date": '19010101',
    "expver": "1",
    "levelist": "1",
    "levtype": "ml",
    "number": "0",
    "grid": "1/1",
    "param": "129",
    "area": "0/-180/90/180",
    "stream": "enda",
    "time": "00:00:00",
    "type": "an",
    "format": "netcdf",
    "target": f"{outdir}/cera20c-orography.nc",
})
