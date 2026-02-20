import tkinter as tk
from tkinter import filedialog, messagebox
import requests

API_URL = "http://127.0.0.1:8000/classify"

def send_image():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    with open(file_path, "rb") as f:
        response = requests.post(
            API_URL,
            files={"file": f}
        )

    if response.status_code == 200:
        data = response.json()
        messagebox.showinfo(
            "Classification Result",
            f"Item: {data['item']}\n"
            f"Category: {data['category']}\n"
            f"Recyclable: {data['recyclable']}\n"
            f"Confidence: {data['confidence']}"
        )
    else:
        messagebox.showerror("Error", "Failed to analyze image")

root = tk.Tk()
root.title("Recycling AI")

btn = tk.Button(root, text="Upload Image", command=send_image)
btn.pack(padx=20, pady=20)

root.mainloop()
