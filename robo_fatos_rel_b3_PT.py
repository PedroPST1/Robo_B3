import requests
from bs4 import BeautifulSoup
import sys
import re
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time
import win32api
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import winsound

def codigo_ativo(title):   
    found = re.findall('(\(\w+)', title)  #string
    if len(found) > 0:
        return found[0].replace('(', '').replace(')', '')[0:4] #troca
    return None


def sendmail(ticker, dt, title, url):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('alertarelease', 'Pedroca_teste')  #Acessa

    subject = f"{dt} - Novo Documento: {ticker}"
    body = f"{ticker}\n{title}\n{url}"              #Preenche
    
    msg = f'Subject: {subject}\n\n\n{body}'
    server.sendmail(
        'alertarelease@gmail.com',
        'pedro.teixeira@dexcapital.com.br',
        msg                                         #Enviar
    )
    print("Email enviado")



daily_ids = list()

#URL = f"https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias?agencia=18&dataInicial=2021-08-20&dataFinal=2021-08-20"

while True:
    date = datetime.today()
    URL = f"https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/ListarTitulosNoticias?agencia=18&dataInicial={date.strftime(format='%Y-%m-%d')}&dataFinal={date.strftime(format='%Y-%m-%d')}"
    page = requests.get(URL, verify = False)
    soup = BeautifulSoup(page.content, 'html.parser')           #StockOverflow

    daily_news = json.loads(soup.contents[0])   #html código jv

    news_lines = list()
    for news in daily_news:             
        #print(news)
        item = news['NwsMsg']
        dt_time = item['dateTime']
        title = item['headline']
        item_id = item['id']
        ativo = codigo_ativo(title)
        news_url = f"https://sistemasweb.b3.com.br/PlantaoNoticias/Noticias/Detail?idNoticia={item_id}&agencia=18&dataNoticia={dt_time.split(' ')[0]}"
        #print(, title, news_url)
        line = dict()
        line['DATE'] = dt_time
        line['ATIVO'] = ativo
        line['TITLE'] = title
        line['ID'] = item_id
        line['URL'] = news_url
        news_lines.append(line)

    all_daily_news = pd.DataFrame(news_lines)
    all_daily_news['DATE'] = pd.to_datetime(all_daily_news['DATE'], format="%Y-%m-%d %H:%M:%S")
    all_daily_news.set_index('DATE', inplace=True)
    
    temp_daily_ids = list(all_daily_news.ID.unique())
    
    new_ids = list(set(temp_daily_ids) - set(daily_ids))
    
    
    #tickers_to_filter = ['CRFB','GMAT','LREN','SOMA','ARZZ','NTCO','RADL','HYPE']
    tickers_to_filter = ['B3SA','TOTS','DXCO','SULA','MGLU','HAPV','FLRY','ABEV','EQTL','WEGE','PSSA','BPAC','MOVI','RENT','VAMO','AERI','BOAS','CRFB','GMAT','LREN','NTCO','RADL','HYPE', 'ALPA','ESPA','VALE','AMBP','LWSA']
    all_daily_news = all_daily_news.loc[all_daily_news.ATIVO.isin(tickers_to_filter)]
    
    filtered = all_daily_news.loc[all_daily_news.ID.isin(new_ids)]
    for index, row in filtered.iterrows():        #matriz no código
        daily_ids.append(row['ID'])
        print(index,'-',row['ATIVO'],'-',row['TITLE'],'-',row['URL'])
        winsound.PlaySound('cashtill.wav', winsound.SND_FILENAME)
        sendmail(row['ATIVO'], index,row['TITLE'],row['URL'])
        #win32api.MessageBox(0, row['ATIVO'], row['TITLE'], 0x00001000)
    time.sleep(300)
    