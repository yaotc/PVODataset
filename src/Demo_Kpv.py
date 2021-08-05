import pandas as pd
import os
import numpy as np
import math
import matplotlib.pyplot as plt

from sklearn import metrics
from sklearn.metrics import mean_squared_error as MSE
from sklearn.metrics import mean_absolute_error as MAE
from pvlib import pvsystem 

from pvodataset import PVODataset


def MAPE(y, pred):
    y = np.array(y)
    pred = np.array(pred)
    ans = []
    for i,j in enumerate(y):
        if y[i] and pred[i]:
            ans.append(np.abs(y[i] - pred[i])/ y[i])
    return np.sum(ans)/ len(ans) * 100

class demo_K_PV(PVODataset):
    """
    The usage of Inheritance grammar.
    Follow Open-Closed Principle and Single Responsibility Principle.
    Note: start - end >= 96. (24h with 15m resolution) = 24*6 = 96 timesteps.)
    """ 
    def __init__(self, path='../datasets/', params=0):
        super(demo_K_PV, self).__init__(path) 

        pass
    
    def init_PV_sys(self):

        module_parameters = {'pdc0': 32, 'gamma_pdc': -0.004}
        inverters = pvsystem.retrieve_sam('cecinverter')
        inverter_parameters = inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']
        system = pvsystem.PVSystem(module_parameters=module_parameters,
                                   inverter_parameters=inverter_parameters,
                           surface_tilt=33, surface_azimuth=180)
        return system

    def calc_PV_clr(self, irra_poa, temp_cell, system):

        pdc = system.pvwatts_dc(g_poa_effective=irra_poa, temp_cell=temp_cell)
        return pdc
    
    # users-defined demo1
    def range_calc_KPV(self, ori_data, start, end):
        power = ori_data["power"][start:end]
        irra_poa = ori_data["lmd_totalirrad"][start:end]
        temp_cell = ori_data["lmd_temperature"][start:end]
        datet = ori_data["date_time"][start:end]
        datet = [str(i)[:-3] for i in datet]
        # 24 h ( 15m resolution) = 24 * 6 = 96 timesteps 
        tmp_time = [datet[i] for i in list(range(0, end, 96))]
        system = self.init_PV_sys()
        K_pv, pltpdc= [], []
        for i in range(start, end):
            pdc = self.calc_PV_clr(irra_poa[i],temp_cell[i], system)
            pltpdc.append(pdc)
            if pdc == 0:
                K_pv.append(0)
            else:
                K_pv.append(power[i]/pdc)

        return K_pv, pltpdc, power, tmp_time


    def plot_kpv(self, K_pv, tmp_time, start, end):
        
        fs = 18
        lines = [1 for i in range(len(K_pv))]
        plt.figure(figsize=(24,8),dpi=300)

        plt.plot(K_pv,  'g-.')
        # plt.plot(pltpdc, 'b--')
        plt.plot(lines,  'k--', linewidth=1)
        # 24 h ( 15m resolution) = 24 * 6 = 96 timesteps 
        plt.xticks(list(range(start, end,96)), tmp_time)

        plt.grid(ls='--')
        plt.xlim(start, end)
        plt.yticks(size = fs-1)
        plt.xticks(size = fs-1)
        plt.ylabel('K_PV',fontsize=fs)
        plt.xlabel('Time step (15-min)',fontsize=fs)
        plt.savefig("./Kpv.png", bbox_inches='tight')
        plt.show()

    def plot_clr(self, power, pltpdc, tmp_time, start, end):
        plt.rc('font',family='Times New Roman')
        plt.figure(figsize=(24,8),dpi=300)
        fs = 18
        line0, = plt.plot(power, color='#D94E5D', linestyle='-')
        line1, = plt.plot(pltpdc, color='blue', linestyle='--')

        for i in list(range(start, end-96, 96)):
            right_ = i + 96 if i+96 <= end else end
            rmse = MSE(power[i:right_], pltpdc[i:right_])**0.5
            mae = MAE(power[i:right_], pltpdc[i:right_])
            mape = MAPE(power[i:right_], pltpdc[i:right_])
            plt.text(i+37, 4, f'MAPE: {round(mape,1)}%', size = fs-4)
            plt.text(i+37, 3, f'RMSE: {round(rmse,1)}',  size = fs-4)
            plt.text(i+37, 2, f'MAE  :{round(mae ,1)}',  size = fs-4)

        plt.grid(ls='--')
        plt.xlim(start, end)
        plt.yticks(size = fs-1)
        plt.xticks(size = fs-1)
        plt.legend(handles=[line0, line1], labels=['PV_MEAS','PV_CLR'], loc='best',fontsize=fs)
        plt.xticks(list(range(start, end, 96)), tmp_time)
        plt.ylabel('Power (W/M^2)',fontsize=fs)
        plt.xlabel('Time step (15-min)',fontsize=fs)
        plt.savefig('./CSI.png',bbox_inches='tight')
        plt.show()


