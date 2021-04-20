import os
import pandas as pd
from binance.client import Client
from datetime import datetime

pathList = os.listdir()

filePath = os.getcwd()
coinPath = filePath +  "/coinList.txt"
apiPath = filePath + "/coinApi.txt"

key_secret = pd.read_csv(apiPath,header=None)
coins = pd.read_csv(coinPath , header=None)
coins = coins.iloc[:,0].str.strip()
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

print("Toplam" , len(coins), "coin bulundu.")
print("Coinler taranıyor... Lütfen bekleyiniz.")
print("")

coinsAylik = pd.DataFrame([],columns=["COINS"])
coinsAylik2 = pd.DataFrame([],columns=["COINS"])
coinsHaftalik = pd.DataFrame([],columns=["COINS"])
coinsHaftalik2 = pd.DataFrame([],columns=["COINS"])
coinsGunluk = pd.DataFrame([],columns=["COINS"])
coins1saat = pd.DataFrame([],columns=["COINS"])
coins4saat = pd.DataFrame([],columns=["COINS"])
coinsHepsi = pd.DataFrame([],columns=["COINS"])



for index,coin in enumerate(coins):
    row = {'COINS':coin}
    kripto = coin
    
    try:
        aylik = client.get_historical_klines(kripto, Client.KLINE_INTERVAL_1MONTH, "2 month ago UTC")    #veri çek
        aylik = pd.DataFrame(aylik , columns=columns ).drop(columns=gereksiz)
        aylik.Date = (aylik.Date/1000).apply(datetime.fromtimestamp)
        aylik = aylik.set_index(aylik.Date).drop(columns=["Date"])
        aylik = aylik.astype(float)
        aylik = aylik.iloc[-2:,:]
        
        haftalik = client.get_historical_klines(kripto, Client.KLINE_INTERVAL_1WEEK, "2 week ago UTC")    #veri çek
        haftalik = pd.DataFrame(haftalik , columns=columns ).drop(columns=gereksiz)
        haftalik.Date = (haftalik.Date/1000).apply(datetime.fromtimestamp)
        haftalik = haftalik.set_index(haftalik.Date).drop(columns=["Date"])
        haftalik = haftalik.astype(float)
        haftalik = haftalik.iloc[-2:,:]

        gunluk = client.get_historical_klines(kripto, Client.KLINE_INTERVAL_1DAY, "2 day ago UTC")    #veri çek
        gunluk = pd.DataFrame(gunluk , columns=columns ).drop(columns=gereksiz)
        gunluk.Date = (gunluk.Date/1000).apply(datetime.fromtimestamp)
        gunluk = gunluk.set_index(gunluk.Date).drop(columns=["Date"])
        gunluk = gunluk.astype(float)
        gunluk = gunluk.iloc[-2:,:]
        
        saat4 = client.get_historical_klines(kripto, Client.KLINE_INTERVAL_4HOUR, "8 hour ago UTC")    #veri çek
        saat4 = pd.DataFrame(saat4 , columns=columns ).drop(columns=gereksiz)
        saat4.Date = (saat4.Date/1000).apply(datetime.fromtimestamp)
        saat4 = saat4.set_index(saat4.Date).drop(columns=["Date"])
        saat4 = saat4.astype(float)
        saat4 = saat4.iloc[-2:,:]
        
        saat1 = client.get_historical_klines(kripto, Client.KLINE_INTERVAL_1HOUR, "2 hour ago UTC")    #veri çek
        saat1 = pd.DataFrame(saat1 , columns=columns ).drop(columns=gereksiz)
        saat1.Date = (saat1.Date/1000).apply(datetime.fromtimestamp)
        saat1 = saat1.set_index(saat1.Date).drop(columns=["Date"])
        saat1 = saat1.astype(float)
        saat1 = saat1.iloc[-2:,:]
        

        pivotAylik = PPSR(aylik.iloc[0,:])
        pivotHaftalik = PPSR(haftalik.iloc[0,:])
        pivotGunluk = PPSR(gunluk.iloc[0,:])


        if gunluk.Close[1] > pivotAylik[0] and gunluk.Close[1] < pivotAylik[1]:
            coinsAylik = coinsAylik.append(row, ignore_index=True)
            if saat4.Close[1] > pivotAylik[0] and saat4.Close[1] < pivotAylik[1]:
                if saat4.Close[1] > pivotHaftalik[0] and saat4.Close[1] < pivotHaftalik[1]:
                    if saat1.Close[1] > pivotHaftalik[0] and saat1.Close[1] < pivotHaftalik[1]:
                        if saat1.Close[1] > pivotGunluk[0] and saat1.Close[1] < pivotGunluk[1]:
                            coinsHepsi = coinsHepsi.append(row, ignore_index=True)
                            
            
        
        ##########################
            
        if saat4.Close[1] > pivotAylik[0] and saat4.Close[1] < pivotAylik[1]:
            coinsAylik2 = coinsAylik2.append(row, ignore_index=True)
            if saat4.Close[1] > pivotHaftalik[0] and saat4.Close[1] < pivotHaftalik[1]:
                coins4saat = coins4saat.append(row, ignore_index=True)
            
        if saat4.Close[1] > pivotHaftalik[0] and saat4.Close[1] < pivotHaftalik[1]:
            coinsHaftalik = coinsHaftalik.append(row, ignore_index=True)
            
            
        ##########################
            
        if saat1.Close[1] > pivotHaftalik[0] and saat1.Close[1] < pivotHaftalik[1]:
            coinsHaftalik2 = coinsHaftalik2.append(row, ignore_index=True)
            if saat1.Close[1] > pivotGunluk[0] and saat1.Close[1] < pivotGunluk[1]:
                coins1saat = coins1saat.append(row, ignore_index=True)
            
        if saat1.Close[1] > pivotGunluk[0] and saat1.Close[1] < pivotGunluk[1]:
            coinsGunluk = coinsGunluk.append(row, ignore_index=True)
   
        

    
    except:
        pass
        
    print(index+1, "- " ,coin, " tarandı." , sep="")
    

print("")
print("Tarama tamamlandı.")

coinsAylik.to_csv(filePath + "/Gunluk_Bar_Aylik_Pivot.csv" , index=False)
coinsAylik2.to_csv(filePath + "/4_Saatlik_Bar_Aylik_Pivot.csv" , index=False)
coinsHaftalik.to_csv(filePath + "/4_Saatlik_Bar_Haftalik_Pivot.csv" , index=False)
coinsHaftalik2.to_csv(filePath + "/1_Saatlik_Bar_Haftalik_Pivot.csv" , index=False)
coinsGunluk.to_csv(filePath + "/1_Saatlik_Bar_Gunluk_Pivot.csv" , index=False)
coins1saat.to_csv(filePath + "/1_Saatlik_Bar_Haftalik_ve_Gunluk_Pivot.csv" , index=False)
coins4saat.to_csv(filePath + "/4_Saatlik_Bar_Haftalik_ve_Aylik_Pivot.csv" , index=False)
coinsHepsi.to_csv(filePath + "/Tum_Pivotlarin_Kosulunu_Saglayanlar.csv" , index=False)





