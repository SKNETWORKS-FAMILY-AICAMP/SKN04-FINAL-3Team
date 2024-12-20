
from selenium.webdriver.common.by import By

from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from bs4 import BeautifulSoup


def review_crawling(driver):
    navbar_review = driver.find_elements(By.XPATH,'//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div')[0].find_elements(By.CLASS_NAME, 'veBoZ')
    for index, e in enumerate(navbar_review, start=1):
        if e.text == '리뷰':
            e.click()
            break  
    review_scrollable_element = driver.find_element(By.XPATH, "html")

    review_last_height = driver.execute_script("return arguments[0].scrollHeight", review_scrollable_element)

    while True:
        # 요소 내에서 아래로 1000px 스크롤
        driver.execute_script("arguments[0].scrollTop += 1000;", review_scrollable_element)

        # 페이지 로드를 기다림
        sleep(1)  # 동적 콘텐츠 로드 시간에 따라 조절

        # 새 높이 계산
        review_new_height = driver.execute_script("return arguments[0].scrollHeight", review_scrollable_element)

        # 스크롤이 더 이상 늘어나지 않으면 루프 종료
        if review_new_height == review_last_height:
            #더보기 클릭
            sleep(1)
            element = driver.find_element(By.XPATH,'//*[@id="app-root"]/div/div/div/div[6]/div[3]/div[3]/div[2]/div/a')  # 클릭할 요소 선택
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()  # 요소로 스크롤 이동
            element.click()  # 클릭 시도 
            #driver.find_element(By.XPATH,'//*[@id="app-root"]/div/div/div/div[6]/div[3]/div[3]/div[2]/div/a').click()
            continue

        review_last_height = review_new_height
        try:
            driver.find_element(By.XPATH,'//*[@id="app-root"]/div/div/div/div[6]/div[3]/div[3]/div[2]/div/a')
        except: #더 보기에 실패하면 멈춤
            break
        

    bs = BeautifulSoup(driver.page_source, 'lxml')
    review_bs = bs.select('.pui__vn15t2')
    for i in review_bs:
        print(i.text)
