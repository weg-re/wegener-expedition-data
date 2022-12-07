# https://psl.noaa.gov/data/gridded/data.20thC_ReanV3.html
mkdir mean
cd mean
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/2mSI/air.2m.1930.nc
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/2mSI/air.2m.1931.nc
cd ..
mkdir spread
cd spread
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/spreads/2mSI/air.2m.1930.nc
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/spreads/2mSI/air.2m.1931.nc
# orography
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/timeInvariantSI/hgt.sfc.nc


# vertical
cd ../mean
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/hgt_above_sfcSI/air.hgtAbvSfc.1930.nc
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/prsSI/air.1930.nc
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/prsSI/hgt.1930.nc
cd ../spread
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/spreads/hgt_above_sfcSI/air.hgtAbvSfc.1930.nc
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/spreads/prsSI/air.1930.nc
wget https://downloads.psl.noaa.gov/Datasets/20thC_ReanV3/spreads/prsSI/hgt.1930.nc

