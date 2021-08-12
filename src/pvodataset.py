import pandas as pd
import os
import numpy as np
import math
from utils import str_2_utc, pk_2_utc, utc_2_pk


class PVODataset(object):
    def __init__(self, path='../datasets/', timezone="UTC", qc=False):
        self.path = path
        self.metadata = self.read_metadata()
#         print("Welcome to PVODataset (PVOD). The PVOD was constructed from 10 PV stations in Hebei, China, with 7 features of Numerical Weather Prediction (NWP), 5 features ofLocal measurements data (LMD), and PV output (Power). The PVOD has 271968 records over 1 year. Enjoy.")
        self.tz = timezone
        self.qc_flag = qc
        if self.tz not in ["UTC", "UTC+8"]:
                raise ValueError("Check Timezone.")
        print("Welcome to PVODataset (PVOD).")
        if self.qc_flag:
            print("Quality control is set to True.")

    
    def show_files(self):
        return list(os.listdir(self.path))
    
    def read_metadata(self):
        metadata = pd.read_csv(self.path + "metadata.csv")
        return metadata
    
    def utc_2_pk_pvod(self, data):
        data["date_time"] = data["date_time"].map(lambda x: utc_2_pk(str(x)))
        return data
    
    # QC funcs
    def qc_steps(self, ori_data):
        # 'phy' 
        E_0n = 1367
        Z = 33 
        ori_data = ori_data.loc[ (ori_data['lmd_totalirrad'] >= -4) & \
                           (ori_data['lmd_totalirrad'] <= 1.5 * ori_data['lmd_diffuseirrad'] * math.cos(math.radians(Z))**1.2 + 100) &\
                    (ori_data['lmd_diffuseirrad'] >= -4) &\
                     (ori_data['lmd_diffuseirrad'] <= 0.95 * ori_data['lmd_diffuseirrad'] * math.cos(math.radians(Z))**1.2 + 50)]
        #  'ext' 
        ori_data = ori_data.loc[ (ori_data['lmd_totalirrad'] > -4) & \
                           (ori_data['lmd_totalirrad'] < 1.5 * 1361  * math.cos(math.radians(Z))**1.2 + 100) &\
                    (ori_data['lmd_diffuseirrad'] > -4) &\
                     (ori_data['lmd_diffuseirrad'] < 0.95 * 1361  * math.cos(math.radians(Z))**1.2 + 50)]
        #  'closr' 
        ori_data = ori_data.loc[ (ori_data['lmd_totalirrad'] > 50) ]
        return ori_data
    
    def read_ori_data(self, station_id):
        """
        timezone : "UTC" or "UTC+8"(Asian/Shanghai)
        """
        ori_data = pd.read_csv(self.path + self.metadata["Station_ID"][station_id] + '.csv')
        if self.tz == "UTC+8":
            ori_data = self.utc_2_pk_pvod(ori_data)
        if self.tz == "UTC":
            ori_data["date_time"] = ori_data["date_time"].map(lambda x: str_2_utc(x))
        if self.qc_flag:
            ori_data = self.qc_steps(ori_data)
        return ori_data
    
    # Show abstract information
    def info(self):
        print("PVOD provides 1 metadata file and 10 PV station data files. The header of station files is : 'date_time', 'nwp_globalirrad', 'nwp_dirrectirrad', 'nwp_temperature', 'nwp_humidity', 'nwp_windspeed', 'nwp_winddirection', 'nwp_pressure','lmd_totalirrad', 'lmd_diffuseirrad', 'lmd_temperature', 'lmd_pressure','lmd_winddirection', 'lmd_windspeed', 'power'.\
              ")
        lens = 0
        for i in range(10):
            ori_data = self.read_ori_data(i)
            tmp = len(ori_data)
            lens += tmp
            print(f"-->Records of Station_{i} are {tmp}.")
        print(f"-> Total {lens} records.")
    
    
    # Show station original data information
    def station_info(self, station_id):
        ori_data = self.read_ori_data(station_id)
        return ori_data.describe()
    

    #
    def select_daterange(self, station_id, start_date, end_date):
        """
        input : station_id (int), start_date (Timestamp), end_date (Timestamp)
        output: select_data (DataFrame)
        """
        pd.set_option('display.max_columns', 9)
        ori_data = self.read_ori_data(station_id)
        if self.tz == "UTC+8":
            start_date = pd.to_datetime(start_date, utc=False).tz_localize('Asia/Shanghai')
            end_date   = pd.to_datetime(end_date  , utc=False).tz_localize('Asia/Shanghai')
        else:
            start_date = pd.to_datetime(start_date, utc=False).tz_localize('UTC')
            end_date   = pd.to_datetime(end_date  , utc=False).tz_localize('UTC')
        select_date_id = ori_data.loc[ (ori_data['date_time'] >= start_date) & (ori_data['date_time'] <= end_date)]
        return select_date_id

    # Date intersection 
    def date_intersection(self, station_id_a, station_id_b):
        """
        input : 2 station id, from 0 to 9 (int).
        output: date intersection between stations (string).
        """
        
        ori_data_a = self.read_ori_data(station_id_a)
        ori_data_b = self.read_ori_data(station_id_b)
        intersection = pd.merge(ori_data_a['date_time'],ori_data_b['date_time'], how='inner') 
        print(f"Station_{station_id_a}   : start: {list(ori_data_a['date_time'])[0]}, end: {list(ori_data_a['date_time'])[-1]}")
        print(f"Station_{station_id_b}   : start: {list(ori_data_b['date_time'])[0]}, end: {list(ori_data_b['date_time'])[-1]}")
        start, end = intersection['date_time'].iloc[0], intersection['date_time'].iloc[-1]
        print(f"intersection: start: {start}, end: {end}")
        
        return start, end
    
              
    def norm_dataframe(self, xy, mode="minmax"):
        data = xy.copy()
        if mode == "std":
            xy = (data - data.mean())/data.std()
            return np.array(xy)
        elif mode == "minmax":
            xy = (data-data.min())/(data.max()-data.min())
            return np.array(xy)
        else:
            raise "norm Error"
              
    def split_data(self, xy, mode="end_order", ratio=0.8):
        assert mode == "end_order", "Split Mode Error!"
        if mode == "end_order":
            train_data = xy[:int(xy.shape[0]*ratio)]
            test_data = xy[int(xy.shape[0]*ratio):]
            return train_data, test_data
        else:
            pass
              

              

class QCfunc(object):
    def __init__(self):
        pass

    def phy(self, mode='GHI',x=0, E_0n=0, Z=0):
        """
        mode = 'GHI', 'DHI', 'BNI'
        Z : radians
        """
        if mode == 'GHI':
              GHI = x
              return -4 < GHI < 1.5 * E_0n * math.cos(math.radians(Z))**1.2 + 100
        elif mode == 'DHI':
              DHI = x
              return -4 < DHI < 0.95 * E_0n * math.cos(math.radians(Z))**1.2 + 50
        elif mode == 'BNI':
              BNI = x
              return -4 < BNI < E_0n
        else:
              raise "MODE Check."
              
    def ext(self, mode='GHI',x=0, E_0n=0, Z=0):
        """
        mode = 'GHI', 'DHI', 'BNI'
        Z : radians
        """
        if mode == 'GHI':
              GHI = x
              return -2 < GHI < 1.5 * E_0n * math.cos(math.radians(Z))**1.2 + 50
        elif mode == 'DHI':
              DHI = x
              return -2 < DHI < 0.95 * E_0n * math.cos(math.radians(Z))**1.2 + 30
        elif mode == 'BNI':
              BNI = x
              return -2 < BNI < 0.95 * E_0n * math.cos(math.radians(Z))**1.2 + 10 
        else:
              raise "MODE Check."
              
class UDFClass(PVODataset):
    """
    The usage of Inheritance grammar.
    Follow Open-Closed Principle and Single Responsibility Principle.
    """ 
    def __init__(self, path='../datasets/', params=0):
        super(UDFClass, self).__init__(path) 
        pass
    
    # user-defined demo0
    def calcuate(self, station_id, param0, param1):
        meta_id = self.metadata.loc[station_id]
        value0, value1 = meta_id[param0], meta_id[param1]
        area = value0 * value1  
        print(f"area = {area} m^2.")
        return area
    
    # users-defined demo1
    def get_id_metedata(self, station_id):
        return self.metadata.loc[station_id]
              
              
              