import os
import pandas as pd
from binance.client import Client
from datetime import datetime

pathList = os.listdir()

filePath = os.getcwd()
coinPath = filePath +  "\coinlist.txt"
apiPath = filePath + "\coinApi.txt"

key_secret = pd.read_csv(apiPath,header=None)
coins = pd.read_csv(coinPath , header=None)
coins = coins.values.reshape(-1,)


api_key = key_secret.loc[0].values[0].split("=")[1].strip()
api_secret = key_secret.loc[1].values[0].split("=")[1].strip()

client = Client(api_key, api_secret , {"verify": True, "timeout": 20})

columns = ["Date","Open","High","Low","Close","VolXmr","gereksiz1","Volume","Islem","Hacim1","Hacim2","gereksiz5"]
gereksiz = ["Open","VolXmr","gereksiz1","Volume","Islem","Hacim1","Hacim2","gereksiz5"]


def PPSR(df):  
    PP = pd.Series((df['High'] + df['Low'] + df['Close']) / 3)  
    R1 = pd.Series(2 * PP - df['Low'])  
    #S1 = pd.Series(2 * PP - df['High'])  
    #R2 = pd.Series(PP + df['High'] - df['Low'])  
    #S2 = pd.Series(PP - df['High'] + df['Low'])  
    #R3 = pd.Series(df['High'] + 2 * (PP - df['Low']))  
    #S3 = pd.Series(df['Low'] - 2 * (df['High'] - PP))  
    psr = {'PP':PP, 'R1':R1}#, 'S1':S1, 'R2':R2, 'S2':S2, 'R3':R3, 'S3':S3}  
    PSR = pd.DataFrame(psr)  
    #df = df.join(PSR)  
    return PSR.values[0]

print("")
print("Toplam" , len(coins), "coin bulundu.")
print("Coinler taranıyor... Lütfen bekleyiniz.")

targetCoins = pd.DataFrame([],columns=["COINS","ANLIK","P-M","R1-M"])

for index,coin in enumerate(coins):
    kripto = coin
    
    try:
        aylik = client.get_historical_klines(kripto, Client.KLINE_INTERVAL_1MONTH, "2 month ago UTC")    #veri çek
        aylik = pd.DataFrame(aylik , columns=columns ).drop(columns=gereksiz)
        aylik.Date = (aylik.Date/1000).apply(datetime.fromtimestamp)
        aylik = aylik.set_index(aylik.Date).drop(columns=["Date"])
        aylik = aylik.astype(float)
        aylik = aylik.iloc[-2:-1,:]


        gunluk = client.get_historical_klines(kripto, Client.KLINE_INTERVAL_1DAY, "1 day ago UTC")    #veri çek
        gunluk = pd.DataFrame(gunluk , columns=columns ).drop(columns=gereksiz)
        gunluk.Date = (gunluk.Date/1000).apply(datetime.fromtimestamp)
        gunluk = gunluk.set_index(gunluk.Date).drop(columns=["Date"])
        gunluk = gunluk.astype(float)
        

        pivots = PPSR(aylik)

        print(gunluk.Close[0])
        print(pivots[0])
        print(pivots[1])
        if gunluk.Close[0] > pivots[0] and gunluk.Close[0] < pivots[1]:
            row = {'COINS':coin , 'ANLIK':gunluk.Close[0], 'P-M':pivots[0], 'R1-M':pivots[1]}
            targetCoins = targetCoins.append(row, ignore_index=True)
            print("sa")
    
    except:
        pass
        
    print(index+1, "- " ,coin, " tarandı." , sep="")
    

print("")
print("Tarama tamamlandı.")

targetCoins.to_csv(filePath + "\TaramaSonuclariAylik.csv" , index=False)

