# 패키지
import pandas as pd
import numpy as np
import copy
import xlrd
import re
import os
from tqdm import tqdm
import math

# 제어 관련 패키지
import time
from timeit import default_timer as timer
from datetime import timedelta
import datetime
from dateutil.relativedelta import relativedelta
import os

# 크롤링 관련 패키지
from bs4 import BeautifulSoup
import requests
from urllib import parse

# 모델링 패키지
import tensorflow as tf
import keras
from tensorflow import keras
from keras.utils.np_utils import to_categorical
from keras import models
from keras import layers

# 에어코리아 대기오염통계 정보 크롤링 코드
def crawling_dust_day(p_file_path, p_dust_fnm, p_st_fnm, p_master_fnm, p_log_fnm):
    print('###################  crawling_dust_day, ', '에어코리아 대기오염통계 정보 크롤링 실행 ###################')
    
    # 시간 측정 변수 선언
    start = timer()  # 시작 시간

    # 관측소 정보 API
    param = {
        'addr' : ''
        , 'stationName' : ''
        , 'pageNo' : ''
        , 'numOfRows' : ''
    }
    p_param = parse.urlencode(param) # 파라미터 인코딩

    url = 'http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getMsrstnList?returnType=xml' \
            '&serviceKey=KTaqsmTc5ccj3OSZwKmCYMRYx%2BqUffUcl6rf%2FhyWs7lgSqc%2BIq3waDHQE180K7maH%2FKdYdVvf%2B7bakCmU81UjQ%3D%3D'

    request_info = requests.get(url + '&' + p_param)
    html_co_cel = BeautifulSoup(request_info.text, 'html.parser')

    # 총 관측소 건수 (593개)
    all_cnt = html_co_cel.find_all(re.compile('totalcount'))[0].get_text()

    param['numOfRows'] = all_cnt
    p_param = parse.urlencode(param) # 파라미터 인코딩
    request_info = requests.get(url + '&' + p_param)
    html_co_cel = BeautifulSoup(request_info.text, 'html.parser')

    # 컬럼 딕셔너리 선언
    col_dict = {
        'addr'   : '측정소_주소'
        , 'stationname'    : '측정소명'
        , 'totalcount': '데이터 총 개수'
    }

    # 데이터 수집하기
    addr_df = pd.DataFrame()
    for col, label in col_dict.items():
        if col in ['numofrows', 'pageno', 'totalcount', 'resultcode', 'resultmsg', 'dataType', 'rnum',
                   'stnid']:  # 필요없는 컬럼 제외
            continue
        # print(col, label)
        # 태그명별 수집
        temp_list = html_co_cel.find_all(re.compile('^' + col + '$'))
        temp_list = list(map(str, temp_list))  # 'Tag' 속성인 원소들을 'str' 형태로 변환
        temp_list = list(map(lambda x: x.replace('<' + col + '>', '').replace('</' + col + '>', ''), temp_list))

        addr_df[label] = temp_list  # 페이지별 데이터 프레임에 담기

    ### 측정소 및 지점 정보 조인 => 지점및측정소_마스터 테이블 생성 ###
    addr_df['일련번호'] = list(range(1,len(addr_df)+1)) # 일련번호 생성
    st_df = pd.read_csv(p_file_path+p_st_fnm, dtype='str') # 지점 정보 가져오기
    # 조인키 생성
    addr_df['key'] = addr_df['측정소_주소'].map(lambda x: str(x.split(' ')[0:2]).replace('\'', '').replace(',', '').replace('[', '').replace(']', ''))

    site_df = pd.DataFrame() # 지점및측정소_마스터 데이터 프레임 선언
    for st, no in zip(st_df['지점명'], st_df['지점번호']):
        temp_df = addr_df[addr_df['key'].str.contains(st)]
        if len(temp_df) > 0:
            print('지점명 :', st, ', 확인 : ', temp_df)
            temp_df['지점명'] = st
            temp_df['지점번호'] = no

            site_df = pd.concat([site_df, temp_df])

        else:
            print('해당 지점명과의 매핑이 되지않음 :', st)
    # 정렬
    site_df = site_df.sort_values(['일련번호'])
    # 부산 해운대구 <= 대구 맵핑제거
    site_df = site_df[~((site_df['key'].str.contains('해운대구')) & (site_df['지점명'] == '대구'))]
    # 나머지 중복은 first 행으로 통일
    site_df = site_df.drop_duplicates(['일련번호'], keep='first')  # 최종 393개 관측소, 82개의 지점 정보만 매핑됨
    # 지점 및 측정소 마스터 데이터 적재
    site_df.to_csv(p_file_path+p_master_fnm, index=False, encoding='cp949')


    ### 에어코리아 대기오염정보 조회 서비스 API ###
    col_dict = {
        'msurdt' : '측정일'
        , 'msrstnname' : '측정소명'
        , 'so2value' : '아황산가스_평균농도'
        , 'covalue' : '일산화탄소_평균농도'
        , 'o3value' : '오존_평균농도'
        , 'no2value' : '이산화질소_평균농도'
        , 'pm10value' : '미세먼지_PM10_평균농도'
        , 'pm25value' : '미세먼지_PM25_평균농도'
    }

    url = 'http://apis.data.go.kr/B552584/ArpltnStatsSvc/getMsrstnAcctoRDyrg?' \
          'returnType=xml&serviceKey=KTaqsmTc5ccj3OSZwKmCYMRYx%2BqUffUcl6rf%2FhyWs7lgSqc%2BIq3waDHQE180K7maH%2FKdYdVvf%2B7bakCmU81UjQ%3D%3D'

    # 최초 접속(트래픽 : 10000)
    # 크롤링 시간 설정
    bgdt = datetime.datetime.today() - relativedelta(months=6)
    inqBginDt = bgdt.strftime(format='%Y%m%d')
    enddt = datetime.datetime.today() - relativedelta(days=1)
    inqEndDt = enddt.strftime(format='%Y%m%d')

    empty_list = [] # 데이터 부재인 측정소(총 594개 측정소)
    save_no = 0 # 총 적재 건수
    for site_nm in tqdm(addr_df['측정소명']): # 지역 기준 FOR문
        # for site_nm in ['종로구']: # 지역 기준 FOR문

        # 지역(관측소)별 데이터 프레임 선언
        all_df = pd.DataFrame()
        print(site_nm)

        param = {
            'msrstnName' : site_nm
            ,'inqBginDt' : inqBginDt # 시작일 => 20210101 부터 제공중(6개월치 데이터 분량은 없음)
            ,'inqEndDt' : inqEndDt # 종료일
            ,'numOfRows' : ''
            ,'pageNo' : ''
        }

        p_param = parse.urlencode(param) # 인코딩

        # 최초 접속
        request_info = requests.get(url + '&' + p_param)
        html_co_cel = BeautifulSoup(request_info.text, 'html.parser')

        # 에러 발생시
        check = html_co_cel.find_all(re.compile('^r.*msg'))[0].get_text()

        while (check == 'LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR') or (check == 'SERVICE ERROR') \
                or (check == 'SERVICE_KEY_IS_NOT_REGISTERED_ERROR'):
            print('요청 초과 제한에러')
            print('재요청')
            time.sleep(3)
            request_info = requests.get(url + '&' + p_param)
            html_co_cel = BeautifulSoup(request_info.text, 'html.parser')
            check = html_co_cel.find_all(re.compile('^r.*msg'))[0].get_text()
            if check.find('ERROR') == -1:
                print('제한 해제')
                break

        # 총 추출 건수(측정소별)
        all_cnt = html_co_cel.find_all(re.compile('totalcount'))[0].get_text()



        if all_cnt == '0':
            print('비어있는 측정소명 :', site_nm)
            empty_list.append(site_nm)
            continue

        if int(all_cnt) > 999: # 총 건수가 1000건 이상일 때 (한 페이지에 999건 밖에 못들고옴)
            param['numOfRows'] = '999' # 전체 페이지 번호
            all_page_no = math.ceil(int(all_cnt)/999) # 전체 페이지 번호
        else:
            param['numOfRows'] = all_cnt
            all_page_no = 1


        # 추출 대상 전체 건 크롤링(페이지 기준)
        for page in range(1, all_page_no+1):
            print('페이지 번호 :',page)
            param['pageNo'] = str(page)

            # 쿼리스트링으로 인코딩
            p_param = parse.urlencode(param)

            # url로 접속
            # time.sleep(0.1)
            request_info = requests.get(url + '&' + p_param)
            html_co_cel = BeautifulSoup(request_info.text, 'html.parser')

            # 에러 발생시
            check = html_co_cel.find_all(re.compile('^r.*msg'))[0].get_text()

            while check in['LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR', 'SERVICE ERROR', 'SERVICE_KEY_IS_NOT_REGISTERED_ERROR']:
                print('요청 초과 제한에러')
                print('재요청')
                time.sleep(3)
                request_info = requests.get(url + '&' + p_param)
                html_co_cel = BeautifulSoup(request_info.text, 'html.parser')
                check = html_co_cel.find_all(re.compile('^r.*msg'))[0].get_text()
                if (check in ['LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR', 'SERVICE ERROR', 'SERVICE_KEY_IS_NOT_REGISTERED_ERROR']) == False:
                    print('제한 해제')
                    break


            # 페이지 기준으로 담을 데이터 프레임 선언
            df = pd.DataFrame()

            # 데이터 수집하기
            for col, label in col_dict.items():
                if col in ['numofrows', 'pageno', 'totalcount', 'resultcode', 'resultmsg', 'dataType', 'rnum', 'stnid']: # 필요없는 컬럼 제외
                    continue
                # print(col, label)
                # 태그명별 수집
                temp_list = html_co_cel.find_all(re.compile('^'+col+'$'))
                temp_list = list(map(str, temp_list)) # 'Tag' 속성인 원소들을 'str' 형태로 변환
                temp_list = list(map(lambda x : x.replace('<'+col+'>', '').replace('</'+col+'>', ''), temp_list))

                if len(temp_list) == 0:
                    print('부재 컬럼명 :', col, '라벨명 :',label)
                    continue
                df[label] = temp_list # 페이지별 데이터 프레임에 담기


            # 데이터 필터링(like 성의 측정소 검색 => 특정 측정소만 추출)
            df = df[df['측정소명'] == site_nm]

            # 데이터 적재
            f_list = os.path.splitext(p_file_path + p_dust_fnm)
            dust_fnm= f_list[0] + '_' + inqBginDt + '_' + inqEndDt + f_list[1]
            if os.path.isfile(dust_fnm) == False:
                print('파일 미존재 => 파일생성 및 적재')
                df.to_csv(dust_fnm, index=False, mode='w', encoding='cp949')
            else:
                print('파일 존재 => 적재')
                df.to_csv(dust_fnm, index=False, mode='a', header=False, encoding='cp949')

            # 총 적재 건수
            save_no += len(df)

            print('페이지 번호 :',page,', 페이지별 데이터 건수 :',len(df), ', 총 적재 건수 :', save_no)


    # 함수 종료 시간
    end = timer()
    all_time = str(timedelta(seconds=end - start)).split(':')
    all_time = all_time[0] + '시간 ' + all_time[1] + '분 ' + all_time[2] + '초'
    today_dt = datetime.datetime.today().strftime(format='%Y-%m-%d %H-%M-%S') # 현재 시간

    print('크롤링 완료, 지상(종관) 크롤링 걸린 시간 :', all_time)
    time_dict = {'등록시간' : [today_dt], '함수명' : ['crawling_dust_day'],
                 '결과_데이터명' : [p_dust_fnm], '소요시간' : [all_time], '전체_건수' : [save_no]}
    time_df = pd.DataFrame(time_dict)

    # 데이터 적재
    f_list = os.path.splitext(p_file_path + p_log_fnm)
    log_fnm = f_list[0]+'_'+inqEndDt+f_list[1]

    if os.path.isfile(log_fnm) == False:
        print('로그 파일 미존재 => 파일생성 및 적재')
        time_df.to_csv(log_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('로그 파일 존재 => 적재')
        time_df.to_csv(log_fnm, index=False, mode='a', header=False, encoding='cp949')


    # 부재 측정소 리스트
    if len(empty_list) != 0:
        empty_df = pd.DataFrame({'부재_측정소명' : empty_list})
        empty_df.to_csv(p_file_path+'미세먼지_일자료_부재측정소_'+inqEndDt+'.csv', index = False, encoding='cp949')

    print('###################  crawling_dust_day, ', '에어코리아 대기오염통계 정보 크롤링 완료 ###################')
    
    return

# 기상 지상종관 일자료 정보 크롤링 코드
def crawling_weather_day(p_file_path, p_st_fnm, p_weather_fnm, p_log_fnm):
    print('###################  crawling_weather_day, ', '기상 지상종관 일자료 정보 크롤링 실행 ###################')
    
    # 시간 측정 변수 선언
    start = timer() # 시작 시간

    # 기상관측일자료 지점 정보 불러오기
    st_df = pd.read_csv(p_file_path+p_st_fnm, dtype='str')

    # 컬럼 딕셔너리 선언
    col_dict = {
        'stnid': '지점번호'
        , 'stnnm': '지점명'
        , 'tm': '시간'
        , 'avgta': '평균_기온'
        , 'minta': '최저_기온'
        , 'maxta': '최고_기온'
        , 'sumrn': '일강수량'
        , 'avgws': '평균_풍속'
        , 'maxws': '최대_풍속'
        , 'avgrhm': '평균_상대습도'
        , 'maxwd': '최다_풍향'
    }

    # 크롤링 시간 파라미터 셋팅
    bgdt = datetime.datetime.today() - relativedelta(months=6) # Day 기준 자료(6개월전)
    inqBginDt = bgdt.strftime(format='%Y%m%d')
    enddt = datetime.datetime.today() - relativedelta(days=1) # 기상종관 API는 전날 자료까지만 제공
    inqEndDt = enddt.strftime(format='%Y%m%d')
    save_no = 0 # 총 적재건수

    # 지점 기준 for문
    for st in tqdm(st_df['지점번호']):
        print('크롤링 지점번호 :', st)
        param = {
            'startDt' : inqBginDt
            # ,'startHh' : '00'
            ,'endDt' : inqEndDt
            # ,'endHh' : '00'
            ,'pageNo' : ''
            ,'numOfRows' : ''
            ,'stnIds' : st
        }
        p_param = parse.urlencode(param)

        # 최초 접속

        url = 'http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList?serviceKey=KTaqsmTc5ccj3OSZwKmCYMRYx%2BqUffUcl6rf%2FhyWs7lgSqc%2BIq3waDHQE180K7maH%2FKdYdVvf%2B7bakCmU81UjQ%3D%3D' \
              '&dataCd=ASOS&dateCd=DAY'
        request_info = requests.get(url + '&' + p_param)
        html_co_cel = BeautifulSoup(request_info.text, 'html.parser')

        # 에러 발생시
        check = html_co_cel.find_all(re.compile('^r.*msg'))[0].get_text()

        while check in ['LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR','SERVICE ERROR','SERVICE_KEY_IS_NOT_REGISTERED_ERROR']:
            print('요청 초과 제한에러')
            print('재요청')
            time.sleep(3)
            request_info = requests.get(url + '&' + p_param)
            html_co_cel = BeautifulSoup(request_info.text, 'html.parser')
            check = html_co_cel.find_all(re.compile('^r.*msg'))[0].get_text()
            if (check in ['LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR', 'SERVICE ERROR','SERVICE_KEY_IS_NOT_REGISTERED_ERROR']) == False:
                print('제한 해제')
                break



        # 총 추출 건수
        all_cnt = html_co_cel.find_all(re.compile('totalcount'))[0].get_text()
        if int(all_cnt) > 999: # 총 건수가 1000건 이상일 때 (한 페이지에 999건 밖에 못들고옴)
            param['numOfRows'] = '999' # 전체 페이지 번호
            all_page_no = int(round(int(all_cnt)/999, 0)) # 전체 페이지 번호
        else:
            param['numOfRows'] = all_cnt
            all_page_no = 1

        # 추출 대상 전체 건 크롤링(페이지 기준)
        for page in tqdm(range(1, all_page_no+1)):
            print('페이지 번호 :',page)
            param['pageNo'] = str(page)

            # 쿼리스트링으로 인코딩
            p_param = parse.urlencode(param)

            # url로 접속
            request_info = requests.get(url + '&' + p_param)
            html_co_cel = BeautifulSoup(request_info.text, 'html.parser')

            # 에러 발생시
            check = html_co_cel.find_all(re.compile('^r.*msg'))[0].get_text()

            while check in ['LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR','SERVICE ERROR','SERVICE_KEY_IS_NOT_REGISTERED_ERROR']:
                print('요청 초과 제한에러')
                print('재요청')
                time.sleep(3)
                request_info = requests.get(url + '&' + p_param)
                html_co_cel = BeautifulSoup(request_info.text, 'html.parser')
                check = html_co_cel.find_all(re.compile('^r.*msg'))[0].get_text()
                if (check in ['LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR', 'SERVICE ERROR','SERVICE_KEY_IS_NOT_REGISTERED_ERROR']) == False:
                    print('제한 해제')
                    break


            # 페이지 기준으로 담을 데이터 프레임 선언
            df = pd.DataFrame()

            # 데이터 수집하기
            for col, label in col_dict.items():
                if col in ['numofrows', 'pageno', 'totalcount', 'resultcode', 'resultmsg', 'dataType', 'rnum']: # 필요없는 컬럼 제외
                    continue
                # print(col, label)
                # 태그명별 수집
                temp_list = html_co_cel.find_all(re.compile('^'+col+'$'))
                temp_list = list(map(str, temp_list)) # 'Tag' 속성인 원소들을 'str' 형태로 변환
                temp_list = list(map(lambda x : x.replace('<'+col+'>', '').replace('</'+col+'>', ''), temp_list))

                if len(temp_list) == 0:
                    print('부재 컬럼명 :', col, '라벨명 :', label)
                    continue
                df[label] = temp_list  # 페이지별 데이터 프레임에 담기

            # 데이터 필터링(LIKE 성의 측정소 검색 => 수집 대상 측정소만 추출)
            df = df[df['지점번호'] == st]

            # 데이터 적재
            f_list = os.path.splitext(p_file_path + p_weather_fnm)
            weather_fnm = f_list[0]+'_'+inqBginDt+'_'+inqEndDt+f_list[1]
            if os.path.isfile(weather_fnm) == False:
                print('파일 미존재')
                df.to_csv(weather_fnm,index=False,mode='w',encoding='cp949')
            else:
                print('파일 존재 => 적재')
                df.to_csv(weather_fnm,index=False,mode='a',header=False,encoding='cp949')

            # 총 적재 건수
            save_no += len(df)

            print('페이지 번호 :', page, ', 페이지별 데이터 건수 :', len(df), ', 총 적재 건수 :', save_no)


    # 함수 종료 시간
    end = timer()
    all_time = str(timedelta(seconds=end - start)).split(':')
    all_time = all_time[0] + '시간 ' + all_time[1] + '분 ' + all_time[2] + '초'
    today_dt = datetime.datetime.today().strftime(format='%Y-%m-%d %H-%M-%S')  # 현재 시간
    print('크롤링 완료, 지상(종관) 크롤링 걸린 시간 :', all_time)
    time_dict = {'등록시간' : [today_dt], '함수명' : ['crawling_weather_day'],
                 '결과_데이터명' : [weather_fnm], '소요시간' : [all_time], '전체_건수' : [save_no]}
    time_df = pd.DataFrame(time_dict)

    # 데이터 적재
    f_list = os.path.splitext(p_file_path + p_log_fnm)
    log_fnm = f_list[0]+'_'+inqEndDt+f_list[1]

    if os.path.isfile(log_fnm) == False:
        print('로그 파일 미존재 => 파일생성 및 적재')
        time_df.to_csv(log_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('로그 파일 존재 => 적재')
        time_df.to_csv(log_fnm, index=False, mode='a', header=False, encoding='cp949')

    print('###################  crawling_weather_day, ', '기상 지상종관 일자료 정보 크롤링 완료 ###################')

    return

# 모델링 및 스코어링 코드
def modeling_and_scoring(p_file_path,p_target_nm,p_dust_fnm,p_weather_fnm,p_master_fnm,p_score_data_fnm,p_log_fnm):
    print('###################  modeling_and_scoring, ', '모델링 및 스코어링 실행 ###################')
    # 시간 측정 변수 선언
    start = timer()  # 시작 시간

    # 크롤링 시간 변수 선언
    bgdt = datetime.datetime.today() - relativedelta(months=6)
    inqBginDt = bgdt.strftime(format='%Y%m%d')

    enddt = datetime.datetime.today() - relativedelta(days=1)
    inqEndDt = enddt.strftime(format='%Y%m%d')

    ##################################### 0. 데이터 임포트 ##################################
    ### 0-1. 대기오염통계_일자료 데이터 임포트
    f_list = os.path.splitext(p_file_path + p_dust_fnm)
    dust_fnm = f_list[0] + '_' + inqBginDt + '_' + inqEndDt + f_list[1]
    df = pd.read_csv(dust_fnm, encoding='cp949', dtype='str')
    # 타입 변환
    dust_dict = {'아황산가스_평균농도': 'float'
        , '일산화탄소_평균농도': 'float'
        , '오존_평균농도': 'float'
        , '이산화질소_평균농도': 'float'
        , '미세먼지_PM10_평균농도': 'float'
        , '미세먼지_PM25_평균농도': 'float'}
    df = df.astype(dust_dict)

    ### 0-2. 기상종관_일자료 데이터 임포트
    f_list = os.path.splitext(p_file_path + p_weather_fnm)
    weather_fnm = f_list[0] + '_' + inqBginDt + '_' + inqEndDt + f_list[1]
    wt_df = pd.read_csv(weather_fnm, encoding='cp949', dtype='str')
    # 타입 변환
    wt_dict = {'평균_기온': 'float'
        , '최저_기온': 'float'
        , '최고_기온': 'float'
        , '일강수량': 'float'
        , '평균_풍속': 'float'
        , '최대_풍속': 'float'
        , '평균_상대습도': 'float'
        , '최다_풍향': 'float'}
    wt_df = wt_df.astype(wt_dict)

    ### 0-3. 지점 및 관측소 Master 테이블
    master_fnm = p_file_path + p_master_fnm
    mst_df = pd.read_csv(master_fnm, encoding='cp949', dtype='str')

    ###################################### 1. 데이터 전처리 ##################################

    ### 1-1. 미세먼지 데이터 결측치 제거
    df = df.dropna()

    ### 1-2. 일강수량 결측치 => 0 으로 치환
    wt_df['일강수량'] = wt_df['일강수량'].map(lambda x: 0 if pd.isna(x) else x)

    ### 1-3. 기상 데이터 결측치 제거
    wt_df = wt_df.dropna()
    wt_df.rename({'시간': '측정일'}, axis='columns', inplace=True)

    ### 1-4. 미세먼지 데이터와 마스터 테이블 조인(지점정보 조인)
    df = pd.merge(df, mst_df[['측정소명', '지점명']], on=['측정소명'], how='left')  # 지점 정보가 조인이 되지 않는 측정소 데이터는 버림.
    df = df.dropna()  # 조인 후 결측치 제거

    ### 1-5. 미세먼지 데이터와 기상 데이터 조인
    df = pd.merge(df, wt_df, on=['측정일', '지점명'], how='left')
    df = df.dropna()  # 조인 후 결측치 제거

    ### 1-6. 전체 측정소 통합 기준(미세먼지 농도에 따른 분류) 및 타겟 컬럼 생성 => WHO 기준
    # 10PM => 0~30 : 좋음, 31~50 : 보통, 51~100 : 나쁨, 101~ : 매우나쁨
    # 2.5PM => 0~15 : 좋음, 16~25 : 보통, 26~50 : 나쁨, 51~ : 매우나쁨
    param = p_target_nm.split('_')[0] + '_' + p_target_nm.split('_')[1] + '_평균농도'
    df[p_target_nm] = df[param].map(lambda x: '좋음' if x <= 50 else '나쁨')  # 나쁨 => 1 , 좋음 => 0
    df['target'] = df[p_target_nm].shift(-1)

    # 측정소별 가장 마지막 관측일 (INPUT DATA) => 타겟 예측을 위한 데이터
    t_df = df.sort_values(['측정소명', '측정일']).groupby(['측정소명']).last().reset_index()
    for site, dt in zip(t_df['측정소명'], t_df['측정일']):
        df = df[~((df['측정소명'] == site) & (df['측정일'] == dt))]

    # 측정일이 하루 전날인 데이터(INPUT DATA)만 추출
    y_dt = inqEndDt[:4]+'-'+inqEndDt[4:6]+'-'+inqEndDt[6:]
    t_df = t_df[t_df['측정일'] == y_dt]
    ######################## 2. 모델링 TRAIN & TARGET LABELING ##############################
    ### 2-1. 학습 및 테스트 데이터 셋팅
    df = df.reset_index(drop=True)  # 인덱스 초기화

    # 학습대상 컬럼외 제거
    d_col = ['측정일', '측정소명', '지점명', '지점번호', p_target_nm, 'target']
    t_col = list(df.columns)
    del_list = list(set(t_col).intersection(d_col))
    for x in del_list:
        if x in t_col:
            t_col.remove(x)

    # 학습데이터 구축을 위한 Numpy 변환
    train_array = np.array(df[t_col])  # 학습을 위한 INPUT DATA
    target_array = to_categorical(df['target'].map(lambda x: 0 if x == '좋음' else 1))  # 학습을 위한 TARGET DATA
    target_dict = {0: '좋음', 1: '나쁨'}

    # 예측(Scoring) 대상 INPUT 데이터 Numpy 변환 : 내일 미세먼지 예측을 위한 당일 INPUT 데이터
    t_tr_array = np.array(t_df[t_col])
    save_no = len(t_df)  # 스코어링 데이터 건수

    # 데이터 확인
    print('SHAPE 확인 : ', train_array.shape, target_array.shape, t_tr_array.shape)
    print('TYPE 확인 : ', type(train_array), type(target_array), type(t_tr_array))

    # 모델 생성
    model = models.Sequential()

    model.add(layers.Dense(32, activation='relu', input_shape=(train_array.shape[1],)))
    model.add(layers.Dense(16, activation='relu'))
    model.add(layers.Dense(target_array.shape[1], activation='softmax'))

    # 모델 구성 확인
    print(model.summary())
    # 모델 학습과정 설정
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    # 모델 학습
    hist = model.fit(train_array, target_array, epochs=5, verbose=2)

    # 스코어링
    proba = model.predict(x=t_tr_array)
    rst_idx = np.argmax(proba, axis=1)
    score_list = list(proba[:, 1]) # 스코어 => "나쁨" 일 확률
    rst_list = [target_dict[idx] for idx in rst_idx]

    t_df['스코어'] = score_list
    t_df['분류결과'] = rst_list
    # cut-off = 0.3 일때의 분류 결과
    t_df['분류결과_cutoff_0.3'] = ['나쁨' if x > 0.3 else '좋음' for x in proba[:, 1]]
    # 컬럼 재정의
    t_df.drop(columns=['target'], inplace=True)

    # 스코어링 데이터 적재
    f_list = os.path.splitext(p_file_path + p_score_data_fnm)
    score_data_fnm = f_list[0] + '_' + inqEndDt + f_list[1]
    if os.path.isfile(score_data_fnm) == False:
        print('스코어링 데이터 파일 미존재')
        t_df.to_csv(score_data_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('스코어링 데이터 파일 존재 => 적재')
        t_df.to_csv(score_data_fnm, index=False, mode='a', header=False, encoding='cp949')

    # 함수 종료 시간
    end = timer()
    all_time = str(timedelta(seconds=end - start)).split(':')
    all_time = all_time[0]+'시간 '+all_time[1]+'분 '+all_time[2]+'초'
    today_dt = datetime.datetime.today().strftime(format='%Y-%m-%d %H-%M-%S')
    print('크롤링 완료, 모델링 및 스코어링 걸린 시간 :', all_time)
    time_dict = {'등록시간': [today_dt], '함수명': ['modeling_and_scoring'],
                 '결과_데이터명': [score_data_fnm], '소요시간': [all_time], '전체_건수': [save_no]}
    log_df = pd.DataFrame(time_dict)

    # 모델 및 스코어링 결과 내역 적재
    f_list = os.path.splitext(p_file_path + p_log_fnm)
    log_fnm = f_list[0] + '_' + inqEndDt + f_list[1]
    if os.path.isfile(log_fnm) == False:
        print('로그 파일 미존재 => 파일생성 및 적재')
        log_df.to_csv(log_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('로그 파일 존재 => 적재')
        log_df.to_csv(log_fnm, index=False, mode='a', header=False, encoding='cp949')

    print('###################  modeling_and_scoring, ', '모델링 및 스코어링 완료 ###################')

    return


# 함수 실행부
if __name__ == '__main__':

    # 0. 함수 관련 파라미터
    file_path = 'C:\\Users\\wai\\Desktop\\프로젝트\\미린트자료\\최종확인\\'  # 전체 파일 경로 설정
    dust_fnm = '에어코리아_대기오염통계_일자료.csv'  # 대기오염정보 데이터 파일명
    weather_fnm = '기상청_지상종관_일자료.csv'  # 기상종관자료 데이터 파일명
    master_fnm = '지점및측정소_마스터.csv'  # 지점 및 관측소 마스터 테이블 파일명
    target_nm = '미세먼지_PM10_등급'  # 예측할 타겟 설정(다음날의 '미세먼지_PM10_등급', '미세먼지_PM25_등급')
    score_data_fnm = '스코어링_데이터.csv'  # 스코어링 데이터 파일명
    st_fnm = '지점정보.csv'  # 지점정보 파일명
    scoring_log_fnm = '모델및스코어링_로그.csv'  # 모델 및 스코어 함수 로그 데이터 파일명
    crawling_log_fnm = '크롤링_로그.csv'  # 크롤링 로그 데이터 파일명


    # 1. 미세먼지 데이터 크롤링 함수 실행
    crawling_dust_day(p_file_path=file_path,p_dust_fnm=dust_fnm,p_st_fnm=st_fnm,p_master_fnm=master_fnm,p_log_fnm=crawling_log_fnm)

    # 2. 기상 데이터 크롤링 함수 실행
    crawling_weather_day(p_file_path=file_path,p_st_fnm=st_fnm,p_weather_fnm=weather_fnm,p_log_fnm=crawling_log_fnm)

    # 3. 모델링 및 스코어링 함수 실행
    modeling_and_scoring(file_path,target_nm,dust_fnm,weather_fnm,master_fnm,score_data_fnm,scoring_log_fnm)

