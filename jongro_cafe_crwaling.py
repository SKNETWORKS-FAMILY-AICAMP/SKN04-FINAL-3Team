from function.home_crawling import home_crawling
from function.info_crawling import info_crawling
from function.menu_crawling import menu_crawling
from function.review_like_this_part_crawling import review_like_this_part_crawling
from function.review_crawling import review_crawling

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from time import sleep

from selenium import webdriver
import pandas as pd

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'



options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
options.add_argument('window-size=1380,900')
driver = webdriver.Chrome(options=options)
driver.set_script_timeout(40)
# 대기 시간
driver.implicitly_wait(time_to_wait=3)

# 반복 종료 조건
loop = True

URL = 'https://map.naver.com/p/search/%EC%A2%85%EB%A1%9C%EA%B5%AC%20%EC%B9%B4%ED%8E%98?c=12.00,0,0,0,dh'
driver.get(url=URL)

def switch_left():
    ############## iframe으로 왼쪽 포커스 맞추기 ##############
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
    driver.switch_to.frame(iframe)
    
def switch_right():
    ############## iframe으로 오른쪽 포커스 맞추기 ##############
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
    driver.switch_to.frame(iframe)

search_bar = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div[1]/div/div/div/input')
ssearch_barer = search_bar.send_keys(Keys.ENTER)

columns = ['category', 'new_open', 'rating', 'visited_review', 'directions_text', 'store_id', 'address','blog_review' , 'phone_num', 'business_hours', 'info', 'review_like_this_part_output', 'menu']
Df = pd.DataFrame(columns=columns)

while(True):
    switch_left()
 
    # 페이지 숫자를 초기에 체크 [ True / False ]
    # 이건 페이지 넘어갈때마다 계속 확인해줘야 함 (페이지 새로 로드 될때마다 버튼 상태 값이 바뀜)
    next_page = driver.find_element(By.XPATH,'//*[@id="app-root"]/div/div[2]/div[2]/a[7]').get_attribute('aria-disabled')
    
    if(next_page == 'true'):
        break
 
    ############## 맨 밑까지 스크롤 ##############
    scrollable_element = driver.find_element(By.CLASS_NAME, "Ryr1F")
 
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
 
    while True:
        # 요소 내에서 아래로 600px 스크롤
        driver.execute_script("arguments[0].scrollTop += 600;", scrollable_element)
 
        # 페이지 로드를 기다림
        sleep(1)  # 동적 콘텐츠 로드 시간에 따라 조절
 
        # 새 높이 계산
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
 
        # 스크롤이 더 이상 늘어나지 않으면 루프 종료
        if new_height == last_height:
            break
 
        last_height = new_height
 
 
    ############## 현재 page number 가져오기 - 1 페이지 ##############
 
    page_no = driver.find_element(By.XPATH,'//a[contains(@class, "mBN2s qxokY")]').text
 
    # 현재 페이지에 등록된 모든 가게 조회
    # 첫페이지 광고 2개 때문에 첫페이지는 앞 2개를 빼야함
    if(page_no == '1'):
        elemets = driver.find_elements(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]//li')[2:]
    else:
        elemets = driver.find_elements(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]//li')
 
    print('현재 ' + '\033[95m' + str(page_no) + '\033[0m' + ' 페이지 / '+ '총 ' + '\033[95m' + str(len(elemets)) + '\033[0m' + '개의 가게를 찾았습니다.\n')
 
    for index, e in enumerate(elemets, start=1):
        final_element = e.find_element(By.CLASS_NAME,'CHC5F').find_element(By.XPATH, ".//a/div/div/span")
 
        print(str(index) + ". " + final_element.text)
 
    print(Colors.RED + "-"*50 + Colors.RESET)
 
    switch_left()
 
    sleep(2)
 
    for index, e in enumerate(elemets, start=1):
        store_name = '' # 가게 이름
        category = '' # 카테고리
        new_open = '' # 새로 오픈
        
        rating = 0.0 # 평점
        visited_review = 0 # 방문자 리뷰
        blog_review = 0 # 블로그 리뷰
        store_id = '' # 가게 고유 번호
        
        address = '' # 가게 주소
        business_hours = [] # 영업 시간
        phone_num = '' # 전화번호
        directions_text = '' #오시는 길
        switch_left()
 
 
        # 순서대로 값을 하나씩 클릭
        e.find_element(By.CLASS_NAME,'CHC5F').find_element(By.XPATH, ".//a/div/div/span").click()
 
        sleep(2)
 
        switch_right()
        
        #홈 정보 크롤링 
        store_name, category, new_open, rating, visited_review, directions_text, store_id, address,blog_review , phone_num, business_hours = home_crawling(driver, business_hours)

        #홈 정보 출력
        print(Colors.BLUE + f'{index}. ' + str(store_name) + Colors.RESET + ' · ' + str(category) + Colors.RED + str(new_open) + Colors.RESET)
        print('평점 ' + Colors.RED + str(rating) + Colors.RESET + ' / ' + str(visited_review) + ' · ' + str(blog_review))
        print(f'가게 고유 번호 -> {store_id}')
        print('가게 주소 ' + Colors.GREEN + str(address) + Colors.RESET)
        print(Colors.CYAN + '가게 영업 시간' + Colors.RESET)
        for i in business_hours:
            print(i)
            print('')
        print('가게 번호 ' + Colors.GREEN + phone_num + Colors.RESET)
        print('오시는길 :' + directions_text)
        print(Colors.MAGENTA + "-"*50 + Colors.RESET)

        #정보 소개 크롤링
        info = info_crawling(driver)

        #방문자 리뷰 이런점이 좋아요 클롤링
        review_like_this_part_output = review_like_this_part_crawling(driver)

        #메뉴 크롤링
        menu = menu_crawling(driver)

        #방문자 리뷰 크롤링링
        #review_crawling(driver)        
        
        ## 데이이터 프레임 저장장
        business_hours_temp = ''

        for i in business_hours:
            i += '\n'
            business_hours_temp += i


        Df.loc[f'{store_name}'] = [category, new_open, rating, visited_review, directions_text, store_id, address,blog_review , phone_num, business_hours_temp, info, review_like_this_part_output, menu]

        ### txt 파일로 저장 ###

        # 저장할 파일명
        output_file = f"store_info{page_no}.txt"

        # 텍스트 파일로 저장
        with open(output_file, "a", encoding="utf-8") as file:
            file.write("Start\n")
            file.write(f"{index}. {store_name} · {category} {new_open}\n")
            file.write(f"평점 {rating} / {visited_review} · {blog_review}\n")
            file.write(f"가게 고유 번호 -> {store_id}\n")
            file.write(f"가게 주소 {address}\n")
            file.write("가게 영업 시간\n")
            for i in business_hours:
                file.write(f"{i}\n")
            file.write("\n")
            file.write(f"가게 번호 {phone_num}\n")
            file.write(f"오시는길: {directions_text}\n")
            file.write("-" * 50 + "\n")
            file.write(f"가게 소개: {info}\n")
            file.write(f"메뉴: {menu}\n")
            file.write(f"이런 점이 좋았어요: {review_like_this_part_output}\n")
            file.write("End\n")


    switch_left()

    Df.to_csv(f'jong_ro_cafe{page_no}.csv', index=False)

    # 페이지 다음 버튼이 활성화 상태일 경우 계속 진행
    if(next_page == 'false'):
        driver.find_element(By.XPATH,'//*[@id="app-root"]/div/div[2]/div[2]/a[7]').click()

    # 아닐 경우 루프 정지
    else:
        loop = False

