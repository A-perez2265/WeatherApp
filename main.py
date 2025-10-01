import tkinter as tk
import requests
from tkinter import messagebox
from PIL import Image, ImageTk
import ttkbootstrap
import speech_recognition as sr
from datetime import datetime
import pytz

root = ttkbootstrap.Window(themename="superhero")
root.title("Weather App")
root.geometry("400x700")

#Placeholder text
placeholder_text = "Please Enter a City"

#Empty List for past searches
search_history = []

#Function holds request to get the weather data
def get_weather(city):
    API_key ="paste in ur API key"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}"
    res = requests.get(url)
    # error message for not found city
    if res.status_code == 404:
        messagebox.showerror("Error", "City not found")
        return None
    # parse JSON weather information
    weather = res.json()
    icon_id = weather['weather'][0]['icon']
    temperature = (weather['main']['temp']-273.15)*1.8+32
    feels_like = (weather['main']['feels_like']-273.15)*1.8+32
    timestamp = weather['dt']
    description = weather['weather'][0]['description']
    city = weather['name']
    country = weather['sys']['country']
    icon_url = f"https://openweathermap.org/img/wn/{icon_id}@4x.png"
    last_updated_datetime = datetime.utcfromtimestamp(timestamp)

    # convert utc to local timezone
    local_timezone = pytz.timezone("America/Chicago")
    local_time = last_updated_datetime.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    formatted_time = local_time.strftime('%m-%d-%y %H:%M:%S')

    return icon_url, temperature, feels_like, formatted_time, description, city, country


#Function to search weather for a city
def search():
    city = user_city.get()
    if city == placeholder_text or not city.strip():
        messagebox.showerror("Error","Please enter a valid city name.")
        return
    result = get_weather(city)
    if result is None:
        return
    icon_url, temperature, feels_like, formatted_time, description, city, country = result
    location_label.configure(text=f"{city},{country}")

    # getting weather icon images
    image = Image.open(requests.get(icon_url,stream=True).raw)
    icon = ImageTk.PhotoImage(image)
    weather_icon.configure(image =icon)
    weather_icon.image = icon

    # update temp and description
    temperature_label.configure (text=f"Temperature : {temperature:.1f}°F")
    weather_description.configure (text=f"Description: {description}")
    weather_feels_label.configure (text=f"Feels Like: {feels_like:.1f}°F")
    weather_formatted_time_label.configure(text=f"Last Updated: {formatted_time}")

    #adds city into search history list if not already in
    if city not in search_history:
        search_history.append(city)
        update_search_history()

#function to update listbox search history
def update_search_history():
    history_listbox.delete(0, tk.END)
    for city in search_history:
        history_listbox.insert(tk.END, city)
#function that allows user to select an item from search history
def select_history(event):
    selection = history_listbox.get(tk.ACTIVE)
    user_city.delete(0, tk.END)
    user_city.insert(0, selection)
    search()

def voice_search():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for a city")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            city = recognizer.recognize_google(audio)
            print(f"Recognized city: {city}")
            user_city.delete(0,tk.END)
            user_city.insert(0,city)
            search()
        except sr.UnknownValueError:
            messagebox.showerror("Error","Could not understand the audio")
        except sr.RequestError:
            messagebox.showerror("Error","Error with the speech recognition service")


#Placeholder management
def clear_placeholder(event):
    if user_city.get() == placeholder_text:
        user_city.delete(0,tk.END)
        user_city.config(foreground="white")

def restore_placeholder(event):
    if not user_city.get():
        user_city.insert(0,placeholder_text)
        user_city.config(foreground="gray")


#Label Widget to show city/country name
location_label = tk.Label(root, font="Verdana, 18")
location_label.pack(pady=20)

#Label widget to show weather icon
weather_icon = tk.Label(root)
weather_icon.pack()

#Temperature label Widget
temperature_label = tk.Label(root, font="Verdana, 18")
temperature_label.pack()

# feels like widget
weather_feels_label = tk.Label(root,font="Verdana, 18")
weather_feels_label.pack()

#Weather description label Widget
weather_description = tk.Label(root, font="Verdana, 18")
weather_description.pack()

#last update widget
weather_formatted_time_label = tk.Label(root, font="Verdana, 12")
weather_formatted_time_label.pack(side=tk.BOTTOM)

#Enter City name widget
user_city = ttkbootstrap.Entry(root, font="Verdana, 18")
user_city.pack(pady=10)
user_city.insert(0,placeholder_text)
user_city.config(foreground="gray")


#binding events to manage placeholder
user_city.bind("<FocusIn>",clear_placeholder)
user_city.bind("<FocusOut>", restore_placeholder)

#Search Button Widget
search_button = ttkbootstrap.Button(root, text="Search", command=search, bootstyle='primary')
search_button.pack(pady=10)


# Voice search button
voice_button = ttkbootstrap.Button(root,text="Voice Search", command=voice_search,bootstyle='info')
voice_button.pack(pady=10)

#Bind enter key to search button
root.bind('<Return>', lambda event: [search(), user_city.delete(0, tk.END)])

#Listbox for search history
history_label = tk.Label(root,text="Past Searches", font="Verdana, 18")
history_label.pack(pady=10)
history_listbox = tk.Listbox(root, height = 5, width = 50,font="Verdana, 18", selectmode=tk.SINGLE)
history_listbox.pack(pady=10)
history_listbox.bind("<<ListboxSelect>>", select_history)

update_search_history()

root.mainloop()