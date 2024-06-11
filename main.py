import tkinter as tk
from tkinter import ttk

#import HEAD
from PIL import Image, ImageTk
import requests
import xml.etree.ElementTree as ET
import webbrowser
from io import BytesIO
import config
import time
import pygame
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import font_manager, rc
import telepot


# matplotlib 백엔드 설정
import matplotlib
matplotlib.use("TkAgg")

bot = telepot.Bot('7329831774:AAF8z4z3L6gI20n18cOM0WSJ9w1sFNJaQV0')
bot.getMe()

# api키 받아오기
API_KEY = config.API_KEY
MAPS_API_KEY = config.MAPS_API_KEY
BASE_URL = "https://openapi.gg.go.kr/PublicLivelihood"

regions = ["수원시", "고양시", "성남시", "용인시", "부천시", "안산시", "안양시", "남양주시", "화성시", "평택시", "의정부시", "시흥시", "파주시", "김포시", "광명시", "광주시", "군포시", "하남시", "오산시", "양주시", "구리시", "안성시", "포천시", "의왕시", "여주시", "양평군", "동두천시", "가평군", "과천시", "연천군"]

facility_data = []
favorites = set()
bgm_playing = True

# Initialize pygame mixer
pygame.mixer.init()
pygame.mixer.music.load("프리스타일_-_7_-_Y.mp3")  # Replace with your BGM file path
pygame.mixer.music.play(-1)  # Play the music in a loop

# 전역 변수로 모든 시설 정보를 갖고 있는 리스트 생성
all_facilities = []

def fetch_all_facilities():
    global all_facilities
    all_facilities = []  # 전역 리스트 초기화
    for region in regions:
        params = {
            'KEY': API_KEY,
            'SIGUN_NM': region,
            'Type': 'xml'
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
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
                        'gym_posbl_item_cont': facility.find('GYM_POSBL_ITEM_CONT').text,
                        'region': region  # Add 'region' field
                    }
                    all_facilities.append(info)
            except ET.ParseError as e:
                print(f"XML Parse Error: {e}")
        else:
            print(f"Error: {response.status_code}, {response.text}")

def send_facility_info_via_telegram():
    selected_index = facilities_combobox.current()
    if selected_index >= 0 and selected_index < len(facility_data):
        selected_facility = facility_data[selected_index]
        chat_id = '7465298776'  # 대상 사용자의 채팅 ID로 변경해야 합니다.

        message = f"체육관명: {selected_facility['name']}\n"
        message += f"시설: {selected_facility['etc_faclt_nm']}\n"
        message += f"면적: {selected_facility['gym_stnd']}\n"
        message += f"가능한 스포츠: {selected_facility['gym_posbl_item_cont']}\n"
        message += f"주소: {selected_facility['address']}\n"

        # 텔레그램 메시지 보내기
        bot.sendMessage(chat_id, message)
    else:
        print("No facility selected or facility data is empty.")

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
    update_combobox_values()
    if facility_data:
        facilities_combobox.current(0)
        facilities_combobox.bind("<<ComboboxSelected>>", lambda event: display_selected_facility())

def update_combobox_values():
    facility_names = [
        f"{'*' if info['name'] in favorites else ''} {info['name']}"
        for info in facility_data
    ]
    facilities_combobox['values'] = facility_names

def update_time():
    now = time.strftime("%Y년 %m월 %d일\n%H시  %M분  %S초", time.localtime())
    time_label.config(text=now)
    root.after(1000, update_time)

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
        display_selected_facility()

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
def toggle_favorite():
    selected_index = facilities_combobox.current()
    if selected_index >= 0 and selected_index < len(facility_data):
        facility_name = facility_data[selected_index]['name']
        if facility_name in favorites:
            favorites.remove(facility_name)
        else:
            favorites.add(facility_name)
        update_combobox_values()  # Combobox 업데이트
        update_favorites_listbox()  # 즐겨찾기 리스트 박스 업데이트
    else:
        print("No facility selected or facility data is empty.")
def update_favorites_listbox():
    favorites_listbox.delete(0, tk.END)
    for facility_name in favorites:
        favorites_listbox.insert(tk.END, facility_name)

def toggle_bgm():
    global bgm_playing
    if bgm_playing:
        pygame.mixer.music.pause()
        bgm_button.config(image=mute_icon)
    else:
        pygame.mixer.music.unpause()
        bgm_button.config(image=unmute_icon)
    bgm_playing = not bgm_playing

#전역변수
fig=None
def show_facility_counts():
    # 한글 폰트 설정
    font_path = "C:/Windows/Fonts/malgun.ttf"  # 한글 폰트 경로 설정 (본인 환경에 맞게 변경)
    font_name = font_manager.FontProperties(fname=font_path).get_name()
    rc('font', family=font_name)

    # 각 지역별로 체육 시설 수를 저장할 딕셔너리 생성
    facility_counts = Counter()

    # 모든 시설의 정보를 바탕으로 각 지역별 체육 시설 수 계산
    for facility in all_facilities:
        facility_counts[facility['region']] += 1

    # 새로운 윈도우 생성
    counts_window = tk.Toplevel(root)
    counts_window.title("도시별 시설의 수")
    counts_window.geometry("1000x800")

    # 그래프 생성
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.barh(list(facility_counts.keys()), list(facility_counts.values()), color='skyblue')
    ax.set_xlabel('체육시설 수')
    ax.set_ylabel('도시')
    ax.set_title('도시별 체육시설의 수')

    # 그래프를 Tkinter 캔버스에 표시
    canvas = FigureCanvasTkAgg(fig, master=counts_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # 스크롤바 생성
    scrollbar = ttk.Scrollbar(counts_window, orient="vertical", command=canvas.get_tk_widget().yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # 스크롤바 설정
    canvas.get_tk_widget().config(yscrollcommand=scrollbar.set)
dy=-20 # y 평행이동

# 메인 위도우 창
root = tk.Tk()
root.title("Fit Finder")
root.geometry("800x550")

# Notebook 생성
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# 메인 페이지 프레임 생성
main_frame = ttk.Frame(notebook)
notebook.add(main_frame, text='메인')

# 그래프 페이지 프레임 생성
graph_frame = ttk.Frame(notebook)
notebook.add(graph_frame, text='그래프')


# 즐겨찾기 페이지 프레임 생성
favorites_frame = ttk.Frame(notebook)
notebook.add(favorites_frame, text='즐겨찾기')

# 이미지 열기
image = Image.open("배경.png")

# 이미지 크기 조정 (원하는 크기로 조정)
image = image.resize((800, 550))

# 이미지를 Tkinter에서 사용할 수 있는 형식으로 변환
photo = ImageTk.PhotoImage(image)

# 이미지를 표시할 Label 생성
image_label = ttk.Label(graph_frame, image=photo)
image_label.pack()
image_label = ttk.Label(favorites_frame, image=photo)
image_label.pack()

# 메인 페이지 내용
ttk.Label(main_frame, text="메인 페이지").pack()

# 그래프 페이지 내용
ttk.Label(graph_frame, text="그래프 페이지").pack()

# 즐겨찾기 페이지 내용
ttk.Label(favorites_frame, text="즐겨찾기 페이지").pack()

#줌인 줌아웃 글로벌 변수
zoom_level = 15  # Initial zoom level

# 현재 시간 표시 레이블
time_label = ttk.Label(main_frame, font=("Arial", 12))
time_label.place(x=40,y=dy+60)

# 시간 업데이트 시작
update_time()
# BGM 토글 버튼
# 이미지 로드
mute_image = Image.open("소리껐을때.png")
unmute_image = Image.open("소리켰을때.png")

# 이미지 크기 조정
mute_image_resized = mute_image.resize((20, 20))
unmute_image_resized = unmute_image.resize((20, 20))

# PhotoImage 객체로 변환
mute_icon = ImageTk.PhotoImage(mute_image_resized)
unmute_icon = ImageTk.PhotoImage(unmute_image_resized)

# 버튼 생성
bgm_button = tk.Button(main_frame, image=unmute_icon, command=toggle_bgm)
bgm_button.place(x=180, y=dy+60)
# 줌인 버튼
zoom_in_button = ttk.Button(main_frame, text="Zoom In", command=zoom_in)
zoom_in_button.place(x=400, y=dy+510, width=100, height=30)

# 줌 아웃 버튼
zoom_out_button = ttk.Button(main_frame, text="Zoom Out", command=zoom_out)
zoom_out_button.place(x=510, y=dy+510, width=100, height=30)

# 돋보기 이미지 가져오기
search_icon = tk.PhotoImage(file="돋보기.png")

# 검색 버튼
search_button = ttk.Button(main_frame, image=search_icon, command=search)
search_button.image = search_icon
search_button.place(x=260, y=dy+90, width=35, height=35)

# 지역 선택 콤보박스
region_combobox = ttk.Combobox(main_frame, values=regions, state="readonly")
region_combobox.place(x=40, y=dy+100, width=220)

# 즐겨 찾기 이미지 가져오기
favorite_icon = tk.PhotoImage(file="즐겨찾기.png")

# 즐겨 찾기 버튼
favorite_button = ttk.Button(main_frame, image=favorite_icon, command=toggle_favorite)
favorite_button.image = favorite_icon
favorite_button.place(x=40, y=dy+420, width=120, height=120)

# 즐겨찾기 목록 리스트 박스
favorites_listbox = tk.Listbox(favorites_frame)
#favorites_listbox.pack()
favorites_listbox.place(x=300, y=50, width=200, height=350)
# 지메일 이미지 가져오기
Gmail_icon = tk.PhotoImage(file="Gmail.png")

# 이메일 연동 버튼
email_button = ttk.Button(main_frame, image=Gmail_icon, command=open_email_client)
email_button.image = Gmail_icon
email_button.place(x=160, y=dy+420, width=120, height=120)

# 시설 수 표시 버튼
facility_count_button = ttk.Button(graph_frame, text="도시별 시설의 수", command=show_facility_counts)
facility_count_button.place(x=300, y=dy+420, width=200, height=100)

# 콤보박스 생성
facilities_combobox = ttk.Combobox(main_frame, state="readonly")
facilities_combobox.place(x=40, y=dy+140, width=300, height=25)

# 정보 출력 텍스트 박스 생성
info_text = tk.Text(main_frame, wrap=tk.WORD)
info_text.place(x=40, y=dy+170, width=300, height=230)

# 지도 출력 라벨 생성
map_label = ttk.Label(main_frame)
map_label.place(x=400, y=dy+100, width=380, height=390)

# 프로그램 실행 시 모든 시설 정보를 가져오도록 수정
fetch_all_facilities()

# 텔레그램으로 시설 정보 보내는 버튼
telegram_icon = tk.PhotoImage(file="텔레그램.png")
send_telegram_button = ttk.Button(main_frame, image=telegram_icon, command=send_facility_info_via_telegram)
send_telegram_button.place(x=280, y=400, width=120, height=120)

# GUI 작동
root.mainloop()