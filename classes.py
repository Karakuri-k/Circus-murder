from lists import *
import random as rd
from constants import *
import pygame as pg

selectedNames = rd.sample(maleNames + femaleNames, numPeople)
selectedTitles = rd.sample(titles, numPeople)
class Evening:
    def __init__(self) -> None:
        self.start = "13:00"
        self.end = "23:30"
        self.timestamps = self.generateTimestamps(self.start, self.end)
        self.locations = self.generateLocations(5)
        self.characters = self.generateCharacters(numPeople)
        self.suspects = list(self.characters)
        self.suspects.remove(self.victim)

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
        currentColor = rd.sample(FARGER, numberOfCharacters)
        for i in range(numberOfCharacters):
            alibi = self.generateAlibis()
            listOfCharacters.append(Person(selectedNames[i], alibi, selectedTitles[i],currentColor[i]))


        murderTime = rd.choice(self.timestamps[:-1])
        crimeScene = rd.choice(self.locations)
        murderIndex = self.timestamps.index(murderTime)

        murderer = rd.choice(listOfCharacters)
        victim = rd.choice([character for character in listOfCharacters if character != murderer])

        murderer.isMurderer = True
        victim.isVictim = True
        murderer.motive = True
        motives = rd.sample(listOfCharacters, 3)
        for character in motives:
            character.motive = True

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
    def __init__(self, firstName, alibiSchedule, title, farge, isMurderer = False, isVictim = False, motive = False, timeToLie = None) -> None:
        self.timeToLie = timeToLie if timeToLie else []
        self.title = title
        self.firstName = firstName
        self.lastName = rd.choice(lastNames)
        self.fullName:str = self.firstName + " " + self.lastName
        self.alibiSchedule = alibiSchedule
        self.isMurderer = isMurderer
        self.motive = motive
        self.color = farge


    def whereWereYou(self, time, b:Evening):
        availablePeople = [char for char in b.characters if char != self and char != b.victim]
        if self.isMurderer and time in self.timeToLie:
            randomLocation = rd.choice([loc for loc in b.locations if loc != b.crimeScene])
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
            for person in availablePeople:
                if person.alibiSchedule[time] == self.alibiSchedule[time]:
                    together.append(person)
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
                
    def haveMotive(self, person:Person, b:Evening):
        if person.motive == False:
            return f"As far as I know {b.victim} was on good terms with {person}"
        else:
            return f"I've heard {b.victim} and {person} weren't on the best of terms"

    def __repr__(self) -> str:
        return f"{self.title} {self.fullName}"

class Murderer(Person):
    def __init__(self, firstName, alibiSchedule, title, farge, timeToLie:list) -> None:
        super().__init__(firstName, alibiSchedule, title, farge)
        self.timeToLie = timeToLie

class SuspectSprite:
    def __init__(self, x, y, person:Person, bredde=60, høyde=100):
        self.x = x
        self.y = y
        self.bredde = bredde
        self.høyde = høyde
        self.person = person
        self.farge = person.color 
        self.outline_farge = tuple(c // 2 for c in self.farge) 
        
    def draw(self, vindu):
        """Tegner suspect sprite på skjermen"""
        # Tegn skygge
        skygge_offset = 3
        pg.draw.rect(vindu, (0, 0, 0, 100),
                     (self.x - self.bredde // 2 + skygge_offset,
                     self.y - self.høyde // 2 + skygge_offset,
                     self.bredde,
                     self.høyde))
        
        # Tegn hovedrektangel
        pg.draw.rect(vindu, self.farge,
                     (self.x - self.bredde // 2,
                      self.y - self.høyde // 2,
                      self.bredde,
                      self.høyde))
        
        # Tegn outline
        pg.draw.rect(vindu, self.outline_farge,
                     (self.x - self.bredde // 2,
                      self.y - self.høyde // 2,
                      self.bredde,
                      self.høyde), 3)
        
        # Tegn øyne
        øye_farge = (255, 255, 255)
        øye_størrelse = 6
        øye_y = self.y - 20
        
        # Venstre øe
        pg.draw.circle(vindu, øye_farge,
                       (int(self.x - 10), int(øye_y)), øye_størrelse)
        pg.draw.circle(vindu, (0, 0, 0),
                       (int(self.x - 10), int(øye_y)), øye_størrelse // 2)
        
        # Høyre 
        pg.draw.circle(vindu, øye_farge,
                       (int(self.x + 10), int(øye_y)), øye_størrelse)
        pg.draw.circle(vindu, (0, 0, 0),
                       (int(self.x + 10), int(øye_y)), øye_størrelse // 2)
        
        # sprite navn
        font = pg.font.Font(None, 24)
        name_text = font.render(str(self.person), True, WHITE)
        name_rect = name_text.get_rect(center=(self.x, self.y + self.høyde // 2 + 20))
        
        # Bakgrunn navn
        bg_rect = name_rect.inflate(10, 5)
        s = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        s.fill((0, 0, 0, 180))
        vindu.blit(s, bg_rect.topleft)
        
        #navn
        vindu.blit(name_text, name_rect)

class Door:
    def __init__(self, x, y, bredde, høyde, navn="Dør", bakgrunn_fil=None, suspect = None) -> None:
        self.x = x  
        self.y = y
        self.bredde = bredde
        self.høyde = høyde
        self.navn = navn
        self.bakgrunn_fil = bakgrunn_fil  # Nytt bakgrunnsbilde for denne døren
        self.farge = (0, 255, 0, 100)  # Grønn med transparency
        self.aktiv_farge = (255, 255, 0, 150)  # Gul når karakteren er nær
        self.åpnet_farge = (255, 0, 0, 150)  # Rød når døren er åpnet
        self.is_aktiv = False
        self.er_åpnet = False
        self.interaksjons_avstand = 100  # Hvor nær karakteren må være
        self.suspect: Person | None = suspect

    def get_rect(self):
        """Returnerer rektangel i verden-koordinater"""
        return pg.Rect(self.x, self.y, self.bredde, self.høyde)

    def check_karakter_nær(self, karakter_x, karakter_y):
        """Sjekker om karakteren er nær nok til å interagere"""
        # Beregn avstanden mellom karakteren og dørens senter
        dør_senter_x = self.x + self.bredde // 2
        dør_senter_y = self.y + self.høyde // 2

        avstand_x = abs(karakter_x - dør_senter_x)
        avstand_y = abs(karakter_y - dør_senter_y)

        # Sjekk om karakteren er innenfor interaksjonsavstand
        self.is_aktiv = (avstand_x < self.interaksjons_avstand and
                         avstand_y < self.interaksjons_avstand)
        return self.is_aktiv

    def on_interact(self):
        """Åpner/lukker døren og returnerer bakgrunnsfilnavnet"""
        self.er_åpnet = not self.er_åpnet
        status = "åpnet" if self.er_åpnet else "lukket"
        print(f"{self.navn} er nå {status}!")
        return self.bakgrunn_fil if self.er_åpnet else None

    def draw(self, vindu, kamera_x, kamera_y, vis_rektangler=True):
        """Tegner bare teksten når karakteren er nær"""
        skjerm_x = self.x - kamera_x
        skjerm_y = self.y - kamera_y

        if self.is_aktiv or self.er_åpnet:
            font = pg.font.Font(None, 36)

            if self.er_åpnet:
                e_text = font.render("Trykk E for å lukke",
                                     True, (255, 255, 255))
            else:
                e_text = font.render("Trykk E for å åpne",
                                     True, (255, 255, 255))

            e_rect = e_text.get_rect(center=(skjerm_x + self.bredde // 2,
                                             skjerm_y + self.høyde // 2))

            #bakgrunn
            bg_rect = e_rect.inflate(20, 10)
            s = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
            s.fill((0, 0, 0, 180))
            vindu.blit(s, bg_rect.topleft)

            # Tegn teksten
            vindu.blit(e_text, e_rect)

class Button:
    def __init__(self, x, y, bredde, høyde, tekst, data=None, farge=(100, 100, 100), hover_farge=(150, 150, 150)):
        self.rect = pg.Rect(x, y, bredde, høyde)
        self.tekst = tekst
        self.data = data
        self.farge = farge
        self.hover_farge = hover_farge
        self.is_hovered = False
        
    def draw(self, vindu):
        # Velg farge basert på hover
        current_farge = self.hover_farge if self.is_hovered else self.farge
        
        # Tegn knapp
        pg.draw.rect(vindu, current_farge, self.rect)
        pg.draw.rect(vindu, WHITE, self.rect, 2)  # Border
        
        # Tekst
        font = pg.font.Font(None, 28)
        text_surface = font.render(self.tekst, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        vindu.blit(text_surface, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]

class DialogBox:
    def __init__(self, x, y, bredde, høyde):
        self.rect = pg.Rect(x, y, bredde, høyde)
        self.text = ""
        self.visible = False
        
    def set_text(self, text):
        self.text = text
        self.visible = True
        
    def hide(self):
        self.visible = False
        
    def draw(self, vindu):
        if not self.visible:
            return
            
        # Tegn bakgrunn
        pg.draw.rect(vindu, (40, 40, 40), self.rect)
        pg.draw.rect(vindu, WHITE, self.rect, 2)
        
        # Tegn tekst med word wrap
        font = pg.font.Font(None, 24)
        words = self.text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= self.rect.width - 20:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Tegn hver linje
        y_offset = self.rect.y + 10
        for line in lines:
            text_surface = font.render(line, True, WHITE)
            vindu.blit(text_surface, (self.rect.x + 10, y_offset))
            y_offset += 30

class TimeSelector:
    def __init__(self, x, y, timestamps):
        self.x = x
        self.y = y
        self.timestamps = timestamps
        self.visible = False
        self.buttons = []
        self.selected_time = None
        
        button_width = 120
        button_height = 40
        buttons_per_row = 5
        x_spacing = 130
        y_spacing = 50
        
        for i, timestamp in enumerate(timestamps):
            row = i // buttons_per_row
            col = i % buttons_per_row
            button_x = self.x + (col * x_spacing)
            button_y = self.y + (row * y_spacing)
            self.buttons.append(Button(button_x, button_y, button_width, button_height, str(timestamp)))
    
    def show(self):
        self.visible = True
        self.selected_time = None
    
    def hide(self):
        self.visible = False
        self.selected_time = None
    
    def check_clicks(self, mouse_pos, mouse_pressed):
        if not self.visible:
            return None
        
        for i, button in enumerate(self.buttons):
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_pressed):
                self.selected_time = self.timestamps[i]
                return self.selected_time
        return None
    
    def draw(self, vindu):
        if not self.visible:
            return
        
        overlay = pg.Surface((VINDU_BREDDE, VINDU_HOYDE), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        vindu.blit(overlay, (0, 0))
        
        font = pg.font.Font(None, 36)
        title = font.render("Select a time:", True, WHITE)
        title_rect = title.get_rect(center=(VINDU_BREDDE // 2, self.y - 40))
        vindu.blit(title, title_rect)
        
        for button in self.buttons:
            button.draw(vindu)

class CharacterSelector:
    def __init__(self, x, y, suspects):
        self.x = x
        self.y = y
        self.suspects = list(suspects)
        self.visible = False
        self.selected_character = None
        
    def makeButtons(self, current_suspect):
        all_suspects = list(self.suspects)
        all_suspects.remove(current_suspect)


        button_width = 400
        button_height = 40
        y_spacing = 50

        for i, suspect in enumerate(all_suspects):
            button_x = self.x
            button_y = self.y + (i * y_spacing)
            self.buttons.append(Button(button_x, button_y, button_width, button_height, str(suspect), data=suspect))

    def show(self, current_suspect):
        self.visible = True
        self.buttons = []
        self.makeButtons(current_suspect)

    def hide(self):
        self.visible = False
        self.selected_character = None
    
    def check_clicks(self, mouse_pos, mouse_pressed):
        if not self.visible:
            return None
        
        for i, button in enumerate(self.buttons):
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_pressed):
                return self.buttons[i].data
        return None
    
    def draw(self, vindu):
        if not self.visible:
            return
        
        overlay = pg.Surface((VINDU_BREDDE, VINDU_HOYDE), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        vindu.blit(overlay, (0, 0))
        
        font = pg.font.Font(None, 36)
        title = font.render("Select a suspect:", True, WHITE)
        title_rect = title.get_rect(center=(VINDU_BREDDE // 2, self.y - 40))
        vindu.blit(title, title_rect)
        
        for button in self.buttons:
            button.draw(vindu)

class Character:
    def __init__(self, x, y, bredde=50, høyde=80):
        self.x = x
        self.y = y
        self.bredde = bredde
        self.høyde = høyde
        self.farge = (255, 0, 0)  # Rød
        self.outline_farge = (150, 0, 0)  # Mørk rød
        self.hastighet = 5

    def get_skjerm_pos(self, kamera_x, kamera_y):
        """Returnerer karakterens posisjon på skjermen"""
        return self.x - kamera_x, self.y - kamera_y

    def draw(self, vindu, kamera_x, kamera_y):
        """Tegner karakteren på skjermen"""
        skjerm_x, skjerm_y = self.get_skjerm_pos(kamera_x, kamera_y)

        # Tegn skygge
        skygge_offset = 3
        pg.draw.rect(vindu, (0, 0, 0, 100),
                     (skjerm_x - self.bredde // 2 + skygge_offset,
                     skjerm_y - self.høyde // 2 + skygge_offset,
                     self.bredde,
                     self.høyde))

        # Tegn hovedrektangel
        pg.draw.rect(vindu, self.farge,
                     (skjerm_x - self.bredde // 2,
                      skjerm_y - self.høyde // 2,
                      self.bredde,
                      self.høyde))

        # Tegn outline
        pg.draw.rect(vindu, self.outline_farge,
                     (skjerm_x - self.bredde // 2,
                      skjerm_y - self.høyde // 2,
                      self.bredde,
                      self.høyde), 3)

        # Tegn øyne
        øye_farge = (255, 255, 255)
        øye_størrelse = 8
        øye_y = skjerm_y - 15

        # Venstre øie
        pg.draw.circle(vindu, øye_farge,
                       (int(skjerm_x - 12), int(øye_y)), øye_størrelse)
        pg.draw.circle(vindu, (0, 0, 0),
                       (int(skjerm_x - 12), int(øye_y)), øye_størrelse // 2)

        # Høyre 
        pg.draw.circle(vindu, øye_farge,
                       (int(skjerm_x + 12), int(øye_y)), øye_størrelse)
        pg.draw.circle(vindu, (0, 0, 0),
                       (int(skjerm_x + 12), int(øye_y)), øye_størrelse // 2)
