import prilepin as PLP
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
import sys
from importlib import reload

reload(PLP)

class Cycle:
    def __init__(self):
        self.stats = None

    def plot(self, stat, stats=None):
        if stats is None: stats = self.stats
        xlab = stats.dtype.names[0]
        pname = 'primary'
        sname = 'secondary'
        plt.figure()
        plt.plot(stats[:,1][xlab], stats[:,1][stat], '--.', label=pname)
        plt.plot(stats[:,2][xlab], stats[:,2][stat], '--.', label=sname)
        plt.plot(stats[:,0][xlab], stats[:,0][stat], '--*', label='tot', lw=2.5)
        plt.legend()
        plt.axhline(ls='--', color='gray')
        plt.title(stat)
        


class Micro(Cycle):
    def __init__(self, number, **name_daytuple):
        super().__init__()
        self._days = name_daytuple
        # prepare for the computation of stats
        for name, day in self._days.items():
            if not isinstance(day, tuple):
                self._days[name] = (day,)

        # compute stats
        self.stats = self._compute_stats(number)     

    def day(self, name):
        d = self._days[name.upper()]
        return d[0] if len(d)==1 else d

    def plot(self, stat='inol'):
        super().plot(stat)
        plt.axhline(y=.75, ls='--', lw=.5, color='blue')
        plt.axhline(y=1.0, ls='--', lw=.5, color='blue')
        plt.axhline(y=1.5, ls='--', lw=.5, color='red')
        plt.axhline(y=2.0, ls='--', lw=.5, color='red')
    
    def _compute_stats(self, week_num):
        stats = np.empty((len(self._days.keys()), 3),
                         dtype = list(zip([ 'cycle', 'inol', 'vol'], [object, float, float])) )
        stat = lambda lift, name: tbl[lift][name].sum()
        idx = 0
        for name, day in self._days.items():
            pri_vol = 0; pri_inol = 0
            sec_vol = 0; sec_inol = 0
            for movement in day:
                tbl = movement.week(week_num, silent=True)
                pri_vol  += stat('pri', 'vol')
                pri_inol += stat('pri', 'inol')
                sec_vol  += stat('sec', 'vol')
                sec_inol += stat('sec', 'inol')
            net_vol = pri_vol + sec_vol
            net_inol = pri_inol + sec_inol
            stats[idx][0] = name+str(week_num), net_inol, net_vol
            stats[idx][1] = name+str(week_num), pri_inol, pri_vol
            stats[idx][2] = name+str(week_num), sec_inol, sec_vol
            idx += 1
        return stats

class Meso(Cycle):
    def __init__(self, micro_lst):
        super().__init__()
        self._micros = micro_lst
        self.stats = np.concatenate([cyc.stats for cyc in self._micros])

        self._micro_stats = np.empty((len(self._micros), 3),
                                     dtype=[('cycle', object), ('inol', float), ('vol', float)])
        for idx, cyc in enumerate(self._micros):
            tbl0 = cyc.stats
            for i in range(3):
                tbl = DataFrame(tbl0[:,i]).sum(axis=0)
                self._micro_stats[idx, i] = tbl['cycle'], tbl['inol'], tbl['vol']

    def plot(self, stat='inol'):
        super().plot(stat)
        plt.axhline(y=.75, ls='--', lw=.5, color='blue')
        plt.axhline(y=1.0, ls='--', lw=.5, color='blue')
        plt.axhline(y=1.5, ls='--', lw=.5, color='red')
        plt.axhline(y=2.0, ls='--', lw=.5, color='red')

    def plot_micros(self, stat='inol'):
        super().plot(stat, self._micro_stats)
        plt.axhline(y=1.00, ls='--', lw=.5, color='blue')
        plt.axhline(y=1.98, ls='--', lw=.5, color='blue')
        plt.axhline(y=2.02, ls='--', lw=.5, color='red')
        plt.axhline(y=3.00, ls='--', lw=.5, color='red')
        
        
    def __getitem__(self, idx):
        return self._micros[idx]
            
    
if __name__ == '__main__':
    plt.ion()
    dl_micros = []; bp_micros = []
    for wn in [1,2,3,5,6,7]:
        dl_micros.append(Micro(wn, WED=PLP.DLMAX, SUN=PLP.DLDYN))
        bp_micros.append(Micro(wn, FRI=PLP.BPMAX, SUN=PLP.BPDYN))

    DLMESO = Meso(dl_micros)
    BPMESO = Meso(bp_micros)
