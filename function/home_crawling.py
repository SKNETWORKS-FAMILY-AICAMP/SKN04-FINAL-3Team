
from selenium.webdriver.common.by import By

from selenium.webdriver.common.action_chains import ActionChains

from time import sleep



def home_crawling(driver, business_hours):
    title = driver.find_element(By.XPATH,'//div[@class="zD5Nm undefined"]')
    store_info = title.find_elements(By.XPATH,'//div[@class="YouOG DZucB"]/div/span')


    # 가게 이름
    store_name = title.find_element(By.XPATH,'.//div[1]/div[1]/span[1]').text

    # 카테고리
    category = title.find_element(By.XPATH,'.//div[1]/div[1]/span[2]').text

    if(len(store_info) > 2):
        # 새로 오픈
        new_open = title.find_element(By.XPATH,'.//div[1]/div[1]/span[3]').text

    new_open = ' '
    ###############################

    review = title.find_elements(By.XPATH,'.//div[2]/span')

    # 인덱스 변수 값
    _index = 1

    # 리뷰 ROW의 갯수가 3개 이상일 경우 [별점, 방문자 리뷰, 블로그 리뷰]
    if len(review) > 2:
        rating_xpath = f'.//div[2]/span[{_index}]'
        rating_element = title.find_element(By.XPATH, rating_xpath)
        rating = rating_element.text.replace("\n", " ")

        _index += 1
    else:
        rating = '정보없음' #별점 정보가 없을 경우
    try:
        # 방문자 리뷰 수수
        visited_review = title.find_element(By.XPATH,f'.//div[2]/span[{_index}]/a').text


        # 인덱스를 다시 +1 증가 시킴
        _index += 1

        # 블로그 리뷰 수수
        blog_review = title.find_element(By.XPATH,f'.//div[2]/span[{_index}]/a').text
    except:
        print('------------ 리뷰 부분 오류 ------------')

    # 가게 id
    store_id = driver.find_element(By.XPATH,'//div[@class="flicking-camera"]/a').get_attribute('href').split('/')[4]

    # 가게 주소
    address = driver.find_element(By.XPATH,'//span[@class="LDgIH"]').text

    # 오시는 길
    directions = driver.find_elements(By.CLASS_NAME,'xHaT3')
    if len(directions) == 0:
        directions_text = ' ' #오시는 길 없으면 None
    else:
        directions[0].click()
        sleep(1)
        directions_text = directions[0].text

    
    try:
        driver.find_element(By.XPATH,'//div[@class="y6tNq"]//span').click()

        # 영업 시간 더보기 버튼을 누르고 2초 반영시간 기다림
        sleep(2)

        parent_element = driver.find_element(By.XPATH,'//a[@class="gKP9i RMgN0"]')
        child_elements = parent_element.find_elements(By.XPATH, './*[@class="w9QyJ" or @class="w9QyJ undefined"]')

        for child in child_elements:
            # 각 자식 요소 내에서 클래스가 'A_cdD'인 span 요소 찾기
            span_elements = child.find_elements(By.XPATH, './/span[@class="A_cdD"]')

            # 찾은 span 요소들의 텍스트 출력
            for span in span_elements:
                actions = ActionChains(driver)
                actions.move_to_element(span).perform()  # 요소로 스크롤 이동
                business_hours.append(span)
        business_hours_texts = [i.text for i in business_hours]
        
        # 가게 전화번호
        phone_num = driver.find_element(By.XPATH,'//span[@class="xlx7Q"]').text
    except:
        print(print('------------ 영업시간 / 전화번호 부분 오류 ------------'))
        phone_num = ''
    
    return store_name, category, new_open, rating, visited_review, directions_text, store_id, address,blog_review , phone_num, business_hours_texts