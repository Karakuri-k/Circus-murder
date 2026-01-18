from lists import *
import random as rd
from constants import *

selectedNames = rd.sample(maleNames + femaleNames, numPeople)
selectedTitles = rd.sample(titles, numPeople)
class Evening:
    def __init__(self) -> None:
        self.start = "13:00"
        self.end = "23:30"
        self.timestamps = self.generateTimestamps(self.start, self.end)
        self.locations = self.generateLocations(5)
        self.characters = self.generateCharacters(numPeople)

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

        for i in range(numberOfCharacters):
            alibi = self.generateAlibis()
            listOfCharacters.append(Person(selectedNames[i], alibi, selectedTitles[i]))


        murderTime = rd.choice(self.timestamps[:-1])
        crimeScene = rd.choice(self.locations)
        murderIndex = self.timestamps.index(murderTime)

        murderer = rd.choice(listOfCharacters)
        victim = rd.choice([character for character in listOfCharacters if character != murderer])

        murderer.isMurderer = True
        victim.isVictim = True

        self.murderer = murderer
        self.victim = victim

        self.murderTime = murderTime
        murderer.timeToLie = []

        self.crimeScene = crimeScene
        murderer.alibiSchedule[murderTime] = crimeScene #gjør morderen sin location til crime scene
        victim.alibiSchedule[murderTime] = crimeScene
        criticalTimestamps = self.timestamps[murderIndex:] #tiden fra drap til kroppen blir funnet

        for timestamp in criticalTimestamps:
            for character in listOfCharacters:
                if character != murderer:
                    if character.alibiSchedule[timestamp] == crimeScene:
                        other_locations = [loc for loc in self.locations if loc != crimeScene]
                        character.alibiSchedule[timestamp] = rd.choice(other_locations) #gjør alle andres locations hvis de er i crime scene før kroppen blir funnet til et annet sted
                if character == victim:
                    character.alibiSchedule[timestamp] = crimeScene 
                if character == murderer:
                    if character.alibiSchedule[timestamp] == crimeScene:
                        self.murderer.timeToLie.append(timestamp)
        return listOfCharacters
        


class Person:
    def __init__(self, firstName, alibiSchedule, title, isMurderer = False, isVictim = False, timeToLie = []) -> None:
        self.timeToLie = timeToLie
        self.title = title
        self.firstName = firstName
        self.lastName = rd.choice(lastNames)
        self.fullName:str = self.firstName + " " + self.lastName
        self.alibiSchedule = alibiSchedule
        self.isMurderer = isMurderer


    def whereWereYou(self, time, b:Evening):
        if self.isMurderer and time in self.timeToLie:
            randomLocation = rd.choice([loc for loc in b.locations if loc != b.crimeScene])
            availablePeople = [char for char in b.characters if char != self and char != b.victim]
            randomNumber = rd.randint(0, len(availablePeople))
            randomPeople = rd.sample(availablePeople, randomNumber) if randomNumber > 0 else []

            if len(randomPeople) == 0:
                return f"At {time}, I was in the {randomLocation}. I was alone."
            elif len(randomPeople) == 1:
                return f"At {time}, I was in the {randomLocation} with {randomPeople[0]}."
            else:
                murdererWhereWereYou = ", ".join(str(char) for char in randomPeople[:-1]) + f" and {randomPeople[-1]}"
                return f"At {time}, I was in the {randomLocation} with {murdererWhereWereYou}."
        else:   
            together = []
            for character in b.characters:
                if character.alibiSchedule[time] == self.alibiSchedule[time]:
                    together.append(character)
            if len(together) == 0:
                return f"At {time}, I was in the {self.alibiSchedule[time]}. I was alone."
            elif len(together) == 1:
                return f"At {time}, I was in the {self.alibiSchedule[time]} with {together[0]}."
            else:
                togetherString = ", ".join(str(char) for char in together[:-1]) + f" and {together[-1]}"
                return f"At {time}, I was in the {self.alibiSchedule[time]} with {togetherString}."
    def haveYouSeen(self, person:Person, b:Evening):
        seen = []
        for time in b.timestamps:
            if person.alibiSchedule[time] == self.alibiSchedule[time]:
                if time not in self.timeToLie:
                    seen.append(time)
                else:
                    pass

        if len(seen) == 0:
            return f"No, I don't believe i have seen {person} all night."
        elif len(seen) == 1:
            return f"Yes, I saw them once in {self.alibiSchedule[seen[0]]} at {seen[0]} o'clock."
        else: 
            sightings = [f"in the {self.alibiSchedule[time]} at {time}" for time in seen[:-1]]
            sightingsString = ", ".join(sightings)  + f" and in the {self.alibiSchedule[seen[-1]]} at {seen[-1]}"
            return f"Yes, I saw them {sightingsString}"
                

    def __repr__(self) -> str:
        return f"{self.title} {self.fullName}"

class Suspect(Person):
    def __init__(self, firstName, alibiSchedule, title) -> None:
        super().__init__(firstName, alibiSchedule, title)


class Murderer(Suspect):
    def __init__(self, firstName, alibiSchedule, title, timeToLie:list) -> None:
        super().__init__(firstName, alibiSchedule, title)
        self.timeToLie = timeToLie

    
