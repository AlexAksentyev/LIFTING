import prilepin as PLP
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
import sys
from importlib import reload

reload(PLP)

class Cycle:
    def __init__(self, name):
        self.stats = None
        self.name = name

    def _plot_base(self, stat, day_type='all', stats=None):
        if stats is None: stats = self.stats
        day_type = day_type.upper()
        ncol = stats.shape[1]
        stats = stats[stats['type']==day_type].reshape(-1,ncol) if day_type!='ALL' else stats
        print('***** PRIMARY *****')
        print(DataFrame(stats[:,1]))
        print('***** SECONDARY *****')
        print(DataFrame(stats[:,2]))
        print('***** BOTH *****')
        print(DataFrame(stats[:,0]))
        xlab = stats.dtype.names[0]
        pname = 'primary'
        sname = 'secondary'
        plt.figure()
        plt.plot(stats[:,1][stat], '--.', label=pname)
        plt.xticks(range(stats.shape[0]), stats[:,1][xlab])
        plt.plot(stats[:,2][stat], '--.', label=sname)
        plt.xticks(range(stats.shape[0]), stats[:,2][xlab])
        plt.plot(stats[:,0][stat], '--*', label='tot', lw=2.5)
        plt.xticks(range(stats.shape[0]), stats[:,0][xlab])
        plt.legend()
        plt.axhline(ls='--', color='gray')
        plt.title(self.name)
        plt.ylabel(stat)
        plt.xlabel(xlab)

    def plot(self, stat='inol', day_type='all'):
        self._plot_base(stat, day_type)
        if stat=='inol':
            plt.axhline(y=.75, ls='--', lw=.5, color='blue')
            plt.axhline(y=1.0, ls='--', lw=.5, color='blue')
            plt.axhline(y=1.5, ls='--', lw=.5, color='red')
            plt.axhline(y=2.0, ls='--', lw=.5, color='red')

class Micro(Cycle):
    def __init__(self, name, number, **name_day):
        super().__init__(name)
        self._days = name_day

        # compute stats
        self.stats = self._compute_stats(number)     

    def day(self, name):
        d = self._days[name.upper()]
        return d[0] if len(d)==1 else d
    
    def _compute_stats(self, week_num):
        stats = np.empty((len(self._days.keys()), 3),
                         dtype = list(zip([ 'day', 'type', 'inol', 'vol', 'maxP', 'maxW'],
                                          [object]*2+[float]*4)) )
        stat = lambda lift, name: tbl[lift][name].sum()
        idx = 0
        for name, day in self._days.items():
            pri_vol = 0; pri_inol = 0
            sec_vol = 0; sec_inol = 0
            tbl = day.week(week_num, silent=True)
            pri_vol  += stat('pri', 'vol')
            pri_inol += stat('pri', 'inol')
            sec_vol  += stat('sec', 'vol')
            sec_inol += stat('sec', 'inol')
            net_vol = pri_vol + sec_vol
            net_inol = pri_inol + sec_inol
            pri_maxP = tbl['pri']['pct'][-1]
            pri_maxW = tbl['pri']['wgt'][-1]
            sec_wsets = tbl['sec']['sets'][-1] # b/c secondary lift may have 0 sets (unlike primary)
            sec_maxP = tbl['sec']['pct'][-1] if sec_wsets!=0 else 0
            sec_maxW = tbl['sec']['wgt'][-1] if sec_wsets!=0 else 0
            net_maxP = max(pri_maxP, sec_maxP)
            net_maxW = max(pri_maxW, sec_maxW)
            stats[idx][0] = name+str(week_num), day.effort_type, net_inol, net_vol, net_maxP, net_maxW
            stats[idx][1] = name+str(week_num), day.effort_type, pri_inol, pri_vol, pri_maxP, pri_maxW
            stats[idx][2] = name+str(week_num), day.effort_type, sec_inol, sec_vol, sec_maxP, sec_maxW
            idx += 1
        return stats

class Meso(Cycle):
    def __init__(self, name, micro_lst):
        super().__init__(name)
        self._micros = micro_lst
        self.stats = np.concatenate([cyc.stats for cyc in self._micros])

        self._micro_stats = np.empty((len(self._micros), 3),
                                     dtype=[('cycle', object), ('inol', float), ('vol', float)])
        for idx, cyc in enumerate(self._micros):
            tbl0 = cyc.stats
            for i in range(3):
                tbl = DataFrame(tbl0[:,i]).sum(axis=0)
                self._micro_stats[idx, i] = tbl['day'], tbl['inol'], tbl['vol']

    def plot_micros(self, stat='inol'):
        super()._plot_base(stat, 'all', stats=self._micro_stats)
        plt.axhline(y=1.00, ls='--', lw=.5, color='blue')
        plt.axhline(y=1.98, ls='--', lw=.5, color='blue')
        plt.axhline(y=2.02, ls='--', lw=.5, color='red')
        plt.axhline(y=3.00, ls='--', lw=.5, color='red')
        
        
    def __getitem__(self, idx):
        return self._micros[idx]
            
    
if __name__ == '__main__':
    stat = sys.argv[1] if len(sys.argv)>1 else 'inol'
    plt.close('all')
    plt.ion()
    dl_micros = []; bp_micros = []; sq_micros = []
    for wn in [1,2,3,5,6,7]:
        dl_micros.append(Micro('DL', wn, WED=PLP.DLMAX, SUN=PLP.DLDYN))
        bp_micros.append(Micro('BP', wn, FRI=PLP.BPMAX, SUN=PLP.BPDYN))
        sq_micros.append(Micro('SQ', wn, WED=PLP.SQMAX, SUN=PLP.SQDYN))

    DLMESO = Meso('DL', dl_micros)
    BPMESO = Meso('BP', bp_micros)
    SQMESO = Meso('SQ', sq_micros)

    # DLMESO.plot(stat); plt.grid()
    # BPMESO.plot(stat); plt.grid()
    # SQMESO.plot(stat); plt.grid()
    # DLMESO.plot_micros(stat); plt.grid()
    # BPMESO.plot_micros(stat); plt.grid()
    # SQMESO.plot_micros(stat); plt.grid()
