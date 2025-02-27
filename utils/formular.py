# -*- coding: utf-8 -*-
import  pandas as pd
import numpy  as np
import talib as ta
'''
用于将日线数据转换为周线、月线，计算ma、macd、ene等指标

'''

'''
  根据日线、5分线、实时数据获取macd等参数
'''


def MACD(df, n_fast=12, n_slow=26):
    EMAfast = df['close'].ewm(ignore_na=False, span=n_fast, min_periods=n_fast - 1, adjust=True).mean()
    EMAslow = df['close'].ewm(ignore_na=False, span=n_slow, min_periods=n_slow - 1, adjust=True).mean()
    df['diff'] = EMAfast - EMAslow
    df['dea'] = df['diff'].ewm(ignore_na=False, span=9, min_periods=8, adjust=True).mean()
    df['macd'] = 2 * (df['diff'] - df['dea'])
    return df


def ENE(df):
    ma11 = df['close'].rolling(window=11, center=False).mean()
    df['upper'] = float(1 + 10.0 / 100) * ma11
    df['lower'] = float(1 - 9.0 / 100) * ma11
    df['ene'] = (df['upper'] + df['lower']) / 2
    return df


def MA(df, ma_list=[5, 10, 20, 60]):
    for ma in ma_list:
        df['MA_' + str(ma)] = df['close'].rolling(window=ma, center=False).mean()
    return df

def KDJ_old(df,fastk=9):
    low = df['low'].rolling(window=fastk,min_periods=1,center=False).min()
    high = df['high'].rolling(window=fastk,min_periods=1,center=False).max()
    rsv  =(df['close'] - low)/ (high -low)*100
    df['KDJ_K'] = rsv.ewm(ignore_na=False,min_periods=0,adjust=True,com=2).mean()
    df['KDJ_D'] = df['KDJ_K'].ewm(ignore_na=False,min_periods=0,adjust=True,com=2).mean()
    df['KDJ_J'] = 3*df['KDJ_K'] - 2* df['KDJ_D']

    return df

'''
    將日線轉換為周線、月線
    return: OHLC,volume,price_change,p_change
'''
def resample(df, _period_='W'):
    dat = df.resample(_period_).last()

    dat['open'] = df['open'].resample(_period_).first()
    dat['high'] = df['high'].resample(_period_).max()
    dat['low'] = df['low'].resample(_period_).min()
    dat['volume'] = df['volume'].resample(_period_).sum()
    dat['close'] = df['close'].resample(_period_).last()
    if 'amount' in dat.columns:
        dat['amount'] = df['amount'].resample(_period_).sum()
        dat.dropna(inplace=True)
        return dat[['open', 'high', 'low',  'close','volume','amount']]
    #dat['price_change'] = df['price_change'].resample(_period_).sum()
    #dat['p_change'] = df['p_change'].resample(_period_).apply(lambda x: (x + 1.0).prod() - 1.0)
    dat.dropna(inplace=True)
    return dat[['open', 'high', 'low',  'close','volume']]

def EMA(DF, N):
    return  pd.Series.ewm(DF, span = N, min_periods = N - 1,adjust=True).mean()

def SMA(DF,N,M):
    DF = DF.fillna(0)
    z = len(DF)
    var = np.zeros(z)
    var[0] = DF[0]
    for i in range (1,z):
        var[i] = (DF[i] * M + var[i-1] *  (N - M)) / N
    for i in range(z):
        DF[i] =var[i]
    return DF


def ATR(DF,N):
    C = DF['close']
    H = DF['high']
    L = DF['low']
    TR1 = MAX(MAX((H-L),ABS(REF(C,1)- H)),ABS(REF(C,1)-L))
    atr =MA(TR1,N)
    return atr
def HHV(DF,N):
    return pd.Series.rolling( DF,N).max()
def LLV(DF,N):
    return pd.Series.rolling( DF,N).min()
def SUM (DF,N):
    return pd.Series.rolling(DF, N).sum()
def ABS (DF):
    return abs(DF)

def MAX (A,B):
    var = IF(A > B, A, B)
    return var
def MIN  (A,B):
    var = IF ( A < B ,A,B )
    return var
def IF (COND,V1,V2):
    var = np.where(COND, V1, V2)
    for i in range(len(var)):
        V1[i] = var[i]
    return V1

def REF(DF,N):
    var = DF.diff(N)
    var = DF - var
    return var
def STD(DF,N):
    return pd.Series.rolling( DF,N).std()

def MACD(DF,FAST,SLOW,MID):
    EMAFAST =EMA(DF,FAST)
    EMASLOW =EMA(DF,SLOW)
    DIFF = EMAFAST-EMASLOW
    DEA = EMA(DIFF,MID)
    MACD = (DIFF- DEA)*2
    DICT = {'DIFF': DIFF, 'DEA': DEA, 'MACD': MACD}
    VAR = pd.DataFrame(DICT)
    return VAR

def KDJ(DF,N,M1,M2):
    C = DF['close']
    H = DF['high']
    L = DF['low']
    RSV =(C- LLV(L,N))/(HHV(H,N)-LLV(L,N)) * 100
    K = SMA(RSV, M1,1)
    D = SMA(K,M2,1)
    J = 3 * K - 2 * D
    DICT = {'KDJ_K': K, 'KDJ_D': D,'KDJ_J': J}
    VAR = pd.DataFrame(DICT)
    return VAR

def OSC(DF,N,M):#变动速率线
    C=DF['close']
    OS = (C- MA(C,N))*100
    MAOSC = EMA(OS,M)
    DICT = {'OSC': OS,'MAOSC' : MAOSC}
    VAR = pd.DataFrame(DICT)
    return VAR

def BBI(DF,N1,N2,N3,N4):#多空指标
    C=DF['close']
    bbi =(MA(C,N1) + MA(C,N2) + MA(C,N3)+ MA(C,N4))/4
    DICT = {'BBI': bbi}
    VAR = pd.DataFrame(DICT)
    return VAR

def BBIBOLL(DF,N1,N2,N3,N4,N,M):#多空布林线
    bbiboll = BBI(DF,N1,N2,N3,N4)
    UPER = bbiboll + M * STD(bbiboll,N)
    DOWN = bbiboll - M * STD(bbiboll,N)
    DICT = {'BBIBOLL': bbiboll, 'UPER': UPER, 'DOWN': DOWN}
    VAR = pd.DataFrame(DICT)
    return VAR

def PBX(DF,N1,N2,N3,N4,N5,N6):#瀑布线
    C= DF['close']
    PBX1 = (EMA(C,N1) + EMA(C,2*N1) + EMA(C,4*N1) )/3
    PBX2 = (EMA(C,N2) + EMA(C,2*N2) + EMA(C,4*N2) )/3
    PBX3 = (EMA(C,N3) + EMA(C,2*N3) + EMA(C,4*N3) )/3
    PBX4 = (EMA(C,N4) + EMA(C,2*N4) + EMA(C,4*N4) )/3
    PBX5 = (EMA(C,N5) + EMA(C,2*N5) + EMA(C,4*N5) )/3
    PBX6 = (EMA(C,N6) + EMA(C,2*N6) + EMA(C,4*N6) )/3
    DICT = {'PBX1': PBX1, 'PBX2': PBX2,'PBX3': PBX3,'PBX4': PBX4,'PBX5': PBX5,'PBX6': PBX6}
    VAR = pd.DataFrame(DICT)
    return VAR

def BOLL(DF,N):#布林线
    C = DF['close']
    boll = MA(C,N)
    UB   = boll + 2 * STD(C,N)
    LB   = boll - 2 * STD(C,N)
    DICT = {'BOLL': boll, 'UB': UB, 'LB': LB}
    VAR = pd.DataFrame(DICT)
    return VAR

def ROC(DF,N,M):#变动率指标
    C = DF['close']
    roc = 100 * (C - REF(C,N)) / REF(C,N)
    MAROC = MA(roc,M)
    DICT = {'ROC': roc, 'MAROC': MAROC}
    VAR = pd.DataFrame(DICT)
    return VAR

def MTM(DF,N,M):#动量线
    C = DF['close']
    mtm = C - REF(C, N)
    MTMMA= MA(mtm, M)
    DICT = {'MTM': mtm, 'MTMMA': MTMMA}
    VAR = pd.DataFrame(DICT)
    return VAR

def MFI(DF,N):#资金指标
    C = DF['close']
    H = DF['high']
    L = DF['low']
    VOL = DF['vol']
    TYP = (C + H + L) / 3
    V1 = SUM(IF(TYP > REF(TYP, 1), TYP * VOL, 0), N) / SUM(IF(TYP < REF(TYP, 1), TYP * VOL, 0), N)
    mfi = 100 - (100 / (1 + V1))
    DICT = {'MFI': mfi}
    VAR = pd.DataFrame(DICT)
    return VAR

def SKDJ(DF,N,M):
    CLOSE = DF['close']
    LOWV = LLV(DF['low'], N)
    HIGHV =HHV(DF['high'], N)
    RSV = EMA((CLOSE - LOWV) / (HIGHV - LOWV) * 100, M)
    K = EMA(RSV, M)
    D = MA(K, M)
    DICT = {'SKDJ_K': K, 'SKDJ_D': D}
    VAR = pd.DataFrame(DICT)
    return VAR

def WR(DF,N,N1):#威廉指标
    HIGH = DF['high']
    LOW = DF['low']
    CLOSE = DF['close']
    WR1=100 * (HHV(HIGH, N) - CLOSE) / (HHV(HIGH, N) - LLV(LOW, N))
    WR2=100 * (HHV(HIGH, N1) - CLOSE) / (HHV(HIGH, N1) - LLV(LOW, N1))
    DICT = {'WR1': WR1, 'WR2': WR2}
    VAR = pd.DataFrame(DICT)
    return VAR

def BIAS(DF,N1,N2,N3):#乖离率
    CLOSE = DF['close']
    BIAS1=(CLOSE - MA(CLOSE, N1)) / MA(CLOSE, N1) * 100
    BIAS2=(CLOSE - MA(CLOSE, N2)) / MA(CLOSE, N2) * 100
    BIAS3=(CLOSE - MA(CLOSE, N3)) / MA(CLOSE, N3) * 100
    DICT = {'BIAS1': BIAS1, 'BIAS2': BIAS2, 'BIAS3': BIAS3}
    VAR = pd.DataFrame(DICT)
    return VAR

def RSI(DF,N1,N2,N3):#相对强弱指标RSI1:SMA(MAX(CLOSE-LC,0),N1,1)/SMA(ABS(CLOSE-LC),N1,1)*100;
    CLOSE =DF['close']
    LC=REF(CLOSE, 1)
    RSI1=SMA(MAX(CLOSE - LC, 0), N1, 1) / SMA(ABS(CLOSE - LC), N1, 1) * 100
    RSI2=SMA(MAX(CLOSE - LC, 0), N2, 1) / SMA(ABS(CLOSE - LC), N2, 1) * 100
    RSI3=SMA(MAX(CLOSE - LC, 0), N3, 1) / SMA(ABS(CLOSE - LC), N3, 1) * 100
    DICT = {'RSI1': RSI1, 'RSI2': RSI2, 'RSI3': RSI3}
    VAR = pd.DataFrame(DICT)
    return VAR

def ADTM(DF,N,M):#动态买卖气指标
    HIGH = DF['high']
    LOW = DF['low']
    OPEN = DF['open']
    DTM=IF(OPEN <= REF(OPEN, 1), 0, MAX((HIGH - OPEN), (OPEN - REF(OPEN, 1))))
    DBM=IF(OPEN >= REF(OPEN, 1), 0, MAX((OPEN - LOW), (OPEN - REF(OPEN, 1))))
    STM=SUM(DTM, N)
    SBM=SUM(DBM, N)
    ADTM1=IF(STM > SBM, (STM - SBM) / STM, IF( STM == SBM , 0, (STM - SBM) / SBM))
    MAADTM=MA(ADTM1, M)
    DICT = {'ADTM': ADTM1, 'MAADTM': MAADTM}
    VAR = pd.DataFrame(DICT)
    return VAR

def DDI(DF,N,N1,M,M1):#方向标准离差指数
    H = DF['high']
    L = DF['low']
    DMZ=IF((H + L) <= (REF(H, 1) + REF(L, 1)), 0, MAX(ABS(H - REF(H, 1)), ABS(L - REF(L, 1))))
    DMF=IF((H + L) >= (REF(H, 1) + REF(L, 1)), 0, MAX(ABS(H - REF(H, 1)), ABS(L - REF(L, 1))))
    DIZ=SUM(DMZ, N) / (SUM(DMZ, N) + SUM(DMF, N))
    DIF=SUM(DMF, N) / (SUM(DMF, N) + SUM(DMZ, N))
    ddi=DIZ - DIF
    ADDI=SMA(ddi, N1, M)
    AD=MA(ADDI, M1)
    DICT = {'DDI':ddi,'ADDI':ADDI,'AD':AD}
    VAR = pd.DataFrame(DICT)
    return VAR

def ADX(DF,N=14):
    H = DF['high']
    L = DF['low']
    C = DF['close']

    PDI = ta.PLUS_DI(H.values,L.values,C.values,N)

    MDI = ta.MINUS_DI(H.values,L.values,C.values,N)
    DX = ta.DX(H.values,L.values,C.values,N)
    ADX = ta.ADX(H.values,L.values,C.values,N)
    VAR = pd.DataFrame({'PDI':PDI,'MDI':MDI,'DX':DX,'ADX':ADX},index=H.index.values)
    return VAR
def AROON(DF,N=20):
    H = DF['high']
    L = DF['low']
    AD,AP = ta.AROON(H.values,L.values,N)
    AR = AP - AD
    VAR = pd.DataFrame({'AROON': AR, 'AROON_UP': AP, 'AROON_DOWN': AD}, index=H.index.values)
    return VAR
def CCI(DF,N=20):
    H = DF['high']
    L = DF['low']
    C = DF['close']
    CCI = ta.CCI(H.values, L.values, C.values, N)
    VAR = pd.DataFrame({'CCI': CCI}, index=H.index.values)
    return VAR

if __name__ == '__main__':

    import tushare as ts
    a =ts.get_k_data('600848')

    print(CCI(a).tail())