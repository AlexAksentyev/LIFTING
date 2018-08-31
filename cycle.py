import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
import lift
import session as ssn
from importlib import reload

reload(lift)
reload(ssn)

STAT = dict(inol=lambda tbl: tbl['inol'].sum(),
                vol=lambda tbl: tbl['vol'].sum(),
                maxP=lambda tbl: tbl['pct'].max(),
                maxW=lambda tbl: tbl['wgt'].max())

class Micro:
    def __init__(self, name, lift1, lift2, accessory):
        self.name = name
        max_eff_name = 'MAX Effort ({})'.format(lift1.name)
        dyn_eff_name = 'DYN Effort ({})'.format(lift1.name)
        self.max_eff = ssn.MaxEffDay(max_eff_name, lift1, accessory)
        self.dyn_eff = ssn.DynEffDay(dyn_eff_name, lift1, lift2)

    def __call__(self, num, silent=False):
        max_tbl = self.max_eff(num, silent)
        dyn_tbl = self.dyn_eff(num, silent)
        return (max_tbl, dyn_tbl)

    def plot(self, stat='inol', day_type='both', weeks=range(1,4)):
        n_rec = len(weeks)
        ps = np.empty((n_rec,2), dtype=[('day', object), (stat, float)])
        ss = np.empty((n_rec,2), dtype=[('day', object), (stat, float)])
        ns = np.empty((n_rec,2), dtype=[('day', object), (stat, float)])
        for i, wn in enumerate(weeks):
            max_tbl, dyn_tbl = self(wn, True)
            ps[i, 0] = 'MAX'+str(wn), STAT[stat](max_tbl['pri'])
            ss[i, 0] = 'MAX'+str(wn), STAT[stat](max_tbl['sec'])
            ns[i, 0] = 'MAX'+str(wn), (ps[i,0][stat] + ss[i,0][stat])
            ps[i, 1] = 'DYN'+str(wn), STAT[stat](dyn_tbl['pri'])
            ss[i, 1] = 'DYN'+str(wn), STAT[stat](dyn_tbl['sec'])
            ns[i, 1] = 'DYN'+str(wn), (ps[i,1][stat] + ss[i,1][stat])
        if day_type=='both':
            ps.shape = (-1,)
            ss.shape = (-1,)
            ns.shape = (-1,)
        else:
            ps = ps[:,0] if day_type=='max' else ps[:,1]
            ss = ss[:,0] if day_type=='max' else ss[:,1]
            ns = ns[:,0] if day_type=='max' else ns[:,1]
        f = plt.figure()
        plt.title(self.name)
        plt.plot(ps[stat], '--.b', label='pri')
        plt.plot(ss[stat], '--.r', label='sec')
        if stat[:3]!='max':
            plt.plot(ns[stat], '--.g', label='net')
        plt.xticks(range(ps.shape[0]), ps['day'])
        plt.xlabel('day'); plt.ylabel(stat)
        plt.legend(); plt.grid()
        return f


if __name__ == '__main__':
    SQMICRO = Micro('BSQ Strength', lift.BSQ, lift.SDL, lift.FSQ)
    DLMICRO = Micro('SDL Strength', lift.SDL, lift.BSQ, lift.CHT)
    OHPMICRO = Micro('OHP Strength', lift.OHP, lift.FBP, lift.RBP)
    FBPMICRO = Micro('FBP Strength', lift.FBP, lift.OHP, lift.CPF)
