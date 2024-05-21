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
        root = ET.fromstring(response.content)
        display_facilities(root)
    else:
        print(f"Error: {response.status_code}")


def display_facilities(root):
    facilities_listbox.delete(0, tk.END)
    for facility in root.findall('.//row'):
        name = facility.find('BIZPLC_NM').text
        latitude = facility.find('REFINE_WGS84_LAT').text
        longitude = facility.find('REFINE_WGS84_LOGT').text
        if name and latitude and longitude:
            facilities_listbox.insert(tk.END, f"{name} ({latitude}, {longitude})")


def show_google_maps(lat, lon):
    url = f"https://www.google.com/maps/@{lat},{lon},15z"
    webbrowser.open(url)


def on_facility_select(event):
    selection = facilities_listbox.curselection()
    if selection:
        index = selection[0]
        facility_info = facilities_listbox.get(index)
        name, coords = facility_info.split(' (')
        lat, lon = coords.rstrip(')').split(', ')
        show_google_maps(lat, lon)


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

# Create and place the listbox to display facilities
facilities_listbox = tk.Listbox(root)
facilities_listbox.place(x=400, y=50, width=380, height=400)  # Adjusted to fit the layout
facilities_listbox.bind('<<ListboxSelect>>', on_facility_select)

# GUI 작동
root.mainloop()