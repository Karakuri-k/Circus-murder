from lists import *
from classes import *
from pprint import pprint
import pygame as pg
from constants import *

#Når spillet starter:
#Opprette så så mange spillere
#Etablere et offer
#Etablere en morder
#hvor var du at time
#har du sett suspect
#hva vet du om suspect (motiv)





b = Evening()
print(b.start)
print(b.end)
print(b.timestamps)
print(b.characters)

pprint(b.characters[0].alibiSchedule)
print(b.locations)
print(b.murderer)
print(b.crimeScene)
print(b.murderTime)
print(b.murderer.alibiSchedule)

