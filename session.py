import numpy as np
from pandas import DataFrame
from lift import Lift, FULL_t
from numpy.lib.recfunctions import append_fields

class Session:
    _struct = None
    
    def __init__(self, label, prim_lift, sec_lift, targ_inol=1.5):
        #targ_inol=1.5(2) for loading phases, .75(1) for maintenance / session
        #targ inol 3 for loading 2 for maintenance / week
        # https://drive.google.com/file/d/1Ob-s7dPK63Or_lNK-FPvvxk4NeMjkJKv/view
        self._label = label
        self._prim_lift = prim_lift
        self._sec_lift = sec_lift
        self._targ_inol = targ_inol

    def __repr__(self):
        pri_inol=0; pri_vol=0
        sec_inol=0; sec_vol=0
        for i in range(1,4):
            print('WEEK #', i)
            dat = self.__call__(i)
            pri_inol += dat['pri']['inol'].sum()
            sec_inol += dat['sec']['inol'].sum()
            pri_vol +=  dat['pri']['vol'].sum()
            sec_vol +=  dat['sec']['vol'].sum()
        pname = self.pri_lift.name
        sname = self.sec_lift.name
        rstr = lambda name, inol, vol: '{} INOL {:4.2f} VOL {:4.2f}\n'.format(name, inol, vol)
        return rstr(pname, pri_inol, pri_vol) +\
                    rstr(sname, sec_inol, sec_vol) +\
                    rstr('TOT', pri_inol+sec_inol, pri_vol+sec_vol)
        

    @property
    def pri_lift(self):
        return self._prim_lift
    @property
    def sec_lift(self):
        return self._sec_lift

    def __call__(self, week_num, silent=False):
        pri_type = self._struct['PRI']
        pri_method = getattr(self.pri_lift, pri_type)
        pri_tbl = pri_method(week_num)
        pri_type = np.array([pri_type]*len(pri_tbl))
        pri_tbl = append_fields(pri_tbl, 'type', pri_type).base
        pri_inol = round(pri_tbl['inol'].sum(), 2)
        pri_vol  = round(pri_tbl['vol'].sum(), 2)
        
        sec_type = self._struct['SEC']
        sec_method = getattr(self.sec_lift, sec_type)
        sec_tbl = sec_method(week_num)
        sec_type = np.array([sec_type]*len(sec_tbl))
        sec_tbl = append_fields(sec_tbl, 'type', sec_type).base
        sec_inol = round(sec_tbl['inol'].sum(), 2)
        sec_vol  = round(sec_tbl['vol'].sum(), 2)
        if not silent:
            print(self.pri_lift.name, "INOL:", pri_inol, "VOL:", pri_vol)
            print(DataFrame(pri_tbl))
            print(self.sec_lift.name, "INOL:", sec_inol, "VOL:", sec_vol)
            print(DataFrame(sec_tbl))
            print("TOT", "INOL:", round(pri_inol+sec_inol,2), "VOL:", round(pri_vol+sec_vol,2))
        return dict(pri=pri_tbl, sec=sec_tbl)

                             
class MaxEffDay(Session):
    _struct = dict(PRI='str', SEC='acc')
                    

class DynEffDay(Session):
    _struct = dict(PRI='pow', SEC='hyp')

if __name__ == '__main__':
    BSQ = Lift('BACK SQ', 140, 20, 60)
    FSQ = Lift('FRONT SQ', 90, 12.5, 52.5)
    
    SDL = Lift('SUMO DL', 145, 20, 60)
    CDL = Lift('CONV DL', 104, 20, 60)
    CHT = Lift('CABLE HIP THRUST', 87.5, 0, 20)
    
    FBP = Lift('FLAT BP', 125, 12.5, 32.5)
    IBP = Lift('INCLINE BP', 52.5, 12.5, 32.5)
    CPF = Lift('CABLE PEC FLY', 18.75, 0,  6.5)
    RBP = Lift('REVERSE BP', 52.5, 12.5, 31.5)
    
    OHP = Lift('OHP', 70, 12.5, 32.5)

    DLMAX = MaxEffDay('WEDNSDAY (Max Effort DL)', SDL, CHT)
    DLDYN = DynEffDay('SUNDAY (Dynamic Effort DL)', SDL, BSQ)
    
    BPMAX = MaxEffDay('FRIDAY (Max Effort BP)', FBP, CPF)
    BPDYN = DynEffDay('SUNDAY (Dynamic Effort BP)', FBP, OHP)
    
    SQMAX = MaxEffDay('WEDNSDAY (Max Effort SQ)', BSQ, FSQ)
    SQDYN = DynEffDay('SUNDAY (Dynamic Effort SQ)', BSQ, SDL)
    
    OHPMAX = MaxEffDay('FRIDAY (Max Effort OHP)', OHP, RBP)
    OHPDYN = DynEffDay('SUNDAY (Dynamic Effort OHP)', OHP, FBP)
