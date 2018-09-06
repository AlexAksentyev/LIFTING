import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
from lift import Lift
from session import MaxEffDay, DynEffDay

class Cycle:
    def __init__(self, *units):
        self._units = units

    def __call__(self, week_num):
        tbl = []
        for unit in self._units:
            tbl.append(unit(week_num))
        return tbl


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

    SQMESO = Cycle(SQMAX, SQDYN)
    BPMESO = Cycle(BPMAX, BPDYN)
