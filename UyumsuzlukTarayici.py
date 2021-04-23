import os
import pandas as pd
from binance.client import Client
from datetime import datetime
import pandas_ta as ta
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
import numpy as np


pathList = os.listdir()

filePath = os.getcwd()
coinPath = filePath +  "/coinList.txt"
apiPath = filePath + "/coinApi.txt"

key_secret = pd.read_csv(apiPath,header=None)
coins = pd.read_csv(coinPath , header=None)
coins = coins.iloc[:,0].str.strip()
coins = coins.values.reshape(-1,)
coinsTemp = []
for co in coins:
    if "USDT" in co:
        coinsTemp.append(co)
coins = coinsTemp
    

api_key = key_secret.loc[0].values[0].split("=")[1].strip()
api_secret = key_secret.loc[1].values[0].split("=")[1].strip()


client = Client(api_key, api_secret , {"verify": True, "timeout": 20})

columns = ["Date","Open","High","Low","Close","VolXmr","gereksiz1","Volume","Islem","Hacim1","Hacim2","gereksiz5"]
gereksiz = ["VolXmr","gereksiz1","Islem","Hacim1","Hacim2","gereksiz5"]




print("Toplam" , len(coins), "USDT çifti bulundu.")
print("Coinler taranıyor... Lütfen bekleyiniz.")
print("")


Uyumsuzluk15dk = pd.DataFrame([],columns=["COINS"])


for index,coin in enumerate(coins):
   
    try:
        row = {'COINS':coin}
        kripto = coin

        dakika15 = client.get_historical_klines(kripto, Client.KLINE_INTERVAL_15MINUTE, "8 hours ago UTC")    #veri çek
        dakika15 = pd.DataFrame(dakika15 , columns=columns ).drop(columns=gereksiz)
        dakika15.Date = (dakika15.Date/1000).apply(datetime.fromtimestamp)
        dakika15 = dakika15.set_index(dakika15.Date).drop(columns=["Date"])
        dakika15 = dakika15.astype(float)
        dakika15 = dakika15.reset_index(drop=True)

        df = dakika15.copy()
        df.ta.rsi(append=True)
        df.drop(columns=["open","high","low","volume",],inplace=True)
        df.dropna(inplace=True)
       
        close_val = df.close.values
        rsi_val = df.RSI_14.values
        
        lmax = argrelextrema(close_val, np.greater)[0][-2:]
        lmin = argrelextrema(close_val, np.less)[0][-2:]

        
        def findPrc(seriMax,seriMin,rsiMax,rsiMin ,lmaxx , lminn , lenC):
            try:
                sMax = (seriMax[1] / seriMax[0] -1)*100
                sMin = (seriMin[1] / seriMin[0] -1)*100
                rMax = rsiMax[1] - rsiMax[0] 
                rMin = rsiMin[1] - rsiMin[0] 
                
                
                if lmaxx[-1] > lminn[-1] and int(lmaxx[-1]) == int(lenC-2):
                    if np.sign(sMax) != np.sign(rMax):
                        if np.abs(sMax) > 1 and np.abs(rMax) > 5:
                            #print(sMax,sMin,rMax,rMin)
                            return "Ayı Uyumsuzluğu Olabilir"
                
                
                elif lmaxx[-1] < lminn[-1] and int(lminn[-1]) == int(lenC-2):
                    if np.sign(sMin) != np.sign(rMin):
                        if np.abs(sMin) > 1 and np.abs(rMin) > 5:
                            #print(sMax,sMin,rMax,rMin)
                            return "Boğa Uyumsuzluğu Olabilir"
    

                return "Uyumsuzluk Yok"
            
            except:
                return "Uyumsuzluk Yok"
            
            
            
        cevap = findPrc(close_val[lmax],close_val[lmin],rsi_val[lmax],rsi_val[lmin],lmax,lmin,len(close_val))
  
        if cevap != "Uyumsuzluk Yok":
    
        
            fig, axs = plt.subplots(2 , figsize=(5,6))
            fig.suptitle("{}' da {}".format(kripto,cevap))
            fig.tight_layout()
    
               
            if cevap == "Boğa Uyumsuzluğu Olabilir":
                
                axs[0].plot(close_val,color="darkblue")
                axs[0].scatter(lmin,close_val[lmin] , color="lightgreen" , s=300)
                axs[0].plot(lmin,close_val[lmin] , color="lightgreen")
                axs[0].set_title("Close {}".format(close_val[-1]))
                    
                axs[1].plot(rsi_val , color="darkblue")
                axs[1].scatter(lmin,rsi_val[lmin] , color="lightgreen" , s=300)
                axs[1].plot(lmin,rsi_val[lmin] , color="lightgreen")
                axs[1].set_title("RSI-14")
            
            if cevap == "Ayı Uyumsuzluğu Olabilir":
                
                axs[0].plot(close_val,color="darkblue")
                axs[0].scatter(lmax,close_val[lmax] , color="red" , s=300)
                axs[0].plot(lmax,close_val[lmax] , color="red")
                axs[0].set_title("Close {}".format(close_val[-1]))
                
                axs[1].plot(rsi_val , color="darkblue")
                axs[1].scatter(lmax,rsi_val[lmax] , color="red" , s=300)
                axs[1].plot(lmax,rsi_val[lmax] , color="red")
                axs[1].set_title("RSI-14")
                
            
            plt.show()
        
    except:
        print("HATA")
        pass

    print(index+1, "- " ,coin, " tarandı." , sep="")


print("")
print("Tarama tamamlandı.")

#coinsAylik.to_csv(filePath + "/Gunluk_Bar_Aylik_Pivot.csv" , index=False)





