import tkinter as tk
from tkinter import ttk
import webbrowser

def search():
    query = entry.get()
    # Perform search functionality here
    print("Searching for:", query)

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

# Load a magnifying glass icon image
search_icon = tk.PhotoImage(file="돋보기.png")

# search 버튼
search_button = ttk.Button(root, image=search_icon, command=search)
search_button.image = search_icon
search_button.place(x=200, y=40, width=35, height=35)

# 검색 박스
entry = ttk.Entry(root)
entry.place(x=50, y=50)

# 즐겨 찾기 버튼
favorite_button = ttk.Button(root, text="즐겨찾기")
favorite_button.place(relx=0.1, rely=0.9, anchor=tk.CENTER)

# 이메일 연동 버튼
email_button = ttk.Button(root, text="이메일", command=open_email_client)
email_button.place(relx=0.23, rely=0.9, anchor=tk.CENTER)

# GUI 작동
root.mainloop()