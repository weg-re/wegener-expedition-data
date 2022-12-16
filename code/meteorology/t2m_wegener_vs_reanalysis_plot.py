"""

@author: Sebastian Scher, Nov 2022

"""

import pandas as pd
import xarray as xr
import seaborn as sns
from pylab import plt
import numpy as np

interp_method = 'linear'
ifile = f'data/wegener_ncep_cera20c_bothstations_{interp_method}.csv'

df = pd.read_csv(ifile, index_col=False)
df['date'] = pd.to_datetime(df['date'])

colors = sns.color_palette('colorblind', 3)
colors[2] = 'black'
sns.set(style='ticks', font_scale=1.25)
plt.rcParams['grid.color'] = '.6'
plt.rcParams['grid.linestyle'] = ':'
plt.figure(figsize=(9, 8))
for iplot, station in enumerate(('AT_Qameruj', 'AT_Weststation')):
    plt.subplot(2, 1, iplot + 1)
    sub = df[df['station'] == station]
    x = sub['date']
    plt.plot(x, sub['cera20c'], c=colors[0], label='CERA-20C')
    plt.fill_between(x, sub['cera20c'] - sub['cera20c_spread'], sub['cera20c'] + sub['cera20c_spread'],
                     alpha=0.6,
                     color=colors[0])
    plt.plot(x, sub['ncep'], c=colors[1], label='20CRv3')
    plt.fill_between(x, sub['ncep'] - sub['ncep_spread'], sub['ncep'] + sub['ncep_spread'], alpha=0.6,
                     color=colors[1])

    plt.plot(x, sub['wegener'], c=colors[2], label='Wegener')
    plt.xlim(pd.to_datetime('19300601'), pd.to_datetime('19311001'))
    plt.legend()
    plt.grid(True)
    plt.ylabel('T2m [°C]')
    sns.despine()
    if station == 'AT_Qameruj':
        plt.title('FS')
    elif station == 'AT_Weststation':
        plt.title('WS')
    else:
        raise Exception

plt.savefig(f'plots/wegener_vs_cera20c_{interp_method}.svg', bbox_inches='tight')
plt.savefig(f'plots/wegener_vs_cera20c_{interp_method}.png', bbox_inches='tight')

# rolling standard deviation
plt.figure(figsize=(9, 8))
for iplot, station in enumerate(('AT_Qameruj', 'AT_Weststation')):
    plt.subplot(2, 1, iplot + 1)
    sub = df[df['station'] == station]
    x = sub['date']
    # compute rolling standard deviation
    window = 10
    sub = sub.rolling(window).std()
    plt.plot(x, sub['cera20c'], c=colors[0], label='CERA-20C')
    plt.plot(x, sub['ncep'], c=colors[1], label='20CRv3')
    plt.plot(x, sub['wegener'], c=colors[2], label='Wegener')
    plt.xlim(pd.to_datetime('19300601'), pd.to_datetime('19311001'))
    plt.legend()
    plt.grid(True)
    plt.ylabel(f'{window} day running standard \n deviation [°C]')
    sns.despine()
    if station == 'AT_Qameruj':
        plt.title('FS')
    elif station == 'AT_Weststation':
        plt.title('WS')
    else:
        raise Exception

plt.savefig(f'plots/wegener_vs_cera20c_running_stdev{interp_method}.svg', bbox_inches='tight')
plt.savefig(f'plots/wegener_vs_cera20c_running_stdev{interp_method}.png', bbox_inches='tight')

# scatterplot with error bars

plt.figure(figsize=(4, 8))
for iplot, station in enumerate(('AT_Qameruj', 'AT_Weststation')):
    plt.subplot(2, 1, iplot + 1)
    sub = df[df['station'] == station]
    r2_cera20c = sub.corr()['cera20c']['wegener'] ** 2
    r2_ncep = sub.corr()['ncep']['wegener'] ** 2
    # remove all nans
    nona = sub.dropna().copy()
    # nona.loc[:,'doy'] = nona['date'].dt.dayofyear
    #
    # plt.scatter(nona['wegener'], nona['cera20c'], marker="x", s=4,
    #              c=nona['date'].dt.dayofyear,
    #              alpha=0.8, label=f'cera20c $r^2={r2_cera20c:.2f}$')
    plt.errorbar(nona['wegener'], nona['cera20c'], xerr=nona['cera20c_spread'], fmt="x", elinewidth=1, markersize=4,
                 color=colors[0],
                 alpha=0.8, label=f'CERA-20C $r^2={r2_cera20c:.2f}$')
    plt.errorbar(nona['wegener'], nona['ncep'], xerr=nona['ncep_spread'], fmt="x", elinewidth=1, markersize=4,
                 color=colors[1],
                 alpha=0.8, label=f'20CRv3 $r^2={r2_ncep:.2f}$')
    sns.despine()
    plt.xlabel('wegener T2m [°C]')
    plt.ylabel('Reanalysis T2m [°C]')
    # plot diagonal line with y=x (https://stackoverflow.com/questions/25497402/adding-y-x-to-a-matplotlib-scatter-plot-if-i-havent-kept-track-of-all-the-data)
    ax = plt.gca()
    lims = [
        np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
        np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
    ]
    # now plot both limits against eachother
    ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0, linewidth=1)
    ax.set_aspect('equal')
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    plt.legend()
    if station == 'AT_Qameruj':
        plt.title('FS')
    elif station == 'AT_Weststation':
        plt.title('WS')
    else:
        raise Exception
    plt.tight_layout(pad=0.4)

plt.savefig(f'plots/wegener_vs_cera20c_scatterplot_{interp_method}.svg', bbox_inches='tight')
plt.savefig(f'plots/wegener_vs_cera20c_scatterplot_{interp_method}.png', bbox_inches='tight')

# analyze difference stationdata Qameruj and Weststation
fs = df[['wegener', 'date']][df['station'] == 'AT_Qameruj']
ws = df[['wegener', 'date']][df['station'] == 'AT_Weststation']
ws = ws.set_index('date')
fs = fs.set_index('date')
# dro pnans
ws = ws.dropna()
fs = fs.dropna()
diff = ws - fs
plt.figure()
plt.plot(diff.index, diff.wegener)
plt.ylabel('WS-FS [K]')
plt.savefig('plots/ws_fs_station_diff.svg')

# monthly means
diff = diff.to_xarray()
plt.figure()
seas_cycle = diff.groupby('date.month').mean()
plt.plot(seas_cycle.month, seas_cycle.wegener)
plt.ylabel('WS-FS [K]')
plt.savefig('plots/ws_fs_station_diff_monthly_seasonalcycle.svg')
# scale to K/100m
z_diff = 940  # m
seas_cycle_per100m = seas_cycle.wegener / (z_diff / 100)
plt.figure()
seas_cycle = diff.groupby('date.month').mean()
plt.plot(seas_cycle_per100m.month, seas_cycle_per100m)
plt.ylabel('WS-FS [K/100m]')
plt.savefig('plots/ws_fs_station_diff_monthly_seasonalcycle_per100m.svg')
