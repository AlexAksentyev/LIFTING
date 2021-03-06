import numpy as np
from pandas import DataFrame
PRILEPIN = np.array([(0.0, .70, 18, 30, 24), # 3--6
                     (.70, .80, 12, 24, 18), # 3--6
                     (.80, .90, 10, 20, 15), # 2--4
                     (.90, 1.0,  4, 10,  7)],# 1--2
                    dtype=list(zip(['lowP', 'upP', 'lowR', 'upR', 'optR'], [float]*2 + [int]*3)))

PSR_t = [('pct', float), ('sets', int), ('reps', int)]
WPSR_t = [('WN', int)]+PSR_t
FULL_t = [('pct', float), ('wgt', float),
          ('sets', int),   ('reps', int),
          ('inol', float), ('vol', float),
          ('inol/set', float), ('vol/set', float)]

WRM = np.array([(.35, 1, 8),
                (.55, 1, 5),
                (.75, 1, 3),
                (.85, 1, 3),
                (.95, 1, 2)],
               dtype=PSR_t)

def str_wave(lift, tot_inol, num_waves=3):
    wave_inol = tot_inol/num_waves
    set_inol = wave_inol/3
    pct_5 = lift.weight(5, set_inol)/lift.RM1
    pct_3 = lift.weight(3, set_inol)/lift.RM1
    pct_1 = lift.weight(1, set_inol)/lift.RM1
    return lift._comp_stats(np.array(list(zip([pct_5, pct_3, pct_1], [3,3,3], [5,3,1])), dtype=PSR_t))

def _get_rows(tbl, wn):
    wn = (wn-1)%len(tbl)
    main = tbl[[wn]][['pct','sets','reps']]
    l = WRM['pct']<main['pct']
    # row = main.copy()
    # row['pct'] = row['pct']+.05 if row['pct']<.95 else .99
    # row['sets'] = 1; row['reps'] = int(.67*row['reps'])
    # wrm = np.hstack((WRM[l], row))
    return np.concatenate([WRM[l], main])

class Lift:
    _bar_wgt = 20
    _HYP = np.array([(1, .75, 3, 6), 
                     (2, .75, 3, 6), 
                     (3, .75, 3, 6)],
                    dtype=WPSR_t)
    _POW =  np.array([(1, .55, 5, 5),
                      (2, .60, 5, 4),
                      (3, .65, 6, 4)],
                     dtype=WPSR_t)
    _STR = np.array([(1, .85, 5, 3), 
                     (2, .93, 4, 2), 
                     (3, .97, 3, 2)],
                    dtype=WPSR_t)
    _ACC = np.array([(1, .65, 3, 10), 
                     (2, .65, 3, 10), 
                     (3, .65, 3, 10)],
                    dtype=WPSR_t)
    
    
    def __init__(self, name, RM1, bar_wgt=20, min_wgt=20):
        self.name = name
        self.RM1 = RM1
        self.bar = bar_wgt
        self._min_wgt = min_wgt
        
    def __repr__(self):
        return str(DataFrame(dict(RM1 = self.RM1, BAR=self._bar_wgt), index=[0]))

    def _comp_stats(self, tbl):
        wgts = np.array([self.pick_closest(wgt)
                         for wgt in tbl['pct']*self.RM1])
        pcts = np.round(wgts/self.RM1, 2)
        reps = tbl['reps']
        if tbl.dtype.names[1] == 'sets':
            sets = tbl['sets']
            inols = np.round(sets*reps/100/(1 - pcts), 2)
        else: # if it's not sets, then it's inols
            inols = np.round(tbl['inols'], 2)
            sets = np.round(self.reps(wgts, inols)/reps)
            sets = np.array([0 if e<0 else e for e in sets])
            inols = self.inol(wgts, sets*reps) # adjust inols for computed sets
        vols = np.round(wgts*sets*reps)
        set_inols = np.round(np.divide(inols, sets, where=sets!=0), 2)
        set_vols = np.round(np.divide(vols, sets, where=sets!=0))
        ret_tbl = np.array(list(zip(pcts, wgts, sets, reps, inols, vols, set_inols, set_vols)), dtype=FULL_t)
        return ret_tbl

    def hyp(self, wn=1):
        return self._comp_stats(_get_rows(self._HYP, wn))
    def pow(self, wn=1):
        return self._comp_stats(_get_rows(self._POW, wn))
    def str(self, wn=1):
        return self._comp_stats(_get_rows(self._STR, wn))
    def acc(self, wn=1):
        return self._comp_stats(_get_rows(self._ACC, wn))
    
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
        wgt = self._min_wgt if wgt<self._min_wgt and wgt>0 else wgt
        load = np.append(np.arange(self._min_wgt, wgt+5, 2.5), 0)
        wgts = load[abs(load-wgt)<2.5]
        if len(wgts)<2: return wgts[0]
        else:
            delta = abs(wgts - wgt)
            best_wgt = wgts[0] if delta[0]<delta[1] else wgts[1]
            return best_wgt


# ******************************
BSQ = Lift('BACK SQ', 120, 20, 50) # current
FSQ = Lift('FRONT SQ', 80, 20, 50) #
MLP = Lift('LEG PRESS', 300, 0, 40)

SDL = Lift('SUMO DL', 130, 20, 50) #
CDL = Lift('CONV DL', 80, 20, 50) #
CHT = Lift('CABLE HIP THRUST', 87.5, 0, 20)
TBR = Lift('T-BAR ROW', 50, 0, 20)
    

FBP = Lift('FLAT BP', 100, 20, 50) #
PFBP = Lift('PAUSED FBP', 80, 20, 50) #
CGBP = Lift('CLOSE GRIP BP', 100, 20, 50) #
IBP = Lift('INCLINE BP', 102.5, 12.5, 32.5)
CPF = Lift('CABLE PEC FLY', 18.75, 0,  6.5)
RBP = Lift('REVERSE BP', 52.5, 12.5, 32.5)
DIP = Lift('DIPS', 100, 0, 72)
    
OHP = Lift('OHP', 50, 20, 30) #

