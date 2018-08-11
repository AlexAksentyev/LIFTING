import numpy as np
import pandas as pds
import sys

class Lift:
    _bar_wgt = 20
    
    def __init__(self, name, RM1, bar_wgt=20, min_wgt=20):
        self.name = name
        self.RM1 = RM1
        self.bar = bar_wgt
        self._min_wgt = min_wgt # used for controling the secondary lift
        
    def __repr__(self):
        return str(pds.DataFrame(dict(RM1 = self.RM1, BAR=self._bar_wgt), index=[0]))
    
    @property
    def bar(self):
        return self._bar_wgt
    @bar.setter
    def bar(self, val):
        self._bar_wgt = val

    def inol(self, wgt, reps):
         return np.round(reps/(1-wgt/self.RM1)/100, 2)
    def weight(self, reps, inol=.75):
        return np.round(self.RM1 * (1 - reps/inol/100), 2)
    def reps(self, wgt, inol=.75):
        return np.round(inol * (1 - wgt/self.RM1) * 100)

    def pick_closest(self, wgt):
        wgt = self._min_wgt if wgt<self._min_wgt else wgt
        load = np.arange(self._min_wgt, wgt+5, 2.5)
        wgts = load[abs(load-wgt)<2.5]
        if len(wgts)<2: return wgts[0]
        else: return wgts[1]

class Session:
    _typespec = [('pct', float), ('wgt', float),
                ('sets', int), ('reps', int),
                ('inol', float), ('inol/set', float)]
    WRM = np.array([(.3, 1, 5),
                        (.5, 1, 5),
                        (.7, 1, 3),
                        (.8, 1, 2),
                        (.9, 1, 1)],
                           dtype = [('pct', float), ('sets', int), ('reps', int)])
    WEEK = None # defined in children
    
    def __init__(self, prim_lift, sec_lift, targ_inol=1.5):
        #targ_inol=1.5(2) for loading phases, .75(1) for maintenance / session
        #targ inol 3 for loading 2 for maintenance / week
        # https://drive.google.com/file/d/1Ob-s7dPK63Or_lNK-FPvvxk4NeMjkJKv/view
        self._prim_lift = prim_lift
        self._sec_lift = sec_lift
        self._targ_inol = targ_inol

    def _comp_stats(self, lift, tbl):
        wgts = np.array([lift.pick_closest(wgt)
                                 for wgt in tbl['pct']*lift.RM1])
        pcts = np.round(wgts/lift.RM1, 2)
        reps = tbl['reps']
        if tbl.dtype.names[1] == 'sets':
                sets = tbl['sets']
                inols = np.round(sets*reps/100/(1 - pcts), 2)
        else: # if it's not sets, then it's inols
                inols = np.round(tbl['inols'], 2)
                sets = np.round(lift.reps(wgts, inols)/reps)
        set_inols = np.round(inols/sets, 2)
        return pcts, wgts, sets, reps, inols, set_inols

    def week(self, week_num):            
        work_sets = self.WEEK[self.WEEK['WN']==week_num][['pct', 'sets', 'reps']]
        warmup_sets = self.WRM[self.WRM['pct']<work_sets['pct']]

        pri = self._prim_lift
        warm_pct, warm_wgt, wsets, wreps, winol, wsinol = self._comp_stats(pri, warmup_sets)
        train_pct, train_wgt, tsets, treps, tinol, tsinol = self._comp_stats(pri, work_sets)
        pri_tbl = np.array(list(zip(warm_pct, warm_wgt, wsets, wreps, winol, wsinol))
                         + [(train_pct, train_wgt, tsets, treps, tinol, tsinol)],
                           dtype = self._typespec)
        pri_inol = winol.sum() + tinol.sum()
        pri_vol = np.sum(pri_tbl['sets']*pri_tbl['reps']*pri_tbl['wgt'])

        sec = self._sec_lift
        sec_inol = round(self._targ_inol - pri_inol, 2)
        sec_tbl = np.array([(.50, 5, .25*sec_inol),
                            (.75, 5, .75*sec_inol)],
                            dtype=[('pct', float), ('reps', int), ('inols', float)])
        sec_pct, sec_wgt, ssets, sreps, sinol, ssinol = self._comp_stats(sec, sec_tbl)
        sec_tbl = np.array(list(zip(sec_pct, sec_wgt, ssets, sreps, sinol, ssinol)), dtype=self._typespec)
        sec_vol = np.sum(sec_tbl['sets']*sec_tbl['reps']*sec_tbl['wgt'])

        print('PRIMARY ({}); TOT INOL: {:4.2f}; TOT VOL: {:4.0f} [kgs]'.format(pri.name, pri_inol, pri_vol))
        print(pds.DataFrame(pri_tbl, index=[week_num]*len(pri_tbl)))
        print('SECONDARY ({}); tot inol: {:4.2f}; TOT VOL: {:4.0f} [kgs]'.format(sec.name, sec_inol, sec_vol))
        print(pds.DataFrame(sec_tbl, index=[week_num]*len(sec_tbl)))
        return dict(pri=pri_tbl, sec=sec_tbl)
        
class MaxEffDay(Session):
    WEEK = np.array([(1, .8, 4, 4),
                         (2, .85, 3, 4),
                         (3, .9, 3, 2),
                         (5, .85, 4, 3),
                         (6, .9, 3, 2),
                         (7, .95, 3, 1)],
                            dtype=[('WN', int), ('pct', float), ('sets', int), ('reps', int)])

class DynEffDay(Session):
        WEEK = np.array([(1, .50, 5, 5),
                         (2, .55, 5, 5),
                         (3, .60, 5, 5),
                         (5, .65, 5, 5),
                         (6, .70, 3, 6),
                         (7, .75, 3, 6)],
                            dtype=[('WN', int), ('pct', float), ('sets', int), ('reps', int)])
        
        
if __name__ == '__main__':
    week_num = int(sys.argv[1])
    BSQ = Lift('BACK SQ', 140, 20, 60)
    FSQ = Lift('FRONT SQ', 90, 12.5, 52.5)
    SDL = Lift('SUMO DL', 137.5, 20, 60)
    CDL = Lift('CONV DL', 104, 20, 60)
    FBP = Lift('FLAT BP', 115, 12.5, 32.5)
    IBP = Lift('INCLINE BP', 52.5, 12.5, 32.5)
    OHP = Lift('OHP', 70, 12.5, 32.5)

    DLMAX = MaxEffDay(SDL, CDL)
    DLDYN = DynEffDay(SDL, BSQ)
    BPMAX = MaxEffDay(FBP, IBP)
    BPDYN = DynEffDay(FBP, OHP)
    SQMAX = MaxEffDay(BSQ, FSQ)
    SQDYN = DynEffDay(BSQ, SDL)

    print('        DEADLIFT')
    print('MAX EFFORT')
    _ = DLMAX.week(week_num)
    print('DYNAMIC EFFORT')
    _ = DLDYN.week(week_num)
    print('\n        SQUAT')
    print('MAX EFFORT')
    _ = SQMAX.week(week_num)
    print('DYNAMIC EFFORT')
    _ = SQDYN.week(week_num)
    print('\n        BENCH PRESS')
    print('MAX EFFORT')
    _ = BPMAX.week(week_num)
    print('DYNAMIC EFFORT')
    _ = BPDYN.week(week_num)
