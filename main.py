from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import requests


WEATHERAPI = "" # used to get the weather data
CITYAPI = "" # used to get the coordinates of a city

def get_weather(city):
    lon, lat = 0, 0
    cityResponse = requests.get(f"https://api.opencagedata.com/geocode/v1/json?key={CITYAPI}&q={city}")
    if cityResponse.status_code == 200:
        cityData = cityResponse.json()
        lon = cityData["results"][0]["geometry"]["lng"]
        lat = cityData["results"][0]["geometry"]["lat"]
        #print(cityData)
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHERAPI}")
        if response.status_code == 200:
            data = response.json()
            print(data)
        else:
            print("Error in fetching the data")
    else:
        print("Error in fetching the data")

class ConfirmPopup(Popup):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
    def yes(self):
        self.dismiss()
        self.caller.yes()
    def no(self):
        self.dismiss()
        self.caller.no()

class ListOfCitiesPopup(Popup):
    def __init__(self, caller):
        super().__init__()
        self.id = "listOfCitiesPopup"
        self.caller = caller
        self.addCities()
    def delete(self):
        self.ids.cityList.clear_widgets()
        self.caller.cities.clear()
    def deleteAllCities(self):
        popup = ConfirmPopup(self)
        popup.open()
    def yes(self):
        self.caller.cities.clear()
        self.ids.cityList.clear_widgets()
    def no(self):
        pass
    def addCities(self):
        self.ids.cityList.height = 0
        for city in self.caller.cities:
            self.ids.cityList.add_widget(CityWidget(city, self))
            self.ids.cityList.height += 50

class AddCityPopup(Popup):
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
    def addCity(self):
        self.caller.cities.append(self.ids.cityName.text)
        self.dismiss()

class CityWidget(BoxLayout):
    def __init__(self, city, caller):
        super().__init__()
        self.id = "cityWidget"
        self.ids.cityName.text = city
        self.caller = caller
    def deleteCity(self):
        popup = ConfirmPopup(self)
        popup.open()
    def yes(self):
        self.caller.ids.cityList.remove_widget(self)
        self.caller.caller.cities.remove(self.ids.cityName.text)
    def no(self):
        pass
    def setCurrentCity(self):
        self.caller.caller.currentCity = self.ids.cityName.text

class MainGrid(BoxLayout):
    def test_request(self):
        get_weather("Hradec nad Moravici") # later the city will be fetched from an input field
    def addCity(self):
        popup = AddCityPopup(self)
        popup.open()
    def listOfCitiesPopup(self):
        popup = ListOfCitiesPopup(self)
        popup.open()

class WeatherApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        return MainGrid()
    
if __name__ == "__main__":
    WeatherApp().run()