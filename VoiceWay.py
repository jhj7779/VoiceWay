import pandas as pd
import playsound
import speech_recognition as sr
import numpy as np
from datetime import datetime
from pytimekr import pytimekr
from konlpy.tag import Komoran
from gtts import gTTS

# r = sr.Recognizer()
# mic = sr.Microphone()
# with mic as source:
#     audio = r.listen(source)
# text = r.recognize_google(audio, language='ko-kr')
# text = text.replace(" ","")

text = "신천역 언제와?"

print(text)

csv_test = None
sname01 = ['안심역','각산역','반야월역','신기역','율하역','용계역','방촌역','해안역','동촌역','아양교역','동구청역','동대구역','신천역','칠성시장역','대구역','중앙로역','반월당역','명덕역','교대역','영대병원역'
    '현충로역','안지랑역','대명역','서부정류장역','송현역','월촌역','상인역','월배역','진천역','대곡역','화원역','설화명곡역']
sname02 = ['영남대역','임당역','정평역','사월역','신매역','고산역','대공원역','연호역','담티역','만촌역','수성구청역','범어역','대구은행역','경대병원역','반월당역','청라언덕역','반고개역','내당역','두류역',
           '감삼역','죽전역','용산역','이곡역','성서산업단지역','계명대역','강창역','대실역','다사역','문양역']
sname03 = ['용지역','범물역','지산역','수성못역','황금역','어린이회관역','수성구민운동장역','수성시장역','대봉교역','건들바위역','명덕역','남산역','신남역','서문시장역','달성공원역','북구청역','원대역',
           '팔달시장역','만평역','공단역','팔달역','매천시장역','매천역','태전역','구암역','칠곡운암역','동천역','팔거역','학정역','칠곡경대병원역']
sinterval01 = [2,2,2,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,1,2,2,1,2,2,1,2,2,1,2,2,2]
sinterval02 = [2,2,2,2,2,2,2,3,1,2,2,2,2,2,2,1,2,2,1,2,2,2,2,2,2,2,2,4]
sinterval03 = [1,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,1,1,2,1,1,2,2,2,1,2,1,2,1]

holiday = [pytimekr.newyear(),pytimekr.lunar_newyear(),pytimekr.samiljeol(),pytimekr.buddha(),pytimekr.children(),pytimekr.memorial(),pytimekr.independence(),
           pytimekr.chuseok(),pytimekr.foundation(),pytimekr.hangul(),pytimekr.christmas()]

state = -1 # -1 : default, 0 : weekday, 1 : saturday, 2 : sunday and holiday
timestamp = []
upanddown = -1 # 1 : up(상행), 0 : down(하행)


def CheckLineNumber(text1): # 호선 구분잣기
    if text1 in sname01:
        linenumber = 1
    elif text1 in sname02:
        linenumber = 2
    else :
        linenumber = 3
    return linenumber
#
def HowLongNeed(text1,text2): # 두 지하철역간 걸리는 시간 계산.
    total = 0
    linenum = CheckLineNumber(text1)
    if linenum == 1:
        departure = sname01.index(text1)
        destination = sname01.index(text2)
        if departure > destination:
            for distance in sinterval01[destination:departure]:
                total = total + distance
        else:
            for distance in sinterval01[departure:destination]:
                total = total + distance

    elif linenum == 2:
        departure = sname02.index(text1)
        destination = sname02.index(text2)
        if departure > destination:
            for distance in sinterval02[destination:departure]:
                total = total + distance
        else:
            for distance in sinterval02[departure:destination]:
                total = total + distance

    elif linenum == 3:
        departure = sname03.index(text1)
        destination = sname03.index(text2)
        if departure > destination:
            for distance in sinterval03[destination:departure]:
                total = total + distance
        else:
            for distance in sinterval03[departure:destination]:
                total = total + distance
    return total

def WhatIsToday():
    now = datetime.now().weekday()
    if now not in holiday : #평일 : 0 토요일 : 1 휴일 : 2
        if now < 5:
            state = 0
        elif now == 5:
            state = 1
        else :
            state = 2
    else :
        state = 2
    return state

def LoadData(text1,text2,text3): #출발역,휴일,csv
    temp1 = []
    temp2 = []
    state = text2
    # 종점처리
    if text1 == sname01[0] or text1 == sname02[0] or text1 == sname03[0]:
        if state == 0:
            temp1.append(text3['상행평일'].dropna().tolist())
        elif state == 1:
            temp1.append(text3['상행토요일'].dropna().tolist())
        else:
            temp1.append(text3['상행휴일'].dropna().tolist())
    #  종점처리       
    elif text1 == sname01[-1] or text1 == sname02[-1] or text1 == sname03[-1]:
        if state == 0:
            temp2.append(text3['하행평일'].dropna().tolist())
        elif state == 1:
            temp2.append(text3['하행토요일'].dropna().tolist())
        else:
            temp2.append(text3['하행휴일'].dropna().tolist())
    else :
        if state == 0:
            temp1.append(text3['상행평일'].dropna().tolist())
            temp2.append(text3['하행평일'].dropna().tolist())
        elif state == 1:
            temp1.append(text3['상행토요일'].dropna().tolist())
            temp2.append(text3['하행토요일'].dropna().tolist())
        else :
            temp1.append(text3['상행휴일'].dropna().tolist())
            temp2.append(text3['하행휴일'].dropna().tolist())
    return temp1,temp2

def WhenSubwayCome(linenum,text1):
    if linenum == 1:
        url = './subway1/' + str(sname01.index(text1)) + '.csv'
    elif linenum == 2:
        url = './subway2/' + str(sname02.index(text1)) + '.csv'
    else :
        url = './subway3/' + str(sname03.index(text1)) + '.csv'

    csv_test = pd.read_csv(url, encoding='cp949')
    stat = WhatIsToday()
    temp1,temp2 = LoadData(text1,stat,csv_test) #출발역,휴일,csv
    return temp1,temp2


def Speak(text):
    tts = gTTS(text=text, lang='ko')
    filename='voice.mp3'
    tts.save(filename)
    playsound.playsound(filename)

# menu = input("input number : ") #1번 : 열차 도착하는 시간 구하기 // 2번 : 역간 예상 소요시간 구하기 // 0번 : 종료
komoran = Komoran(userdic='user_dic.txt')
# if menu == '1':
    # text = input("해당 역이름을 입력하세요: ")
nouns = komoran.nouns(text)
findstation = nouns
station_match = [s for s in findstation if "역" in s]
text = station_match[0]


linenum = CheckLineNumber(text)
temp1,temp2 = WhenSubwayCome(linenum,text)
now = datetime.now()
timestamp1 = []
timestamp2 = []
index1 = -1
index2 = -1


if temp1:
    temp1 = temp1[0]

    for item in temp1:
        timestamp1.append(item.split(':'))

    for idx, value in enumerate(timestamp1):
        if int(datetime.time(now).hour) >= int(value[0]) and int(datetime.time(now).minute) > int(value[1]):
            index1 = idx
    timestamp1 = timestamp1[index1 + 1:]

if temp2:
    temp2 = temp2[0]

    for item in temp2:
        timestamp2.append(item.split(':'))
    for idx, value in enumerate(timestamp2):
        if int(datetime.time(now).hour) >= int(value[0]) and int(datetime.time(now).minute) > int(value[1]):
            index2 = idx
    timestamp2 = timestamp2[index2 + 1:]

if linenum == 1:
    desti1 = "설화명곡"
    desti2 = "안심"
elif linenum == 2:
    desti1 = "문양"
    desti2 = "영남대"
else :
    desti1 = "칠곡경대병원"
    desti2 = "용지"

if not timestamp1 and timestamp2:
    Speak(desti2 + "방면 도착 예정 시간은 " + timestamp2[0][0] + " 시 "+timestamp2[0][1] +" 분 입니다.")
    print(desti2 + "방면 도착 예정 시간은 " + timestamp2[0][0] + " 시 "+timestamp2[0][1] +" 분 입니다.")
elif timestamp1 and not timestamp2:
    Speak(desti1 + "방면 도착 예정 시간은 " + timestamp1[0][0] + " 시 " + timestamp1[0][1] + " 분 입니다.")
    print(desti1 + "방면 도착 예정 시간은 " + timestamp1[0][0] + " 시 " + timestamp1[0][1] + " 분 입니다.")
else :

    print(desti1 + "방면 도착 예정 시간은 " + timestamp1[0][0] + " 시 " + timestamp1[0][1] + " 분 입니다.")
    print(desti2 + "방면 도착 예정 시간은 " + timestamp2[0][0] + " 시 " + timestamp2[0][1] + " 분 입니다.")
    Speak(desti1 + "방면 도착 예정 시간은 " + timestamp1[0][0] + " 시 " + timestamp1[0][1] + " 분 입니다."
          + desti2 + "방면 도착 예정 시간은 " + timestamp2[0][0] + " 시 " + timestamp2[0][1] + " 분 입니다.")





#
# elif menu == '2':
#     text1 = input("출발역을 입력하세요: ")
#     text2 = input("도착역을 입력하세요: ")
#     print(text1 + "에서 " + text2 + "까지 " + str(HowLongNeed(text1, text2)) + " 분이 소요될 예정입니다.")
# else :
#     exit(0)