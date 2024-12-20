from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from time import sleep
from bs4 import BeautifulSoup


def menu_crawling(driver):
    navbar_review = driver.find_elements(By.XPATH,'//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div')[0].find_elements(By.CLASS_NAME, 'veBoZ')
    for index, e in enumerate(navbar_review, start=1):
        if e.text == '메뉴':
           e.click()
           break  
    more_button = driver.find_elements(By.CLASS_NAME,'xHaT3')
    if len(more_button) != 0:
        for i in more_button:
            element = i  # 클릭할 요소 선택
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()  # 요소로 스크롤 이동
            element.click()  # 클릭 시도 
            sleep(1)
    
    bs = BeautifulSoup(driver.page_source, 'lxml')
    review_bs = bs.select('.MXkFw')
    print('메뉴 : ')
    for i in review_bs:
        
        print(i.text)

    meun_output = ''
    for i in review_bs:
        temp = i.text + '\n'
        meun_output += temp 

    return meun_output
        