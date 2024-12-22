from kivy.app import App
from kivy.uix.gridlayout import GridLayout
import requests


API = ""

def get_weather(city):
    lon, lat = 14.4378, 50.0755 # will later be replaced with the actual coordinates from a city entered by the user
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API}")
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print("Error in fetching the data")




class MainGrid(GridLayout):
    def test_request(self):
        get_weather("London")




class WeatherApp(App):
    def build(self):
        return MainGrid()
    
if __name__ == "__main__":
    WeatherApp().run()