
from selenium.webdriver.common.by import By

from time import sleep



def info_crawling(driver):
    navbar_info = driver.find_elements(By.XPATH,'//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div')[0].find_elements(By.CLASS_NAME, 'veBoZ')
    try:
        for index, e in enumerate(navbar_info, start=1):
            if e.text != '메뉴':
                e.click() #하나씩 이동
            sleep(0.8)
            if e.text == '정보':
                e.click()  
                break  
    except: #가끔 오류가 남... 정보로 이동하기 재시도
        try:
            for index, e in enumerate(navbar_info, start=3):
                if e.text != '메뉴':
                    e.click() #하나씩 이동
                sleep(0.8)
                if e.text == '정보':
                    e.click()  
                    break  
        except: 
            info = '가게 정보 불러오기 실패'
            print(info)
            return info
        
    sleep(1)
    try:
        info = driver.find_elements(By.CLASS_NAME,'Ve1Rp')
        info = info[0].text
        print(info)
        return info
    except:
        info = '가게 정보 불러오기 실패'
        print(info)
        return info