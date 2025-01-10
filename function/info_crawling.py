
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
    
    except:
        info = '가게 정보 불러오기 실패'
        print(info)
    #편의시설 및 서비스
    try:
        convenience_facilities_and_services = driver.find_elements(By.CLASS_NAME,'woHEA')[0].find_elements(By.CLASS_NAME,'c7TR6')
        
        print('편의설 및 서비스 : ')
        for i in convenience_facilities_and_services:
            
            print(i.text)

        convenience_facilities_and_services_text = ''
        for i in convenience_facilities_and_services:
            temp = i.text + '\n'
            convenience_facilities_and_services_text += temp    
    
    except:
        print('편의시설 및 서비스 정보 없음')
        convenience_facilities_and_services_text = '편의시설 및 서비스 정보 없음'
    #주차정보
    try:
        Parking = driver.find_elements(By.CLASS_NAME,'uWPF_')
        print(Parking[0].text)
        Parking_text = Parking[0].text
    except:
        print('주차 정보 없음')
        Parking_text = '주차 정보없음'
    #sns링크
    try:
        sns_list = convenience_facilities_and_services = driver.find_elements(By.CLASS_NAME,'R7y09')

        print('sns 링크 : ')
        for i in sns_list:
            
            print(i.find_elements(By.CSS_SELECTOR, 'a')[0].get_attribute("href"))

        sns_text = ''
        for i in sns_list:
            temp = i.find_elements(By.CSS_SELECTOR, 'a')[0].get_attribute("href") + '\n'
            sns_text += temp  
    except:
        print('sns 링크 정보 없음')
        sns_text = 'sns 링크 정보 없음'

    
    return info, convenience_facilities_and_services_text, Parking_text, sns_text