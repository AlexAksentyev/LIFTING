import numpy as np
from pandas import DataFrame
PRILEPIN = np.array([(0.0, .70, 18, 30, 24),
                     (.70, .80, 12, 24, 18),
                     (.80, .90, 10, 20, 15),
                     (.90, 1.0,  4, 10,  7)],
                    dtype=list(zip(['lowP', 'upP', 'lowR', 'upR', 'optR'], [float]*2 + [int]*3)))

PSR_t = [('pct', float), ('sets', int), ('reps', int)]
WPSR_t = [('WN', int)]+PSR_t
FULL_t = [('pct', float), ('wgt', float),
          ('sets', int),   ('reps', int),
          ('inol', float), ('vol', float),
          ('inol/set', float), ('vol/set', float)]

WRM = np.array([(.3, 1, 8),
                (.5, 1, 5),
                (.7, 1, 3),
                (.8, 1, 2),
                (.9, 1, 1)],
               dtype=PSR_t)

def _get_rows(tbl, wn):
    wn = (wn-1)%len(tbl)
    main = tbl[[wn]][['pct','sets','reps']]
    wrm = WRM[WRM['pct']<main['pct']]
    return np.concatenate([wrm, main])

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
    _ACC = np.array([(1, .4, 3, 15), 
                     (2, .4, 3, 15), 
                     (3, .4, 3, 15)],
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
        upi=np.unique(ret_tbl['pct'], return_index=True)[1]
        uri=np.unique(ret_tbl['reps'], return_index=True)[1]
        return ret_tbl#[ii]

    def hyp(self, wn):
        return self._comp_stats(_get_rows(self._HYP, wn))
    def pow(self, wn):
        return self._comp_stats(_get_rows(self._POW, wn))
    def str(self, wn):
        return self._comp_stats(_get_rows(self._STR, wn))
    def acc(self, wn):
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
BSQ = Lift('BACK SQ', 147.5, 20, 60)
FSQ = Lift('FRONT SQ', 90, 12.5, 52.5)
MLP = Lift('LEG PRESS', 300, 0, 40)

SDL = Lift('SUMO DL', 147.5, 20, 60)
CDL = Lift('CONV DL', 104, 20, 60)
CHT = Lift('CABLE HIP THRUST', 87.5, 0, 20)
    
FBP = Lift('FLAT BP', 120, 12.5, 32.5)
IBP = Lift('INCLINE BP', 92.5, 12.5, 32.5)
CPF = Lift('CABLE PEC FLY', 18.75, 0,  6.5)
RBP = Lift('REVERSE BP', 52.5, 12.5, 32.5)
DIP = Lift('DIPS', 100, 0, 73)
    
OHP = Lift('OHP', 70, 12.5, 32.5)

