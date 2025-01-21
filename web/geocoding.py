import os
import requests
from dotenv import load_dotenv

def geocode_address_naver(address, client_id, client_secret):
    """
    주소를 Naver Maps Geocoding API로 위도와 경도로 변환.
    
    Parameters:
    - address (str): 지리 좌표를 구할 주소
    - client_id (str): Naver API Client ID
    - client_secret (str): Naver API Client Secret

    Returns:
    - tuple: (위도, 경도) 또는 None
    """
    base_url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
    }
    params = {"query": address}

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if "addresses" in data and len(data["addresses"]) > 0:
            lat = float(data["addresses"][0]["y"])
            lng = float(data["addresses"][0]["x"])
            return lng, lat
        else:
            print("No results found.")
            return None
    else:
        print(f"HTTP Error: {response.status_code}")
        return None


load_dotenv()

# 환경 변수 가져오기
naver_client_id = os.getenv("NCP_CLIENT_ID")
naver_client_secret = os.getenv("NCP_CLIENT_SECRET")
# 사용 예제
address = "서울 중구 명동10길 29"
coordinates = geocode_address_naver(address, naver_client_id, naver_client_secret)

if coordinates:
    print(f"Address: {address}, Coordinates: {coordinates}")
else:
    print("Geocoding failed.")
