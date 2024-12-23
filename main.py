from kivy.uix.effectwidget import Rectangle
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
import requests
import json
import datetime

WEATHERAPI = "" # used to get the weather data
CITYAPI = "" # used to get the coordinates of a city

# this is a function that gets all the weather data for a city
def get_weather(city, caller):
    lon, lat = 0, 0
    # getting the latitude and longitude of the city
    cityResponse = requests.get(f"https://api.opencagedata.com/geocode/v1/json?key={CITYAPI}&q={city}")
    if cityResponse.status_code == 200:
        cityData = cityResponse.json()
        lon = cityData["results"][0]["geometry"]["lng"]
        lat = cityData["results"][0]["geometry"]["lat"]
        # getting the weather data for the coordinates
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHERAPI}")
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    else:
        if CITYAPI == "" or WEATHERAPI == "":
            caller.ids.cityName.text = "API keys not set"
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
        self.setupCheckbox()
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
        self.ids.cityList.height = 50
        self.ids.cityList.add_widget(HelpWidget())
        for city in self.caller.cities:
            self.ids.cityList.add_widget(CityWidget(city, self))
            self.ids.cityList.height += 50
    # method for checking the checkbox of the city that is the current city
    def setupCheckbox(self):
        for child in self.ids.cityList.children:
            if child.ids.cityName.text != "Name":
                if child.ids.cityName.text == self.caller.currentCity:
                    child.ids.isCurrentCity.active = True

# class for the popup that is used for showing an error message
class ErrorPopup(Popup):
    # initializing the class
    def __init__(self, message):
        super().__init__()
        self.ids.errorMessage.text = message

# class for the popup that is used for adding a city
class AddCityPopup(Popup):
    # initializing the class
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
    # method for adding a city to the list of cities
    def addCity(self):
        if self.ids.cityName.text == "" or self.ids.cityName.text in self.caller.cities:
            popup = ErrorPopup("City already added or field is empty")
            popup.open()
        else:
            self.caller.cities.append(self.ids.cityName.text)
            self.caller.writeToFile()
            self.writeToHistory()
            self.dismiss()
    # method for setting up the history of added cities spinner using the history.json file
    def setupSpinner(self):
        file = open("history.json", "r")
        data = json.load(file)
        file.close()
        if len(data) == 0:
            return
        else:
            self.ids.historySpinner.values.clear()
            for city in data:
                text = city["Name"]
                if len(text) > 10:
                    text = text[:10] + "..."
                self.ids.historySpinner.values.append(text)
    # method for writing the added city to the history of the searched cities (history.json)
    def writeToHistory(self):
        file = open("history.json", "r")
        data = json.load(file)
        file.close()
        data.append({"Name": self.ids.cityName.text})
        if len(data) > 10:
            data.pop(0)
        file = open("history.json", "w")
        json.dump(data, file)
        file.close()
    # method for setting the text of the text input to the selected value of the history spinner
    def setTextInput(self):
        if self.ids.historySpinner.text != "" and self.ids.historySpinner.text != "History":
            self.ids.cityName.text = self.ids.historySpinner.text
        self.ids.historySpinner.text = "History"
    # method for setting API keys popup
    def setAPIs(self):
        popup = APIPopup(self)
        popup.open()

# class for the popup that is used for setting the API keys
class APIPopup(Popup):
    # initializing the class
    def __init__(self, caller):
        super().__init__()
        self.caller = caller
    # method for setting the API keys entered by the user
    def setAPIs(self):
        if self.ids.openWeatherMapAPI.text != "":
            global WEATHERAPI
            WEATHERAPI = self.ids.openWeatherMapAPI.text
        if self.ids.timezoneDBAPI.text != "":
            global CITYAPI
            CITYAPI = self.ids.timezoneDBAPI.text
        self.caller.caller.setup(False)
        self.writeAPIs()
        self.dismiss()
    # method for writing the API keys to the file (APIK.json)
    def writeAPIs(self):
        with open("APIK.json", "w") as file:
            json.dump({"OpenWeatherMap": WEATHERAPI, "CityAPI": CITYAPI}, file)
        file.close()

# class for the help widget, this is the widget that is used for displaying the help text in the list of cities popup
class HelpWidget(BoxLayout):
    pass

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
        if self.ids.isCurrentCity.active == True:
            for child in self.caller.ids.cityList.children:
                if child.ids.cityName.text != "Name":
                    if child.ids.isCurrentCity.active == True:
                        child.ids.isCurrentCity.active = False
            self.caller.caller.currentCity = self.ids.cityName.text
            self.ids.isCurrentCity.active = True
            self.caller.caller.writeToFile()
            self.caller.caller.setup(False)
        else:
            self.ids.isCurrentCity.active = True

# main grid class, this is the main grid on the main screen
class MainGrid(BoxLayout):
    # initializing the class
    def __init__(self):
        super().__init__()
        self.bind(size = self.setBackground, pos = self.setBackground) # binding the background image to the size and position of the grig, because otherwise it woudnt resize correctly
    # method for setting up all the labels with the weather data of the current city
    def load_city(self):
        info = get_weather(self.currentCity, self)
        if info != None:
            self.weather = str(info["weather"][0]["description"])
            self.ids.cityName.text = str(self.currentCity)
            self.ids.temperature.text = str(round(info["main"]["temp"] - 273.15, 2)) + "°C"
            self.ids.weather.text = str(info["weather"][0]["description"])
            self.ids.feelsLike.text = str(round(info["main"]["feels_like"] - 273.15, 2)) + "°C"
            self.ids.high.text = str(round(info["main"]["temp_max"] - 273.15, 2)) + "°C"
            self.ids.low.text = str(round(info["main"]["temp_min"] - 273.15, 2)) + "°C"
            sunrise = datetime.datetime.fromtimestamp(info["sys"]["sunrise"])
            self.ids.sunrise.text = str(sunrise.hour) + ":" + str(sunrise.minute)
            sunset = datetime.datetime.fromtimestamp(info["sys"]["sunset"])
            self.ids.sunset.text = str(sunset.hour) + ":" + str(sunset.minute)
            self.ids.windSpeedDirection.text = str(info["wind"]["speed"]) + "m/s " + str(info["wind"]["deg"]) + "°"
            self.ids.humidity.text = str(info["main"]["humidity"]) + "%"
            # getting info for the sunrise and sunset
            self.sunrise = info["sys"]["sunrise"]
            self.sunset = info["sys"]["sunset"]
            self.timeIn = info["dt"]
    # method for opening the popup used for adding a city
    def addCity(self):
        popup = AddCityPopup(self)
        popup.open()
    # method for setting up the app, this is called after the main grid is created and if the current city is changed
    def setup(self, call = False):
        if call: # the things insed this if statement are only called once(when the app is started), otherwise it could cause issues with file writing
            self.getCities()
            self.getAPIKeys()
            self.clockEvent = Clock.schedule_interval(self.setup, 120) # every 2 minutes the weather data is updated, the free version of the API only allows 60 calls per minute, so this should have enough room in case the user changes the current city multiple times
        self.load_city()
        self.setBackground()
    # method for getting the API keys from the file (APIK.json)
    def getAPIKeys(self):
        try:
            with open("APIK.json", "r") as file:
                data = json.load(file)
            file.close()
            global WEATHERAPI, CITYAPI
            WEATHERAPI = data["OpenWeatherMap"]
            CITYAPI = data["CityAPI"]
        except:
            with open("APIK.json", "w") as file:
                json.dump({"OpenWeatherMap": "", "CityAPI": ""}, file)
            file.close()
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
                self.canvas.before.add(Rectangle(source="snow.jpg", size = self.size, pos = self.pos))
            else:
                self.canvas.before.add(Rectangle(source="default.jpg", size = self.size, pos = self.pos))
        else:
            self.canvas.before.add(Rectangle(source="default.jpg", size = self.size, pos = self.pos))
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
        self.cities = []
        try:
            with open("data.json", "r") as file:
                data = json.load(file)
            file.close()
            for key in data:
                if key["CurrentCity"] == "Yes":
                    self.currentCity = key["Name"]
                self.cities.append(key["Name"])
        except:
            with open("data.json", "w") as file:
                json.dump({"Name": "Paris", "CurrentCity": "No"}, file)
            file.close()
    # method for saving all the old and newly added cities, called every time a city is added or deleted
    def writeToFile(self):
        # clearing the file
        File = open("data.json", "w")
        json.dump([], File)
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