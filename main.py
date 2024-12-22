from kivy.uix.effectwidget import Rectangle
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import requests
import json

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
            #print(data)
            return data
        else:
            #print("Error in fetching the data")
            return None
    else:
        #print("Error in fetching the data")
        return None

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
    def __init__(self):
        super().__init__()
        self.bind(size = self.setBackground, pos = self.setBackground)
    def load_city(self):
        info = get_weather(self.currentCity)
        #print("Here")
        if info != None:
            self.weather = str(info["weather"][0]["description"])
            self.ids.cityName.text = str(self.currentCity)
            #print(info["weather"][0]["description"])
            self.ids.weather.text = str(info["weather"][0]["description"])
            #print(info["main"]["temp"])
            self.ids.temperature.text = str(round(info["main"]["temp"] - 273.15, 2)) + "°C"
            #print(info["main"]["humidity"])
            self.ids.humidity.text = str(info["main"]["humidity"]) + "%"

            # getting info for the sunrise and sunset
            self.sunrise = info["sys"]["sunrise"]
            self.sunset = info["sys"]["sunset"]
            self.timeIn = info["dt"]
            # this is just for testing
            #print(self.sunrise, self.sunset, self.timeIn)
            #print(type(self.sunrise), type(self.sunset), type(self.timeIn))
            #if self.timeIn >= self.sunset or self.timeIn <= self.sunrise:
            #    print("Night")
    def addCity(self):
        popup = AddCityPopup(self)
        popup.open()
    def setup(self):
        self.getCities()
        self.load_city()
        self.setBackground()
    def setBackground(self, *args):
        if self.weather != "":
            #print(self.weather)
            self.canvas.before.clear()
            if self.checkTime():
                self.canvas.before.add(Rectangle(size = self.size, pos = self.pos, source="night.jpg"))
                #print("Night")
            elif "rain" in self.weather or "thunderstorm" in self.weather or "drizzle" in self.weather:
                self.canvas.before.add(Rectangle(source="rain.jpg", size = self.size, pos = self.pos))
                #print("Rain")
            elif "cloud" in self.weather:
                self.canvas.before.add(Rectangle(source="cloudy.jpg", size = self.size, pos = self.pos))
                #print("Cloudy")
            elif "clear" in self.weather:
                self.canvas.before.add(Rectangle(source="sunny.jpg", size = self.size, pos = self.pos))
                #print("Clear")
            elif "snow" in self.weather:
                self.canvas.before.add(Rectangle(source="snow.jpg", size = self.size, pos = self.pos)) # will be added later
                #print("Snow")
            else:
                self.canvas.before.add(Rectangle(source="bigMystery.jpg", size = self.size, pos = self.pos)) # will be added later
                #print("Default")
    def checkTime(self):
        if self.timeIn >= self.sunset or self.timeIn <= self.sunrise:
            return True
        else:
            return False
    def listOfCitiesPopup(self):
        popup = ListOfCitiesPopup(self)
        popup.open()
    def getCities(self):
        try:
            with open("data.json", "r") as file:
                data = json.load(file)
            file.close()
            for key in data:
                #print(key)
                if key["CurrentCity"] == "Yes":
                    self.currentCity = key["Name"]
                self.cities.append(key["Name"])
        except:
            #print("Error in reading the file")
            with open("data.json", "w") as file:
                json.dump({"Name": "Paris", "CurrentCity": "No"}, file)
            file.close()

class WeatherApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        return MainGrid()
    
if __name__ == "__main__":
    WeatherApp().run()