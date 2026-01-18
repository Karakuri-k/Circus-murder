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
print(f"the characters are: {b.characters}")
print(f"the murderer is: {b.murderer}")
print(f"the victim is: {b.victim}")

pprint(f"the locations are {b.locations}")
print(f"the crime scene is: {b.crimeScene}")
print(f"the time of death is: {b.murderTime}")

print("the murderer's schedule is: ")
pprint(b.murderer.alibiSchedule)

print("the victim's schedule is:")
pprint(b.victim.alibiSchedule)
print(b.murderer.timeToLie)

print(b.murderer.whereWereYou("14:00", b))
print(b.murderer.haveYouSeen(b.victim, b))
print(b.characters[0].haveMotive(b.characters[2], b))