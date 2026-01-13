from lists import *
import random as rd

class Evening:
    def __init__(self) -> None:
        self.start = "13:00"
        self.end = "23:30"
        self.timestamps = self.generateTimestamps(self.start, self.end)
        self.locations = self.generateLocations(5)
        self.characters = self.generateCharacters(7)

    def generateTimestamps(self, start, end, intervalMinutes = 30):
        def timeToMinutes(timeStr):
            partsOfStr = timeStr.split(":")
            hours = int(partsOfStr[0])
            minutes = int(partsOfStr[1])
            #kan skrives på en annen måte, men skrev det på måten jeg skjønte
            return hours * 60 + minutes #60 min per time
        
        def minutesToTime(minutes):
            hours = minutes // 60 #alt delt på 60 for å få timer og legg igjen rest
            mins = minutes % 60 #det som blir igjen
            return f"{hours:02d}:{mins:02d}" #returnerer det som en string klokkeslett
        

        startMins = timeToMinutes(start)
        endMins = timeToMinutes(end)

        timestamps = []
        current = startMins
        while current <= endMins:
            timestamps.append(minutesToTime(current))
            current += intervalMinutes

        return timestamps

    def generateLocations(self, numberOfLocations:int):
        locations = []
        for location in range(numberOfLocations):
            return rd.sample(listPlaces, numberOfLocations) # tar numberOfLocations antall steder fra lista listPlaces
        return locations
    
    def generateAlibis(self):
        alibi = {}
        for timestamp in self.timestamps:
            alibi[timestamp] = rd.choice(self.locations)
        return alibi

    def generateCharacters(self, numberOfCharacters):
        listOfCharacters = []

        for character in range(numberOfCharacters):
            alibi = self.generateAlibis()
            listOfCharacters.append(Person(alibi))

        murderTime = rd.choice(self.timestamps[:-1])
        crimeScene = rd.choice(self.locations)
        murderIndex = self.timestamps.index(murderTime)

        murderer = rd.choice(listOfCharacters)

        murderer.isMurderer = True
        self.murderer = murderer
        self.murderTime = murderTime
        self.crimeScene = crimeScene
        murderer.alibiSchedule[murderTime] = crimeScene #gjør morderen sin location til crime scene
        criticalTimestamps = self.timestamps[murderIndex:] #tiden fra drap til kroppen blir funnet

        for character in listOfCharacters:
            if character != murderer:
                for timestamp in criticalTimestamps:
                    if character.alibiSchedule[timestamp] == crimeScene:
                        other_locations = [loc for loc in self.locations if loc != crimeScene]
                        character.alibiSchedule[timestamp] = rd.choice(other_locations)

                        #gjør alle andres locations hvis de er i crime scene før kroppen blir funnet til et annet sted
        return listOfCharacters
        


class Person:
    def __init__(self, alibiSchedule, isMurderer = False) -> None:
        x = rd.randint(1, 2)
        if x == 1:
            self.firstName = maleNames[rd.randint(0, len(maleNames)-1)]
        else:
            self.firstName = femaleNames[rd.randint(0, len(femaleNames)-1)]

        self.lastName = lastNames[rd.randint(0, len(lastNames)-1)] 
        self.fullName:str = self.firstName + " " + self.lastName
        self.alibiSchedule = alibiSchedule
        self.isMurderer = isMurderer


    def whereWereYou(self, time):
        pass
            

    def __repr__(self) -> str:
        return self.fullName

class Suspect(Person):
    def __init__(self, alibiSchedule) -> None:
        super().__init__(alibiSchedule)

"""class Victim(Person):
    def __init__(self, name, timeOfDeath) -> None:
        super().__init__()
        self.timeOfDeath = timeOfDeath"""

class Murderer(Suspect):
    def __init__(self, alibiSchedule, timeToLie:str) -> None:
        super().__init__(alibiSchedule)
