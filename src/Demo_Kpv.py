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
    

    def read_weather(self, path='../datasets/McClear/s7_clr_data_17-19.csv'):
        """
        periods = 500 S5.  96 (S7,S8)
        """
        s_clr = pd.read_csv(path)
        times = pd.date_range('03-16-2018 16:00', freq='15min', periods=96*2, tz="UTC") #
        weather = pd.DataFrame(columns=['ghi', 'dni', 'dhi'], index=times)
        weather['dni'] = np.array(s_clr['BNI'])
        weather['ghi'] = np.array(s_clr['GHI'])
        weather['dhi'] = np.array(s_clr['DHI'])
        return weather
    
    def init_PV_sys(self):

        temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        module_parameters = pvsystem.retrieve_sam('CECMod')['Yingli_Energy__China__YL250P_29b']
        ivt_para = pvsystem.retrieve_sam('cecinverter')['Advanced_Energy_Industries__Solaron_500kW__3159500_XXXX___480V_']
        ivt_para["Pdco"], ivt_para['Vdco'], ivt_para["Vdcmax"], ivt_para['Idcmax'], = 567000, 315, 1000, 1134
        ivt_para["Mppt_low"], ivt_para['Mppt_high'] = 460, 950
        inverter_parameters = ivt_para
        system = PVSystem(surface_tilt=33, surface_azimuth=180,
                          module_parameters=module_parameters,
                          inverter_parameters=inverter_parameters,
                          modules_per_string=20, strings_per_inverter=100,
                          temperature_model_parameters=temperature_model_parameters)
        
        lat, lon = 36.64403, 113.64187 # S7 
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
        K_pv, pltac= [], []
        all_ac = np.array(mc.ac)
        for i in range(len(all_ac)):
            ac_i = all_ac[i] / 1e6 * 135
            # 135 is an estimated value based on the installed capacity of the station and the arrangement of PV panels, and each station is different.
            pltac.append(ac_i)
            if ac_i <= 1:
                K_pv.append(0)
            else:
                K_pv.append(power[i]/ac_i)

        return K_pv, pltac, power, tmp_time
    
    
    def plot_kpv(self, K_pv, tmp_time, start, end):
        fs = 24
        lines = [1 for i in range(len(K_pv))]
        plt.figure(figsize=(10,6),dpi=300)

        plt.plot(K_pv,  'g-.')
        # plt.plot(pltac, 'b--')
        plt.plot(lines,  'k--', linewidth=1)
        # 24 h ( 15m resolution) = 24 * 6 = 96 timesteps 
        plt.xticks(list(range(start, end, 96)), tmp_time)

        plt.grid(ls='--')
        plt.xlim(start, end)
        plt.yticks(size = fs)
        plt.xticks(size = fs)
        plt.ylabel('K$_{PV}$',fontsize=fs)
        plt.xlabel('Time step (15-min)',fontsize=fs)
        # plt.savefig("./Kpv_S7_cloudy.pdf", bbox_inches='tight',format='pdf')
        plt.show()

    def plot_clr(self, power, pltac, tmp_time, start, end):
        plt.rc('font',family='Times New Roman')
        plt.figure(figsize=(10,6),dpi=300)
        fs = 24
        line0, = plt.plot(power, color='#D94E5D', linestyle='-')
        line1, = plt.plot(pltac, color='blue', linestyle='--')

        for i in list(range(start, end-96, 96)):
            right_ = i + 96 if i+96 <= end else end
            rmse = RMSE(power[i:right_], pltac[i:right_])
            mae = MAE(power[i:right_], pltac[i:right_])
            mape = MAPE(power[i:right_], pltac[i:right_])
#             plt.text(i+37, 4, f'MAPE:{round(mape,1)}%', size = fs)
#             plt.text(i+37, 3, f'RMSE:{round(rmse,1)}' , size = fs)
#             plt.text(i+37, 2, f'MAE  :{round(mae ,1)}' , size = fs)

        plt.grid(ls='--')
        plt.xlim(start, end)
        plt.yticks(size = fs)
        plt.xticks(size = fs)
        plt.ylim(-1,17)
        plt.legend(handles=[line0, line1], labels=['PV_MEAS','PV_CLR'], loc='best',fontsize=fs)
        plt.xticks(list(range(start, end, 96)), tmp_time)
        plt.ylabel('Power (MW)',fontsize=fs)
        plt.xlabel('Time step (15-min)',fontsize=fs)
        # plt.savefig('./CSI_S7_cloudy.pdf', bbox_inches='tight',format='pdf')
        plt.show()
