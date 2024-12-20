
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup



def review_like_this_part_crawling(driver):
    navbar_review = driver.find_elements(By.XPATH,'//*[@id="app-root"]/div/div/div/div[4]/div/div/div/div')[0].find_elements(By.CLASS_NAME, 'veBoZ')
    for index, e in enumerate(navbar_review, start=1):
        if e.text == '리뷰':
            e.click()
            break  

    while(True):
        sleep(1)
        a=driver.find_elements(By.XPATH,'//*[@id="app-root"]/div/div/div/div[6]/div[3]/div[1]/div/div/div[2]/a')
        if len(a) != 0:
            if a[0].text == '접기':
                break
            a[0].click()
            continue
        else : break

    bs = BeautifulSoup(driver.page_source, 'lxml')
    review_like_this_part_data = bs.select('.vfTO3')
    print('이런점이 좋았어요')
    for i in review_like_this_part_data:
        print(i.text)

    review_like_this_part_output = ''
    for i in review_like_this_part_data:
        temp = i.text + '\n'
        review_like_this_part_output += temp 

    return review_like_this_part_output

    