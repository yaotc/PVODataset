import pandas as pd
import os
import numpy as np
import math
import matplotlib.pyplot as plt
from utils import MAPE, RMSE, MAE

import pvlib
from pvlib import location
from pvlib import irradiance
from pvlib import pvsystem 
import datetime
from pysolar.solar import radiation, get_altitude
import pytz

from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain

from pvodataset import PVODataset



class demo_K_PV(PVODataset):
    """
    The usage of Inheritance grammar.
    Follow Open-Closed Principle and Single Responsibility Principle.
    Note: start - end >= 96. (24h with 15m resolution) = 24*6 = 96 timesteps.)
    
    Please modify the pdc0 in Func(init_PV_sys), longitude, latitude in Func(get_dir_rad).
    """ 
    def __init__(self, path='../datasets/', timezone="UTC",params=0):
        super(demo_K_PV, self).__init__(path) 
        self.tz = timezone
        print(self.tz)
        pass
    
    def init_PV_sys(self):

        module_parameters = {'pdc0': 30, 'gamma_pdc': -0.005}
        inverters = pvsystem.retrieve_sam('cecinverter')
        inverter_parameters = inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']
        system = pvsystem.PVSystem(module_parameters=module_parameters,
                                   inverter_parameters=inverter_parameters,
                           surface_tilt=33, surface_azimuth=180)
        return system

        
    def read_weather(self, path='../datasets/McClear/s5_clr_data.csv'):
        """
        periods = 500 S5.  96( S7,S8)
        """
        s_clr = pd.read_csv(path)
        times = pd.date_range('03-04-2018 16:00', freq='15min', periods=500, tz="UTC") #
        weather = pd.DataFrame(columns=['ghi', 'dni', 'dhi'], index=times)
        weather['dni'] = np.array(s_clr['BNI'])
        weather['ghi'] = np.array(s_clr['GHI'])
        weather['dhi'] = np.array(s_clr['DHI'])
        return weather
    
    def init_PV_sys(self):

        temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        module_parameters = {'pdc0': 119, 'gamma_pdc': -0.005}
        inverter_parameters = {'pdc0': 119}
        system = PVSystem(surface_tilt=33, surface_azimuth=180,
                          module_parameters=module_parameters,
                          inverter_parameters=inverter_parameters,
                          temperature_model_parameters=temperature_model_parameters)
        
        # For this example, we will be using Golden, Colorado
        lat, lon = 38.2355 , 114.1236 # S5 pdc0 = 119
#         lat, lon = 36.64403, 113.64187 # S7 pdc0 = 53
#         lat, lon = 36.70761, 113.89999 # S8 Pdc0 = 56
        site = location.Location(lat, lon, tz='UTC')

        mc = ModelChain(system, site, transposition_model='perez',
                        solar_position_method='nrel_numpy',
                        orientation_strategy='south_at_latitude_tilt',
                        aoi_model='physical', spectral_model='no_loss')
        
        mc.run_model(self.read_weather())
        return mc

    
#     def calc_PV_clr(self, irra_poa, temp_cell, system):

#         pdc = system.pvwatts_dc(g_poa_effective=irra_poa, temp_cell=temp_cell)
#         return pdc
    
#     def get_dir_rad(self, date):
#         """
#         Clear-sky model.
#         """
#         date = datetime.datetime.strptime(str(date), "%Y-%m-%d %H:%M")
#         longitude_deg, latitude_deg = 114.1236, 38.2355 # s5
#         date = datetime.datetime(date.year, date.month, date.day, \
#                                  date.hour, date.minute, tzinfo=pytz.timezone('Asia/Shanghai'))
#         altitude_deg = get_altitude(latitude_deg, longitude_deg, date)
        
#         irr = radiation.get_radiation_direct(date, altitude_deg)
# #         print(altitude_deg, irr)
#         return irr

    # users-defined demo1

    def range_calc_KPV(self, ori_data, start, end):
        power = ori_data["power"][start:end].reset_index(drop=True)
#         irra_poa = ori_data["lmd_totalirrad"][start:end].reset_index(drop=True)
        temp_cell = ori_data["lmd_temperature"][start:end].reset_index(drop=True)
        datet = ori_data["date_time"][start:end].reset_index(drop=True)
        datet = [str(i)[:-3-6] for i in datet]
        # 24 h ( 15m resolution) = 24 * 6 = 96 timesteps 

        tmp_time = [datet[i] for i in list(range(start, end, 96))]
        mc  = self.init_PV_sys()
        K_pv = []
        all_dc = np.array(mc.dc)
        for i in range(len(all_dc)):
            if all_dc[i] < 1:
                K_pv.append(0)
            else:
                K_pv.append(power[i]/all_dc[i])

        return K_pv, all_dc, power, tmp_time
    
    
    def plot_kpv(self, K_pv, tmp_time, start, end):
        
        fs = 12
        lines = [1 for i in range(len(K_pv))]
        plt.figure(figsize=(24,8),dpi=300)

        plt.plot(K_pv,  'g-.')
        # plt.plot(pltpdc, 'b--')
        plt.plot(lines,  'k--', linewidth=1)
        # 24 h ( 15m resolution) = 24 * 6 = 96 timesteps 
        plt.xticks(list(range(start, end, 96)), tmp_time)

        plt.grid(ls='--')
        plt.xlim(start, end)
        plt.yticks(size = fs)
        plt.xticks(size = fs)
        plt.ylabel('K$_{PV}$',fontsize=fs)
        plt.xlabel('Time step (15-min)',fontsize=fs)
#         plt.savefig("./Kpv_S7.pdf", bbox_inches='tight',format='pdf')
        plt.show()


    def plot_clr(self, power, pltpdc, tmp_time, start, end):
        plt.rc('font',family='Times New Roman')
        plt.figure(figsize=(24,8),dpi=300)
        fs = 12
        line0, = plt.plot(power, color='#D94E5D', linestyle='-')
        line1, = plt.plot(pltpdc, color='blue', linestyle='--')

        for i in list(range(start, end-96, 96)):
            right_ = i + 96 if i+96 <= end else end
            rmse = RMSE(power[i:right_], pltpdc[i:right_])**0.5
            mae = MAE(power[i:right_], pltpdc[i:right_])
            mape = MAPE(power[i:right_], pltpdc[i:right_])
            plt.text(i+37, 4, f'MAPE:{round(mape,1)}%', size = fs)
            plt.text(i+37, 3, f'RMSE:{round(rmse,1)}' , size = fs)
            plt.text(i+37, 2, f'MAE  :{round(mae ,1)}' , size = fs)

        plt.grid(ls='--')
        plt.xlim(start, end)
        plt.yticks(size = fs)
        plt.xticks(size = fs)
        plt.legend(handles=[line0, line1], labels=['S7_PV_MEAS','S7_PV_CLR'], loc='upper left',fontsize=fs)
        plt.xticks(list(range(start, end, 96)), tmp_time)
        plt.ylabel('Power (W/M$^2$)',fontsize=fs)
        plt.xlabel('Time step (15-min)',fontsize=fs)
#         plt.savefig('./CSI_S7.pdf', bbox_inches='tight',format='pdf')
        plt.show()
    
    def plot_clr2(self, power, pltpdc, tmp_time, start, end, pdc2):
        plt.rc('font',family='Times New Roman')
        plt.figure(figsize=(24,8),dpi=300)
        fs = 12
        line0, = plt.plot(power, color='#D94E5D', linestyle='-')
        line1, = plt.plot(pltpdc, color='blue', linestyle='--')
#         line2, = plt.plot(pdc2, color='blue', linestyle='--')

#         for i in list(range(start, end-96, 96)):
#             right_ = i + 96 if i+96 <= end else end
#             rmse = RMSE(power[i:right_], pltpdc[i:right_])**0.5
#             mae = MAE(power[i:right_], pltpdc[i:right_])
#             mape = MAPE(power[i:right_], pltpdc[i:right_])
#             plt.text(i+37, 4, f'MAPE:{round(mape,1)}%', size = fs)
#             plt.text(i+37, 3, f'RMSE:{round(rmse,1)}' , size = fs)
#             plt.text(i+37, 2, f'MAE  :{round(mae ,1)}' , size = fs)

        plt.grid(ls='--')
        plt.xlim(start, end)
        plt.yticks(size = fs)
        plt.xticks(size = fs)
#         plt.legend(handles=[line0, line1, line2], labels=['S8_PV_MEAS','PV_EST', 'S8_PV_CLR'], loc='best',fontsize=fs)
        plt.legend(handles=[line0, line1], labels=['S8_PV_MEAS','PV_EST'], loc='upper left',fontsize=fs)

        plt.xticks(list(range(start, end, 96)), tmp_time)
        plt.ylabel('Power (W/M^2)',fontsize=fs)
        plt.xlabel('Time step (15-min)',fontsize=fs)
#         plt.savefig('./CSI_EST.pdf', bbox_inches='tight',format='pdf')
        plt.show()

