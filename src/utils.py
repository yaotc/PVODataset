import datetime, pytz
import numpy as np


def str_2_utc(time_str:str)->datetime:
    naive_time = datetime.datetime.strptime(time_str,'%Y-%m-%d %H:%M:%S')
    utctime = datetime.datetime(naive_time.year,naive_time.month,naive_time.\
                                day,naive_time.hour,naive_time.minute,tzinfo=pytz.timezone('UTC'))
    return utctime

def pk_2_utc(pktime_str:str)->datetime:
    '''
    transfer PK to UTC , format: yyyy-m-d H-m-s
    '''
    naive_time = datetime.datetime.strptime(pktime_str,'%Y-%m-%d %H:%M:%S')
    pktime = naive_time.astimezone(pytz.timezone('Asia/Shanghai'))
    utctime = pktime.astimezone(pytz.timezone('UTC'))
    return utctime


def utc_2_pk(utctime_str:str)->datetime:
    '''
    transfer UTC to PK , format: yyyy-m-d H-m-s
    '''
    naive_time = datetime.datetime.strptime(utctime_str,'%Y-%m-%d %H:%M:%S')
    utctime = datetime.datetime(naive_time.year,naive_time.month,naive_time.\
                                day,naive_time.hour,naive_time.minute,tzinfo=pytz.timezone('UTC'))
    pktime = utctime.astimezone(pytz.timezone('Asia/Shanghai'))
    return pktime



def MAPE(y, pred):
    y = np.array(y)
    pred = np.array(pred)
    ans = []
    for i,j in enumerate(y):
        if pred[i] is np.NaN:
            print("keke")
    for i,j in enumerate(y):
        if y[i] and pred[i] and not np.isnan(pred[i]):
            ans.append(np.abs(y[i] - pred[i])/ y[i])
    return np.sum(ans)/ len(ans) * 100

def RMSE(y, pred):
    y = np.array(y)
    pred = np.array(pred)
    ans = []
    for i,j in enumerate(y):
        if not np.isnan(pred[i]):
            ans.append(np.abs(y[i] - pred[i])**2)
    return np.sqrt(np.sum(ans)/ len(ans))

def MAE(y, pred):
    y = np.array(y)
    pred = np.array(pred)
    ans = []
    for i,j in enumerate(y):
        if not np.isnan(pred[i]):
            ans.append(np.abs(y[i] - pred[i]))
    return np.sum(ans)/ len(ans) 
