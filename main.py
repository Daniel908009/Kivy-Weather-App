from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import requests


WEATHERAPI = "" # used to get the weather data
CITYAPI = "" # used to get the coordinates of a city

def get_weather(city):
    lon, lat = 14.4378, 50.0755 # will later be replaced with the actual coordinates from a city entered by the user
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHERAPI}")
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print("Error in fetching the data")




class MainGrid(BoxLayout):
    def test_request(self):
        get_weather("London") # later the city will be fetched from an input field




class WeatherApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        return MainGrid()
    
if __name__ == "__main__":
    WeatherApp().run()