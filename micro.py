import prilepin as PLP
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
import sys

class Micro:
    def __init__(self, number, **name_daytuple):
        self._days = name_daytuple
        # prepare for the computation of stats
        for name, day in self._days.items():
            if not isinstance(day, tuple):
                self._days[name] = (day,)

        # compute stats
        self.stats = self._compute_stats(number)

    def _compute_stats(self, week_num):
        stats = np.empty((len(self._days.keys()), 3),
                         dtype = list(zip(['day', 'inol', 'vol'], [object, float, float])) )
        stat = lambda lift, name: tbl[lift][name].sum()
        idx = 0
        for name, day in self._days.items():
            pri_vol = 0; pri_inol = 0
            sec_vol = 0; sec_inol = 0
            for movement in day:
                tbl = movement.week(week_num, silent=True)
                pri_vol += stat('pri', 'vol')
                pri_inol += stat('pri', 'inol')
                sec_vol += stat('sec', 'vol')
                sec_inol += stat('sec','inol')
            net_vol = pri_vol + sec_vol
            net_inol = pri_inol + sec_inol
            stats[idx][0] = name+str(week_num), net_inol, net_vol
            stats[idx][1] = name+str(week_num), pri_inol, pri_vol
            stats[idx][2] = name+str(week_num), sec_inol, sec_vol
            idx += 1
        return stats

# class Meso:
#     def __init__(self, *micro_lst):
#         self._micros = micro_lst

#     def _compute_stat(self, stat_name):
#         stats = np.empty(len(self._micros),
#                          dtype=list(zip(['num', 'pri','sec','net'], [int]+[float]*3)))
#         for cycle in self._micros:
#             s = 
    
if __name__ == '__main__':
    plt.ion()
    cyc_lst = []
    for wn in [1,2,3,5,6,7]:
        cyc_lst.append(Micro(wn, WED=PLP.DLMAX, FRI=PLP.BPMAX, SUN=(PLP.DLDYN, PLP.BPDYN)))
    
    # vol_lst = []; inol_lst = []
    # for wn in [1,2,3,5,6,7]:
    #     vol_lst.append(cycle.vol(wn))
    #     inol_lst.append(cycle.inol(wn))
    # vols = np.concatenate(vol_lst)
    # inols = np.concatenate(inol_lst)

    # f, ax = plt.subplots(2,1,sharex=True)
    # ax[0].plot(vols['day'], vols['pri'], '--.r', label='primary')
    # ax[0].plot(vols['day'], vols['sec'], '--.b', label='secondary')
    # ax[0].plot(vols['day'], vols['net'], '--.m', label='net')
    # ax[0].set_title('volume'); ax[0].set_ylabel('volume [kgs]'); ax[0].legend()
    # ax[1].plot(inols['day'], inols['pri'], '--.r', label='primary')
    # ax[1].plot(inols['day'], inols['sec'], '--.b', label='secondary')
    # ax[1].plot(inols['day'], inols['net'], '--.m', label='net')
    # ax[1].set_title('inol'); ax[1].set_ylabel('INOL'); ax[1].legend()
    # ax[0].axhline(linestyle='--', color='gray'); ax[1].axhline(linestyle='--', color='gray')
    
