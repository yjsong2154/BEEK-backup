#!/usr/bin/env python
# coding: utf-8

# 하루 평균 데이터 수집

# In[1]:


import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib import parse


# In[2]:


import datetime
from datetime import timedelta

now = datetime.datetime.now()
delta = timedelta(days=1)
yesterday = now - delta
yesterday_str = yesterday.strftime('%Y%m%d')
yesterday_dash = yesterday.strftime('%Y-%m-%d')

print(yesterday)


# In[3]:


CSV_ROOT = './savedata/avg_data_save.csv'

pre_save_data = pd.read_csv(CSV_ROOT)
pre_save_data = pre_save_data[['city', 'date','SO2', 'O3', 'NO2', 'PM10', 'PM25', 'avg temp', 'max temp', 'min temp', 'rain', 'wind', 'humid']]
pre_save_data.sort_values(by=['date','city'])

last_day = pre_save_data.iat[-1,1]

pre_save_data.tail()


# In[4]:


def crawling_weather(loc_code, date):
    param = {
        'ServiceKey' : 'dLeJY56I9i5QWd6UksGvqxOsIKaVQ3Aa9rNJZW3rOlPd6FBEoTlhtmmjMsghEicTUqb64WaPkNqv852BGEBLIA=='
        , 'pageNo' : '1'
        , 'numOfRows' : '1'
        , 'dataType' : 'XML'
        , 'dataCd' : 'ASOS'
        , 'dateCd' : 'DAY'
        , 'startDt' : date
        , 'endDt' : date
        , 'stnIds' : str(loc_code)
    }
    p_param = parse.urlencode(param)

    url = 'http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList'

    request_info = requests.get(url + '?' + p_param)
    soup = BeautifulSoup(request_info.text, 'html.parser')
    
    return soup


# In[5]:


def crawling_dust(loc_name, date):
    param = {
        'serviceKey' : 'dLeJY56I9i5QWd6UksGvqxOsIKaVQ3Aa9rNJZW3rOlPd6FBEoTlhtmmjMsghEicTUqb64WaPkNqv852BGEBLIA=='
        , 'returnType' : 'XML'
        , 'numOfRows' : '10'
        , 'pageNo' : '1'
        , 'inqBginDt' : date
        , 'inqEndDt' : date
        , 'msrstnName' : loc_name
    }
    p_param = parse.urlencode(param)

    url = 'http://apis.data.go.kr/B552584/ArpltnStatsSvc/getMsrstnAcctoRDyrg'

    request_info = requests.get(url + '?' + p_param)
    soup = BeautifulSoup(request_info.text, 'html.parser')
    
#     print(soup.prettify())
    
    return soup


# In[6]:


def listing_bs(raw_bs):
    items = raw_bs.select('item')
    return_arr = []
    
    arr_code = [
        'stnnm' , 'tm' , 'avgTa' , 'maxTa', 'minTa' , 'sumRn' , 'avgWs' , 'avgRhm'
    ]
    
    for item in items:
        temp_arr = []
        for key in arr_code:
            sel_data = item.select_one(key).string
            if sel_data is not None:
                temp_arr.append(sel_data)
            else:
                temp_arr.append(None)
        return_arr.append(temp_arr)
        
    return return_arr


# In[7]:


def listing_bs_dust(raw_bs):
    items = raw_bs.select('item')
    return_arr = []
    
    arr_code = [
        'msrstnname' , 'msurdt' , 'so2value' , 'o3value', 'no2value' , 'pm10value' , 'pm25value'
    ]
    
    for item in items:
        temp_arr = []
        for key in arr_code:
            sel_data = item.select_one(key).string
            if sel_data is not None:
                temp_arr.append(sel_data)
            else:
                temp_arr.append(None)
        return_arr.append(temp_arr)
        
    return return_arr


# In[8]:


arr_col = [ 'city', 'date', 'avg temp', 'max temp', 'min temp', 'rain', 'wind', 'humid' ]

loc_arr = [105,90,93,98,119,99,284,192,279,272,174,165,258,189,251,140,146,238,235
           ,236,226,221,131,156,143,133,159,108,152,112,184]

weather_list = []

for loc_code in loc_arr:
    weather_html = crawling_weather(loc_code, yesterday_str)
    weather_list.extend(listing_bs(weather_html))
    print('loc :', loc_code ,'complete')


# In[9]:


arr_col_dust = [ 'city', 'date', 'SO2', 'O3', 'NO2', 'PM10', 'PM25' ]

loc_names = ['강남구','강동구','강북구' #서울
             ,'가평','기흥','수지' #경기
             ,'검단','논현','부평' #인천
             ,'금호동','상리','인제읍' #강원
             ,'공주','내포','논산' #충남
             ,'구성동','문창동','정림동' #대전
             ,'가덕면','단양읍','사천동' #충북
             ,'개금동','대신동','덕포동' #부산
             ,'농소동','삼남읍','약사동' #울산
             ,'다사읍','본동','유가읍' #대구
             ,'가흥동','대송면','명륜동' #경북
             ,'거창읍','명서동','북부동' #경남
             ,'고흥읍','담양읍','보성읍' #전남
             ,'건국동','두암동','유촌동' #광주
             ,'개정동','노송동','삼기면' #전북
             ,'대정읍','연동','이도동' #제주
            ]

dust_list = []

for loc_name in loc_names:
    dust_html = crawling_dust(loc_name, yesterday_str)
    dust_list.extend(listing_bs_dust(dust_html))
    print('loc :', loc_name ,'complete')
    
print(dust_list)


# In[10]:


weather_pd = pd.DataFrame(weather_list)
weather_pd.columns = arr_col
dust_pd = pd.DataFrame(dust_list)
dust_pd.columns = arr_col_dust


# In[11]:


loc_list = {
    '강릉' : '강원'
    , '속초' : '강원'
    , '북춘천' : '강원'
    , '동두천' : '경기'
    , '수원' : '경기'
    , '파주' : '경기'
    , '거창' : '경남'
    , '진주' : '경남'
    , '구미' : '경북'
    , '영주' : '경북'
    , '순천' : '전남'
    , '목포' : '전남'
    , '보성군' : '전남'
    , '서귀포' : '제주'
    , '고창군' : '전북'
    , '군산' : '전북'
    , '전주' : '전북'
    , '금산' : '충남'
    , '보령' : '충남'
    , '부여' : '충남'
    , '보은' : '충북'
    , '제천' : '충북'
    , '청주' : '충북'
}
sido_list = ['강원','경기','경남','경북','광주','대구','대전','부산','서울','울산','인천','전남','전북','제주','충남','충북']

weather_pd['city'] = weather_pd['city'].replace(loc_list)
data_weather_sido = weather_pd[weather_pd['city'].isin(sido_list)]
data_weather_num = data_weather_sido.astype({"avg temp": float, "max temp": float, "min temp": float, "rain": float, "wind": float, "humid": float})
# data_weather_sido.head()
data_weather_avg = data_weather_num.groupby(['city','date']).mean()
data_weather_avg = data_weather_avg.reset_index()
data_weather_avg.head()


# In[12]:


loc_list = {
    '강남구':'서울','강동구':'서울','강북구':'서울' #서울
    ,'가평':'경기','기흥':'경기','수지':'경기' #경기
    ,'검단':'인천','논현':'인천','부평':'인천' #인천
    ,'금호동':'강원','상리':'강원','인제읍':'강원' #강원
    ,'공주':'충남','내포':'충남','논산':'충남' #충남
    ,'구성동':'대전','문창동':'대전','정림동':'대전' #대전
    ,'가덕면':'충북','단양읍':'충북','사천동':'충북' #충북
    ,'개금동':'부산','대신동':'부산','덕포동':'부산' #부산
    ,'농소동':'울산','삼남읍':'울산','약사동':'울산' #울산
    ,'다사읍':'대구','본동':'대구','유가읍':'대구' #대구
    ,'가흥동':'경북','대송면':'경북','명륜동':'경북' #경북
    ,'거창읍':'경남','명서동':'경남','북부동':'경남' #경남
    ,'고흥읍':'전남','담양읍':'전남','보성읍':'전남' #전남
    ,'건국동':'광주','두암동':'광주','유촌동':'광주' #광주
    ,'개정동':'전북','노송동':'전북','삼기면':'전북' #전북
    ,'대정읍':'제주','연동':'제주','이도동':'제주' #제주
}
sido_list = ['강원','경기','경남','경북','광주','대구','대전','부산','서울','울산','인천','전남','전북','제주','충남','충북']

dust_pd['city'] = dust_pd['city'].replace(loc_list)
data_dust_sido = dust_pd[dust_pd['city'].isin(sido_list)]
data_dust_num = data_dust_sido.astype({'SO2':float, 'O3':float, 'NO2':float, 'PM10':float, 'PM25':float})
# data_weather_sido.head()
data_dust_avg = data_dust_num.groupby(['city','date']).mean()
data_dust_avg = data_dust_avg.reset_index()
data_dust_avg.head()


# In[13]:


data_avg = pd.merge(data_dust_avg,data_weather_avg)
data_avg.head()


# In[14]:


if(yesterday_dash == last_day):
    data_avg = pre_save_data
else :
    data_avg = pd.concat([data_avg,pre_save_data])
    
data_avg.head()


# In[15]:


SAVE_POINT = './savedata/avg_data_save.csv'
data_avg.to_csv(SAVE_POINT, sep=',', na_rep='NaN')


# 꽃가루 데이터 수집 및 저장   
# 꽃가루 지수가 수입가능한 날과 아닌 날 따로   
# 세벽값이 의미가 있을까? - 평균값이 아니라 사람들이 활동하는 시간을 중요하게 잡아보자   
# 

# In[ ]:




