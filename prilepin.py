import numpy as np
import pandas as pds
import sys

PRILEPIN = np.array([(0.0, .70, 18, 30, 24),
                     (.70, .80, 12, 24, 18),
                     (.80, .90, 10, 20, 15),
                     (.90, 1.0,  4, 10,  7)],
                    dtype=list(zip(['lowP', 'upP', 'lowR', 'upR', 'optR'], [float]*2 + [int]*3)))
    
def useful(reps, pct):
    row = PRILEPIN[np.logical_and(pct>=PRILEPIN['lowP'], pct<PRILEPIN['upP'])]
    return reps >= row['lowR'] and reps <= row['upR']

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
        else:
            delta = abs(wgts - wgt)
            best_wgt = wgts[0] if delta[0]<delta[1] else wgts[1]
            return best_wgt

class Session:
    _typespec = [('pct', float), ('wgt', float),
                ('sets', int), ('reps', int),
                ('inol', float), ('vol', float),
                ('inol/set', float), ('vol/set', float)]
    _effort_type = None # defined in children
    WRM = np.array([(.3, 1, 5),
                        (.5, 1, 5),
                        (.7, 1, 3),
                        (.8, 1, 2),
                        (.9, 1, 1)],
                           dtype = [('pct', float), ('sets', int), ('reps', int)])
    WEEK = None # defined in children
    
    def __init__(self, week_day, prim_lift, sec_lift, targ_inol=1.5):
        #targ_inol=1.5(2) for loading phases, .75(1) for maintenance / session
        #targ inol 3 for loading 2 for maintenance / week
        # https://drive.google.com/file/d/1Ob-s7dPK63Or_lNK-FPvvxk4NeMjkJKv/view
        self._week_day = week_day
        self._prim_lift = prim_lift
        self._sec_lift = sec_lift
        self._targ_inol = targ_inol

    @property
    def pri_lift(self):
        return self._prim_lift
    @property
    def sec_lift(self):
        return self._sec_lift
    @property
    def effort_type(self):
        return self._effort_type

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
                sets = np.array([0 if e<0 else e for e in sets])
                inols = lift.inol(wgts, sets*reps) # adjust inols for computed sets
        vols = np.round(wgts*sets*reps)
        set_inols = np.round(np.divide(inols, sets, where=sets!=0), 2)
        set_vols = np.round(np.divide(vols, sets, where=sets!=0))
        return pcts, wgts, sets, reps, inols, vols, set_inols, set_vols

    def week(self, week_num, silent=False):            
        work_sets = self.WEEK[self.WEEK['WN']==week_num][['pct', 'sets', 'reps']]
        warmup_sets = self.WRM[self.WRM['pct']<work_sets['pct']]

        pri = self._prim_lift
        warm_pct, warm_wgt, wsets, wreps, winol, wvol, wsinol, wsvol = self._comp_stats(pri, warmup_sets)
        train_pct, train_wgt, tsets, treps, tinol, tvol, tsinol, tsvol = self._comp_stats(pri, work_sets)
        pri_tbl = np.array(list(zip(warm_pct, warm_wgt, wsets, wreps, winol, wvol, wsinol, wsvol))
                         + [(train_pct, train_wgt, tsets, treps, tinol, tvol, tsinol, tsvol)],
                           dtype = self._typespec)
        pri_inol = winol.sum() + tinol.sum()
        pri_vol = np.sum(pri_tbl['sets']*pri_tbl['reps']*pri_tbl['wgt'])

        sec = self._sec_lift
        sec_inol = round(self._targ_inol - pri_inol, 2)
        sec_tbl = np.array([(.50, 5, .25*sec_inol),
                            (.75, 5, .75*sec_inol)],
                            dtype=[('pct', float), ('reps', int), ('inols', float)])
        sec_pct, sec_wgt, ssets, sreps, sinol, svol, ssinol, ssvol = self._comp_stats(sec, sec_tbl)
        sec_inol = sinol.sum() # recompute after rep readjustment
        sec_tbl = np.array(list(zip(sec_pct, sec_wgt, ssets, sreps, sinol, svol, ssinol, ssvol)), dtype=self._typespec)
        if not useful(ssets[1]*sreps[1], sec_pct[1]): # if the work sets aren't useful, don't include sec lift
            sec_tbl['sets'] *= 0
            sec_tbl['reps'] *= 0
            sec_tbl['inol'] *= 0
            sec_tbl['vol']  *= 0
            sec_tbl['inol/set'] *= 0
            sec_tbl['vol/set']  *= 0
        sec_vol = np.sum(sec_tbl['sets']*sec_tbl['reps']*sec_tbl['wgt'])
        sec_inol = self._sec_lift.inol(sec_tbl['wgt'], sec_tbl['sets']*sec_tbl['reps']).sum()

        if not silent:
            print('        '+self._week_day)
            print('PRIMARY ({}); TOT INOL: {:4.2f}; TOT VOL: {:4.0f} [kgs]'.format(pri.name, pri_inol, pri_vol))
            print(pds.DataFrame(pri_tbl, index=[week_num]*len(pri_tbl)))
            print('SECONDARY ({}); TOT INOL: {:4.2f}; TOT VOL: {:4.0f} [kgs]'.format(sec.name, sec_inol, sec_vol))
            print(pds.DataFrame(sec_tbl, index=[week_num]*len(sec_tbl)))
            print('TOT INOL: {:4.2f}; TOT VOL: {:4.0f}'.format(pri_inol+sec_inol, pri_vol+sec_vol))
        return dict(pri=pri_tbl, sec=sec_tbl)
        
class MaxEffDay(Session):
    WEEK = np.array([(1, .82, 4, 4),
                     (2, .87, 5, 3),
                     (3, .92, 4, 2),
                     (5, .87, 5, 3),
                     (6, .92, 3, 2),
                     (7, .96, 3, 2)],
                        dtype=[('WN', int), ('pct', float), ('sets', int), ('reps', int)])
    _effort_type = 'MAX'

class DynEffDay(Session):
        WEEK = np.array([(1, .55, 5, 5),
                         (2, .60, 5, 5),
                         (3, .65, 5, 5),
                         (5, .55, 6, 4),
                         (6, .60, 5, 4),
                         (7, .65, 6, 3)],
                            dtype=[('WN', int), ('pct', float), ('sets', int), ('reps', int)])
        _effort_type = 'DYN'

############################################################
BSQ = Lift('BACK SQ', 140, 20, 60)
FSQ = Lift('FRONT SQ', 90, 12.5, 52.5)
SDL = Lift('SUMO DL', 137.5, 20, 60)
CDL = Lift('CONV DL', 104, 20, 60)
FBP = Lift('FLAT BP', 115, 12.5, 32.5)
IBP = Lift('INCLINE BP', 52.5, 12.5, 32.5)
OHP = Lift('OHP', 70, 12.5, 32.5)

DLMAX = MaxEffDay('WEDNSDAY (Max Effort DL)', SDL, CDL)
DLDYN = DynEffDay('SUNDAY (Dynamic Effort DL)', SDL, BSQ)
BPMAX = MaxEffDay('FRIDAY (Max Effort BP)', FBP, IBP)
BPDYN = DynEffDay('SUNDAY (Dynamic Effort BP)', FBP, OHP)
SQMAX = MaxEffDay('SUNDAY (Max Effort SQ)', BSQ, FSQ)
SQDYN = DynEffDay('WEDNSDAY (Dynamic Effort SQ)', BSQ, SDL)
    
if __name__ == '__main__':
    week_num = int(sys.argv[1])
    day = sys.argv[2].upper() if len(sys.argv)>2 else 'ALL'

    silent = dict(WED=True, FRI=True, SUN=True)
    if day!='ALL':
        silent[day[:3]]=False
    else:
        for day in silent.keys():
            silent[day]=False
            
    dlmax_tbl = DLMAX.week(week_num, silent['WED'])
    bpmax_tbl = BPMAX.week(week_num, silent['FRI'])
    dldyn_tbl = DLDYN.week(week_num, silent['SUN'])
    bpdyn_tbl = BPDYN.week(week_num, silent['SUN'])
