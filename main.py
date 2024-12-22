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
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHERAPI}")
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    else:
        return None

# class for the popup that is used for confirming a choice
class ConfirmPopup(Popup):
    # initializing the class
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
    # method for the case that the user confirmed his choice
    def yes(self):
        self.dismiss()
        self.caller.yes()
    # method for the case that the user changed his mind
    def no(self):
        self.dismiss()
        self.caller.no()

# class for the popup that is used for showing all the cities that are in the data file
class ListOfCitiesPopup(Popup):
    # initializing the class
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
        self.addCities()
    # method for opening the popup for confirming the deletion of all cities
    def deleteAllCities(self):
        popup = ConfirmPopup(self)
        popup.open()
    # method for the case that the user confirmed he wants to delete all cities
    def yes(self):
        self.caller.cities.clear()
        self.ids.cityList.clear_widgets()
        self.caller.writeToFile()
    # method for the case that the user changed his mind, this is empty, but has to be here because of how the popup works
    def no(self):
        pass
    # method for adding all the cities to the scroll view
    def addCities(self):
        self.ids.cityList.height = 0
        for city in self.caller.cities:
            self.ids.cityList.add_widget(CityWidget(city, self))
            self.ids.cityList.height += 50

# class for the popup that is used for adding a city
class AddCityPopup(Popup):
    # initializing the class
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
    # method for adding a city to the list of cities
    def addCity(self): # will later have to check if the city is valid, will be done later
        self.caller.cities.append(self.ids.cityName.text)
        self.caller.writeToFile()
        self.dismiss()

# class for the city widget, this is the widget that is used for displaying the cities in the scroll view of cities inside the city menu popup
class CityWidget(BoxLayout):
    # initializing the class
    def __init__(self, city, caller):
        super().__init__()
        self.ids.cityName.text = city
        self.caller = caller
    # method for opening the popup for confirming the deletion of a city
    def deleteCity(self):
        popup = ConfirmPopup(self)
        popup.open()
    # method for the case that the user confirmed he wants to delete a city
    def yes(self):
        self.caller.ids.cityList.remove_widget(self)
        self.caller.caller.cities.remove(self.ids.cityName.text)
        self.caller.caller.writeToFile()
    # method for the case that the user changed his mind, this is empty, but has to be here because of how the popup works
    def no(self):
        pass
    # method for setting the current city to the city that was clicked
    def setCurrentCity(self):
        self.caller.caller.currentCity = self.ids.cityName.text

# main grid class, this is the main grid on the main screen
class MainGrid(BoxLayout):
    # initializing the class
    def __init__(self):
        super().__init__()
        self.bind(size = self.setBackground, pos = self.setBackground) # binding the background image to the size and position of the grig, because otherwise it woudnt resize correctly
    # method for setting up all the labels with the weather data of the current city
    def load_city(self):
        info = get_weather(self.currentCity)
        if info != None:
            self.weather = str(info["weather"][0]["description"])
            self.ids.cityName.text = str(self.currentCity)
            self.ids.weather.text = str(info["weather"][0]["description"])
            self.ids.temperature.text = str(round(info["main"]["temp"] - 273.15, 2)) + "°C"
            self.ids.humidity.text = str(info["main"]["humidity"]) + "%"
            # getting info for the sunrise and sunset
            self.sunrise = info["sys"]["sunrise"]
            self.sunset = info["sys"]["sunset"]
            self.timeIn = info["dt"]
    # method for opening the popup used for adding a city
    def addCity(self):
        popup = AddCityPopup(self)
        popup.open()
    # method for setting up the app, this is called after the main grid is created
    def setup(self):
        self.getCities()
        self.load_city()
        self.setBackground()
    # setting the background image based on the weather
    def setBackground(self, *args):
        if self.weather != "":
            self.canvas.before.clear()
            if self.checkTime():
                self.canvas.before.add(Rectangle(size = self.size, pos = self.pos, source="night.jpg"))
            elif "rain" in self.weather or "thunderstorm" in self.weather or "drizzle" in self.weather:
                self.canvas.before.add(Rectangle(source="rain.jpg", size = self.size, pos = self.pos))
            elif "cloud" in self.weather:
                self.canvas.before.add(Rectangle(source="cloudy.jpg", size = self.size, pos = self.pos))
            elif "clear" in self.weather:
                self.canvas.before.add(Rectangle(source="sunny.jpg", size = self.size, pos = self.pos))
            elif "snow" in self.weather:
                self.canvas.before.add(Rectangle(source="snow.jpg", size = self.size, pos = self.pos)) # will be added later
            else:
                self.canvas.before.add(Rectangle(source="bigMystery.jpg", size = self.size, pos = self.pos)) # will be added later
    # method for checking if it is night or day, this is used for setting the background image
    def checkTime(self):
        if self.timeIn >= self.sunset or self.timeIn <= self.sunrise:
            return True
        else:
            return False
    # method for creating the popup for showing all the cities that are in the data file
    def listOfCitiesPopup(self):
        popup = ListOfCitiesPopup(self)
        popup.open()
    # method for getting all the cities from the data file
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
    # method for saving all the old and newly added cities, called every time a city is added or deleted
    def writeToFile(self):
        # clearing the file
        File = open("data.json", "w")
        File.write("")
        File.close()
        # writing the new cities data
        data = []
        for city in self.cities:
            if city == self.currentCity:
                data.append({"Name": city, "CurrentCity": "Yes"})
            else:
                data.append({"Name": city, "CurrentCity": "No"})
        with open("data.json", "w") as file:
            json.dump(data, file)
        file.close()

# main app class
class WeatherApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1) # setting the background color
        return MainGrid()

# running the app
if __name__ == "__main__":
    WeatherApp().run()