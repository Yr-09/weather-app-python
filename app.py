import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import json
import os
import random
from config import API_KEY, BASE_URL

# Файл истории
HISTORY_FILE = "history.json"

# Загрузка истории
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Сохранение в историю
def save_to_history(city, weather_data):
    history = load_history()
    entry = {
        "город": city,
        "температура": weather_data["temp"],
        "погода": weather_data["description"]
    }
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# Получение погоды
def get_weather():
    city = entry_city.get().strip()
    if not city:
        messagebox.showwarning("Ошибка", "Введите название города!")
        return

    url = f"{BASE_URL}?q={city}&appid={API_KEY}&lang=ru&units=metric"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            messagebox.showerror("Ошибка", "Город не найден.")
            return
        elif response.status_code != 200:
            messagebox.showerror("Ошибка", f"Код ошибки: {response.status_code}")
            return

        data = response.json()
        temp = round(data["main"]["temp"])
        feels_like = round(data["main"]["feels_like"])
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        desc = data["weather"][0]["description"].capitalize()

        # Отображение
        result_text.set(f"🌡 Температура: {temp}°C (ощущается как {feels_like}°C)")
        desc_text.set(f"☁ Погода: {desc}")
        humidity_text.set(f"💧 Влажность: {humidity}%")
        wind_text.set(f"💨 Ветер: {wind_speed} м/с")

        # Сохранение в историю
        save_to_history(city, {"temp": temp, "description": desc})

        # Совет по погоде
        tips = [
            "Не забудьте зонт, если идёт дождь!",
            "Сегодня отличный день для прогулки!",
            "Одевайтесь теплее — прохладно!",
            "Идеальная погода для кофе и книг.",
            "Солнечно Не забудьте солнцезащитные очки."
        ]
        advice_text.set(f"💡 Совет: {random.choice(tips)}")

    except requests.ConnectionError:
        messagebox.showerror("Ошибка", "Нет подключения к интернету.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Показ истории
def show_history():
    history = load_history()
    if not history:
        messagebox.showinfo("История", "История пуста.")
        return

    history_window = tk.Toplevel(root)
    history_window.title("История запросов")
    history_window.geometry("400x300")

    text_area = scrolledtext.ScrolledText(history_window, font=("Arial", 10))
    text_area.pack(expand=True, fill="both", padx=10, pady=10)

    for entry in history:
        text_area.insert(tk.END, f"📍 {entry['город']}\n")
        text_area.insert(tk.END, f"   {entry['температура']}°C, {entry['погода']}\n\n")
    text_area.configure(state="disabled")

# GUI
root = tk.Tk()
root.title("🌤 Погодное приложение")
root.geometry("500x500")
root.resizable(False, False)

tk.Label(root, text="Узнайте погоду в вашем городе", font=("Arial", 16, "bold")).pack(pady=15)

tk.Label(root, text="Город:", font=("Arial", 12)).pack()
entry_city = tk.Entry(root, width=30, font=("Arial", 12))
entry_city.pack(pady=5)

tk.Button(root, text="Узнать погоду", command=get_weather, bg="lightblue", font=("Arial", 10)).pack(pady=10)

# Результаты
result_text = tk.StringVar(value="...")
desc_text = tk.StringVar(value="...")
humidity_text = tk.StringVar(value="...")
wind_text = tk.StringVar(value="...")
advice_text = tk.StringVar(value="💡 Совет по погоде появится здесь")

tk.Label(root, textvariable=result_text, font=("Arial", 12), fg="blue").pack(pady=5)
tk.Label(root, textvariable=desc_text, font=("Arial", 11)).pack(pady=3)
tk.Label(root, textvariable=humidity_text, font=("Arial", 11)).pack(pady=3)
tk.Label(root, textvariable=wind_text, font=("Arial", 11)).pack(pady=3)
tk.Label(root, textvariable=advice_text, font=("Arial", 10, "italic"), fg="green", wraplength=450).pack(pady=15)

tk.Button(root, text="Показать историю", command=show_history, bg="lightyellow", font=("Arial", 10)).pack(pady=10)

root.mainloop()
