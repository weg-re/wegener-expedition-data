"""
plot prfiles with data from extract_ncep_profiles.py
and with 'data-wegener/soundings/eismitte-soundings.csv'



ncep is in UTC. I assume that wegener is in CET.

"""
import string
import xarray as xr
import pandas as pd
import numpy as np
from pylab import plt
import seaborn as sns

ncep = xr.open_dataset('data/ncep_profiles_eismitte_hgtlevs.nc')
ncep_plevs = xr.open_dataset('data/ncep_profiles_eismitte_plevs.nc')

cera20c = xr.open_dataset('data/cera20c_profiles_eismitte_mlevs.nc')
cera20c['t'] = cera20c['t'] - 273.15

# shift to MEZ (CET)
ncep['time'] = ncep['time'] + pd.to_timedelta('1h')
ncep_plevs['time'] = ncep_plevs['time'] + pd.to_timedelta('1h')

# read wegener measurements
ifile_wegener = 'data-wegener/soundings/eismitte-soundings.csv'
wegener = pd.read_csv(ifile_wegener)
# in the data, p is in mm Hg
# convert to hPa
wegener['p'] = 1.3332 * wegener['p']

# proifle Nr5 doesnt have any height information, so we drop it
wegener = wegener[wegener['Nr'] != 5]

colors = sns.color_palette('colorblind', 3)
colors[2] = 'black'
sns.set(style='ticks', font_scale=1.25)
plt.rcParams['grid.color'] = '.6'
plt.rcParams['grid.linestyle'] = ':'
plt.rcParams['lines.markersize'] = 10
plt.figure(figsize=(14, 8))
for iplot, nr in enumerate(wegener['Nr'].unique()):
    profile_wegener = wegener.query("Nr==@nr")
    # we only need Nr,date, T and H, the rest we drop, and we drop all
    # columsn where T or H are nan
    profile_wegener = profile_wegener[['Nr', 'date', 'time', 'T', 'H']]
    profile_wegener = profile_wegener.dropna()

    assert (len(profile_wegener['date'].unique() == 1))
    date = profile_wegener['date'].iloc[0]
    # we use starting time as reference
    time_wegener = profile_wegener['time'].iloc[0]
    datetime_wegener = pd.to_datetime(date + '-' + time_wegener, format="%d.%m.%Y-%Hh%M")
    # get closest time in reanalysis
    profile_ncep = ncep.interp(time=datetime_wegener, method='nearest')
    profile_ncep_plevs = ncep_plevs.interp(time=datetime_wegener, method='nearest')

    # combine both ncep profiles. use the one obtained from plev data from 500m on (500m is the highest
    # from the height data)
    lowest_plev_idx_above_500 = (profile_ncep_plevs['z_abvsfc'] > 500).argmax()
    profile_ncep_plevs = profile_ncep_plevs.isel(level=slice(lowest_plev_idx_above_500.values, None))
    # replace the old level values (hpa) with the height
    profile_ncep_plevs['level'] = profile_ncep_plevs['z_abvsfc']
    # combine
    profile_ncep = xr.concat([profile_ncep, profile_ncep_plevs], dim='level')

    # cera20c
    profile_cera20c = cera20c.interp(time=datetime_wegener, method='nearest')
    profile_cera20c['t_mean'] = profile_cera20c['t'].mean('number')
    profile_cera20c['t_spread'] = profile_cera20c['t'].std('number')

    marker = '*'
    plt.subplot(2, 3, iplot + 1)
    plt.plot(profile_cera20c['t_mean'], profile_cera20c['z_abvsfc'], label='CERA-20C', marker=marker,
             color=colors[0])
    plt.fill_betweenx(profile_cera20c['z_abvsfc'], profile_cera20c['t_mean'] - profile_cera20c['t_spread'],
                      profile_cera20c['t_mean'] + profile_cera20c['t_spread'],
                      color=colors[0], alpha=0.6)
    # plot indivudial members
    for number in profile_cera20c['number']:
        plt.plot(profile_cera20c.sel(number=number)['t'], profile_cera20c['z_abvsfc'], linewidth=1, linestyle='--',
                 color=colors[0])

    plt.plot(profile_ncep['t'], profile_ncep['level'], label='20CRv3', marker=marker,
             color=colors[1])
    plt.fill_betweenx(profile_ncep['level'], profile_ncep['t'] - profile_ncep['t_spread'],
                      profile_ncep['t'] + profile_ncep['t_spread'],
                      color=colors[1], alpha=0.6)

    plt.plot(profile_wegener['T'], profile_wegener['H'], label='Wegener', marker=marker,
             color=colors[2])

    hmin = -20
    hmax = 1500
    plt.ylim(hmin, hmax)
    # compute the corresponding xlims
    ncep_visible_values = profile_ncep.where((profile_ncep['level'] < hmax) & (profile_ncep['level'] > 0))
    cera20c_visible_values = profile_cera20c.where(
        (profile_cera20c['z_abvsfc'] < hmax) & (profile_cera20c['z_abvsfc'] > 0))
    # while still not all cera20c data was ready
    xmin = np.min(((ncep_visible_values['t'] - ncep_visible_values['t_spread']).min(),
                   (cera20c_visible_values['t_mean'] - cera20c_visible_values['t_spread']).min(),
                   np.min(profile_wegener['T'])))
    xmax = np.max(((ncep_visible_values['t'] + ncep_visible_values['t_spread']).max(),
                   (cera20c_visible_values['t_mean'] + cera20c_visible_values['t_spread']).max(),
                   np.max(profile_wegener['T'])))
    plt.xlim(xmin - 1, xmax + 1)
    plt.xlabel('T [°C]')
    plt.ylabel('heigh above ground [m]')
    plt.legend()
    sns.despine()
    plt.grid(True)
    plt.title(f'{datetime_wegener} CET')
    # alphabetical subplot labels
    plt.text(-0.1, 1.05, string.ascii_lowercase[iplot], transform=plt.gca().transAxes,
             fontdict={'size': 18, 'weight': 'bold'})
plt.tight_layout(pad=0.4)

plt.savefig(f'plots/eismitte_profiles_vs_reanalysis.svg', bbox_inches='tight')
plt.savefig(f'plots/eismitte_profiles_vs_reanalysis.png', bbox_inches='tight', dpi=300)
