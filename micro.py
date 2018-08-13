import prilepin as PLP
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
import sys

class Micro:
    def __init__(self, **name_daytuple):
        self._days = name_daytuple
        for name, day in self._days.items():
            if not isinstance(day, tuple):
                self._days[name] = (day,)

    def vol(self, week_num):
        return self._compute_stat('vol', week_num)
    def inol(self, week_num):
        return self._compute_stat('inol', week_num)

    def _compute_stat(self, stat_name, week_num):
        stats = np.empty(len(self._days.keys()),
                         dtype = list(zip(['day', 'pri', 'sec', 'net'], [object]+[float]*3)) )
        idx = 0
        for name, day in self._days.items():
            stat_pri = 0; stat_sec = 0
            for movement in day:
                tbl = movement.week(week_num, silent=True)
                stat_pri += tbl['pri'][stat_name].sum()
                stat_sec += tbl['sec'][stat_name].sum()
            stat_net = stat_pri + stat_sec
            stats[idx] = name+str(week_num), stat_pri, stat_sec, stat_net
            idx += 1
        return stats    
    
if __name__ == '__main__':
    plt.ion()
    cycle = Micro(WED=PLP.DLMAX, FRI=PLP.BPMAX, SUN=(PLP.DLDYN, PLP.BPDYN))
    
    vol_lst = []; inol_lst = []
    for wn in [1,2,3,5,6,7]:
        vol_lst.append(cycle.vol(wn))
        inol_lst.append(cycle.inol(wn))
    vols = np.concatenate(vol_lst)
    inols = np.concatenate(inol_lst)

    f, ax = plt.subplots(2,1,sharex=True)
    ax[0].plot(vols['day'], vols['pri'], '--.r', label='primary')
    ax[0].plot(vols['day'], vols['sec'], '--.b', label='secondary')
    ax[0].plot(vols['day'], vols['net'], '--.m', label='net')
    ax[0].set_title('volume'); ax[0].set_ylabel('volume [kgs]'); ax[0].legend()
    ax[1].plot(inols['day'], inols['pri'], '--.r', label='primary')
    ax[1].plot(inols['day'], inols['sec'], '--.b', label='secondary')
    ax[1].plot(inols['day'], inols['net'], '--.m', label='net')
    ax[1].set_title('inol'); ax[1].set_ylabel('INOL'); ax[1].legend()
    ax[0].axhline(linestyle='--', color='gray'); ax[1].axhline(linestyle='--', color='gray')
    
