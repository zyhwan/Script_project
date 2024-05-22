import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import xml.etree.ElementTree as ET
import webbrowser

API_KEY = "53410d545159465aab4d0554a9aeca36"
BASE_URL = "https://openapi.gg.go.kr/PublicLivelihood"

def search():
    query = entry.get()
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
    facilities_combobox['values'] = []
    facility_data = []
    for facility in root.findall('.//row'):
        name = facility.find('FACLT_NM').text
        lat = facility.find('REFINE_WGS84_LAT').text
        lon = facility.find('REFINE_WGS84_LOGT').text

        info = {
            'name': name,
            'lat': lat,
            'lon': lon,
            'etc_faclt_nm': facility.find('ETC_FACLT_NM').text,
            'gym_stnd': facility.find('GYM_STND').text,
            'gym_posbl_item_cont': facility.find('GYM_POSBL_ITEM_CONT').text
        }
        facility_data.append(info)

        if name:
            facilities_combobox['values'] = (*facilities_combobox['values'], name)

    if facility_data:
        facilities_combobox.current(0)
        facilities_combobox.bind("<<ComboboxSelected>>", lambda event: display_selected_facility(facility_data))

def display_selected_facility(facility_data):
    selected_index = facilities_combobox.current()
    selected_facility = facility_data[selected_index]

    info_text.delete(1.0, tk.END)
    info_text.insert(tk.END, f"Name: {selected_facility['name']}\n")
    info_text.insert(tk.END, f"Facilities: {selected_facility['etc_faclt_nm']}\n")
    info_text.insert(tk.END, f"Dimensions: {selected_facility['gym_stnd']}\n")
    info_text.insert(tk.END, f"Available Items: {selected_facility['gym_posbl_item_cont']}\n")

    lat = selected_facility['lat']
    lon = selected_facility['lon']
    if lat and lon:
        show_google_maps(lat, lon)

def show_google_maps(lat, lon):
    url = f"https://www.google.com/maps/@{lat},{lon},15z"
    webbrowser.open(url)

def open_email_client():
    email_address = "your_email@example.com"  # Replace with your email address
    subject = "Feedback on Fit Finder"  # Subject of the email
    body = "Write your feedback here..."  # Body of the email
    email_url = f"mailto:{email_address}?subject={subject}&body={body}"
    webbrowser.open(email_url)

# 메인 위도우 창
root = tk.Tk()
root.title("Fit Finder")
root.geometry("800x500")

# 돋보기 이미지 가져오기
search_icon = tk.PhotoImage(file="돋보기.png")

# search 버튼
search_button = ttk.Button(root, image=search_icon, command=search)
search_button.image = search_icon
search_button.place(x=260, y=40, width=35, height=35)

# 검색 박스
entry = ttk.Entry(root)
entry.place(x=50, y=50, width=200)

# 즐겨 찾기 이미지 가져오기
favorite_icon = tk.PhotoImage(file="즐겨찾기.png")

# 즐겨 찾기 버튼
favorite_button = ttk.Button(root, image=favorite_icon)
favorite_button.image = favorite_icon
favorite_button.place(x=30, y=370, width=120, height=120)

# 지메일 이미지 가져오기
Gmail_icon = tk.PhotoImage(file="Gmail.png")

# 이메일 연동 버튼
email_button = ttk.Button(root, image=Gmail_icon, command=open_email_client)
email_button.image = Gmail_icon
email_button.place(x=150, y=370, width=120, height=120)

# 콤보박스 생성
facilities_combobox = ttk.Combobox(root, state="readonly")
facilities_combobox.place(x=400, y=50, width=380, height=25)

# 정보 출력 텍스트 박스 생성
info_text = tk.Text(root, wrap=tk.WORD)
info_text.place(x=400, y=80, width=380, height=370)

# GUI 작동
root.mainloop()
