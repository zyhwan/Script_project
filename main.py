import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import xml.etree.ElementTree as ET
import webbrowser
from io import BytesIO

# api키 받아오기
API_KEY = "53410d545159465aab4d0554a9aeca36"
MAPS_API_KEY = "AIzaSyDHyb1cVoi0TvJzPEkdPBXL5DIQrUHNKIk"
BASE_URL = "https://openapi.gg.go.kr/PublicLivelihood"

regions = ["수원시", "고양시", "성남시", "용인시", "부천시", "안산시", "안양시", "남양주시", "화성시", "평택시", "의정부시", "시흥시", "파주시", "김포시", "광명시", "광주시", "군포시", "하남시", "오산시", "양주시", "구리시", "안성시", "포천시", "의왕시", "여주시", "양평군", "동두천시", "가평군", "과천시", "연천군"]

facility_data = []

def search():
    query = region_combobox.get()
    if not query:
        print("Please select a region.")
        return

    params = {
        'KEY': API_KEY,
        'SIGUN_NM': query,
        'Type': 'xml'
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content)
            display_facilities(root)
        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def display_facilities(root):
    global facility_data
    facilities_combobox['values'] = []
    facility_data = []
    for facility in root.findall('.//row'):
        name = facility.find('FACLT_NM').text
        lat = facility.find('REFINE_WGS84_LAT').text
        lon = facility.find('REFINE_WGS84_LOGT').text
        address = facility.find('REFINE_LOTNO_ADDR').text  # Extract address information

        info = {
            'name': name,
            'lat': lat,
            'lon': lon,
            'address': address,  # Store address information
            'etc_faclt_nm': facility.find('ETC_FACLT_NM').text,
            'gym_stnd': facility.find('GYM_STND').text,
            'gym_posbl_item_cont': facility.find('GYM_POSBL_ITEM_CONT').text
        }
        facility_data.append(info)

        if name:
            facilities_combobox['values'] = (*facilities_combobox['values'], name)

    if facility_data:
        facilities_combobox.current(0)
        facilities_combobox.bind("<<ComboboxSelected>>", lambda event: display_selected_facility())



def display_selected_facility():
    selected_index = facilities_combobox.current()
    selected_facility = facility_data[selected_index]

    info_text.delete(1.0, tk.END)
    info_text.insert(tk.END, f"체육관명: {selected_facility['name']}\n")
    info_text.insert(tk.END, f"시설: {selected_facility['etc_faclt_nm']}\n")
    info_text.insert(tk.END, f"면적: {selected_facility['gym_stnd']}\n")
    info_text.insert(tk.END, f"가능한 스포츠: {selected_facility['gym_posbl_item_cont']}\n")

    facility_name = selected_facility['name']
    region = region_combobox.get()  # Get the selected region from the combobox
    if facility_name and region:
        geocode_and_show_map(f"{facility_name}, {region}")

def geocode_and_show_map(address):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={MAPS_API_KEY}"
    response = requests.get(geocode_url)
    if response.status_code == 200:
        geocode_data = response.json()
        if geocode_data['status'] == 'OK':
            location = geocode_data['results'][0]['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            show_google_maps(lat, lng)
        else:
            print("Geocoding failed")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def zoom_in():
    global zoom_level
    zoom_level += 1
    display_selected_facility()  # 줌 인

def zoom_out():
    global zoom_level
    if zoom_level > 0:
        zoom_level -= 1
        display_selected_facility()  # 줌 아웃

def show_google_maps(lat, lng):
    global zoom_level
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom={zoom_level}&size=400x400&key={MAPS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        map_image = ImageTk.PhotoImage(image)
        map_label.config(image=map_image)
        map_label.image = map_image
    else:
        print(f"Error: {response.status_code}, {response.text}")

def open_email_client():
    selected_index = facilities_combobox.current()
    if selected_index >= 0 and selected_index < len(facility_data):
        selected_facility = facility_data[selected_index]
        email_address = "zyhwan010410@gmail.com"  # Replace with your email address
        subject = f"Fit Finder: {selected_facility['name']}"  # Subject of the email
        body = (f"체육관명: {selected_facility['name']}\n"
                f"시설: {selected_facility['etc_faclt_nm']}\n"
                f"면적: {selected_facility['gym_stnd']}\n"
                f"가능한 스포츠: {selected_facility['gym_posbl_item_cont']}\n")
        email_url = f"mailto:{email_address}?subject={subject}&body={body}"
        webbrowser.open(email_url)
    else:
        print("No facility selected or facility data is empty.")

# 메인 위도우 창
root = tk.Tk()
root.title("Fit Finder")
root.geometry("800x500")

# 줌인 줌아웃 글로별 변수
zoom_level = 15  # Initial zoom level

# 줌인 버튼
zoom_in_button = ttk.Button(root, text="Zoom In", command=zoom_in)
zoom_in_button.place(x=400, y=460, width=100, height=30)

# 줌 아웃 버튼
zoom_out_button = ttk.Button(root, text="Zoom Out", command=zoom_out)
zoom_out_button.place(x=510, y=460, width=100, height=30)

# 돋보기 이미지 가져오기
search_icon = tk.PhotoImage(file="돋보기.png")

# 검색 버튼
search_button = ttk.Button(root, image=search_icon, command=search)
search_button.image = search_icon
search_button.place(x=260, y=40, width=35, height=35)

# 지역 선택 콤보박스
region_combobox = ttk.Combobox(root, values=regions, state="readonly")
region_combobox.place(x=40, y=50, width=220)

# 즐겨 찾기 이미지 가져오기
favorite_icon = tk.PhotoImage(file="즐겨찾기.png")

# 즐겨 찾기 버튼
favorite_button = ttk.Button(root, image=favorite_icon)
favorite_button.image = favorite_icon
favorite_button.place(x=40, y=370, width=120, height=120)

# 지메일 이미지 가져오기
Gmail_icon = tk.PhotoImage(file="Gmail.png")

# 이메일 연동 버튼
email_button = ttk.Button(root, image=Gmail_icon, command=open_email_client)
email_button.image = Gmail_icon
email_button.place(x=160, y=370, width=120, height=120)

# 콤보박스 생성
facilities_combobox = ttk.Combobox(root, state="readonly")
facilities_combobox.place(x=40, y=90, width=300, height=25)

# 정보 출력 텍스트 박스 생성
info_text = tk.Text(root, wrap=tk.WORD)
info_text.place(x=40, y=120, width=300, height=230)

# 지도 출력 라벨 생성
map_label = ttk.Label(root)
map_label.place(x=400, y=50, width=380, height=390)

# GUI 작동
root.mainloop()