from classes import *
import pygame as pg
from constants import *
import os
import random as rd

pg.init()
vindu = pg.display.set_mode([VINDU_BREDDE, VINDU_HOYDE])
pg.display.set_caption("Murder Mystery")
clock = pg.time.Clock()


current_dir = os.path.dirname(__file__)


def load_and_scale_background(filename):
    """Last inn og skaler et bakgrunnsbilde"""
    bildesti = os.path.join(current_dir, filename)
    bakgrunn_original = pg.image.load(bildesti).convert()

    ny_bredde = int(VINDU_BREDDE * 2)
    ny_hoyde = int(VINDU_HOYDE * 1.4)
    return pg.transform.scale(bakgrunn_original, (ny_bredde, ny_hoyde))


def load_room_background(filename):
    bildesti = os.path.join(current_dir, filename)
    bilde = pg.image.load(bildesti).convert()
    return pg.transform.scale(bilde, (VINDU_BREDDE, VINDU_HOYDE))


MAIN_BACKGROUND = "photos/doors.png"
bakgrunn = load_and_scale_background(MAIN_BACKGROUND)
ny_bredde = bakgrunn.get_width()
ny_hoyde = bakgrunn.get_height()

kamera_x = (ny_bredde - VINDU_BREDDE) // 2
kamera_y = (ny_hoyde - VINDU_HOYDE) // 2

mål_kamera_x = kamera_x
mål_kamera_y = kamera_y



def synk_kamera_med_karakter(karakter_x, verden_bredde):
    ideell_kamera_x = karakter_x - VINDU_BREDDE // 2
    return max(0, min(ideell_kamera_x, verden_bredde - VINDU_BREDDE))

seenClicked = False
def main():
    global kamera_x, kamera_y, mål_kamera_x, mål_kamera_y, bakgrunn, ny_bredde, ny_hoyde

    evening = Evening()
    print(f"the characters are: {evening.characters}")
    print(f"the murderer is: {evening.murderer}")
    print(f"the victim is: {evening.victim}")
    print(f"the time of death is: {evening.murderTime}")
    print(f"the time to lie is: {evening.murderer.timeToLie}")


    running = True
    smooth_hastighet = 0.15  
    vis_rektangler = True  
    current_background = MAIN_BACKGROUND  
    i_rom = False
    åpen_dør = None
    current_suspect = None

    button_y_start = 400
    button_spacing = 70
    button_bredde = 300
    button_høyde = 50
    button_x = (VINDU_BREDDE - button_bredde) // 2

    whereWereYou_button = Button(button_x, button_y_start, button_bredde, button_høyde, 
                                  "Where were you at...?")
    haveYouSeen_button = Button(button_x, button_y_start + button_spacing, button_bredde, button_høyde,
                                 "Have you seen...?")
    haveMotive_button = Button(button_x, button_y_start + button_spacing * 2, button_bredde, button_høyde,
                               "How was ...'s relationship with the victim?")
    
    dialog_box = DialogBox(50, 50, VINDU_BREDDE - 100, 150)
    time_selector = TimeSelector(100, 150, evening.timestamps)
    character_selector = CharacterSelector(100, 150, evening.suspects)



    dører = [
        Door(100, 250, 225, 475, "Dør 1", "photos/room1.png", evening.suspects[0]),
        Door(420, 250, 215, 475, "Dør 2", "photos/room.png", evening.suspects[1]),
        Door(730, 250, 215, 475, "Dør 3", "photos/room.png", evening.suspects[2]),
        Door(1020, 250, 215, 475, "Dør 4", "photos/room.png", evening.suspects[3]),
        Door(1320, 250, 215, 475, "Dør 5", "photos/room.png", evening.suspects[4]),
        Door(1620, 250, 215, 475, "Dør 6", "photos/room.png", evening.suspects[5]),
    ]

  
    karakter = Character(ny_bredde // 2, VINDU_HOYDE - 150)

    seenClicked = False
    while running:
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if time_selector.visible:
                        time_selector.hide()
                    elif character_selector.visible:
                        character_selector.hide()
                    else:
                        running = False
                elif event.key == pg.K_SPACE:
               
                    vis_rektangler = not vis_rektangler
                elif event.key == pg.K_e:
                    for dør in dører:
                        if dør.is_aktiv:
                            ny_bakgrunn_fil = dør.on_interact()
                            bakgrunn_fil_å_laste = ny_bakgrunn_fil if ny_bakgrunn_fil else MAIN_BACKGROUND
                            try:
                                if ny_bakgrunn_fil:
                                
                                    bakgrunn = load_room_background(ny_bakgrunn_fil)

                                    ny_bredde = VINDU_BREDDE
                                    ny_hoyde = VINDU_HOYDE
                                    current_background = ny_bakgrunn_fil

                                    current_suspect = SuspectSprite(
                                        VINDU_BREDDE // 2, 
                                        VINDU_HOYDE // 2, 
                                        dør.suspect # type: ignore
                                    )

                                    i_rom = True
                                    åpen_dør = dør
                                    dialog_box.hide()
                                    time_selector.hide()
                                    character_selector.hide()
                                    kamera_x = 0
                                    kamera_y = 0
                                    mål_kamera_x = 0
                                    mål_kamera_y = 0

                                    print("Gikk inn i rom")

                                else:
                                    bakgrunn = load_and_scale_background(MAIN_BACKGROUND)
                                    ny_bredde = bakgrunn.get_width()
                                    ny_hoyde = bakgrunn.get_height()
                                    current_background = MAIN_BACKGROUND

                                    current_suspect = None 
                                    i_rom = False
                                    åpen_dør = None
                                    dialog_box.hide()
                                    time_selector.hide()
                                    character_selector.hide()

                                    kamera_x = synk_kamera_med_karakter(karakter.x, ny_bredde)
                                    mål_kamera_x = kamera_x
                                    kamera_y = (ny_hoyde - VINDU_HOYDE) // 2
                                    mål_kamera_y = kamera_y

                                    print("Tilbake til hovedområdet")


                            except Exception as e:
                                print(f"Kunne ikke laste bakgrunn: {e}")

                                print(
                                    f"Kunne ikke laste bakgrunn {bakgrunn_fil_å_laste}: {e}")
                            break
                        
        keys = pg.key.get_pressed()


        if i_rom and current_suspect:
            if time_selector.visible:
                selected_time = time_selector.check_clicks(mouse_pos, mouse_pressed)
                if selected_time:
                    response = current_suspect.person.whereWereYou(selected_time, evening)
                    dialog_box.set_text(response)
                    time_selector.hide()

            elif character_selector.visible:
                selected_character = character_selector.check_clicks(mouse_pos, mouse_pressed)
                if selected_character:
                    if seenClicked:
                        response = current_suspect.person.haveYouSeen(selected_character, evening)
                        seenClicked = False
                    else:
                        response = current_suspect.person.haveMotive(selected_character, evening)
                    dialog_box.set_text(response)
                    character_selector.buttons = []
                    character_selector.hide()
                    
            else: 
                whereWereYou_button.check_hover(mouse_pos)
                haveYouSeen_button.check_hover(mouse_pos)
                haveMotive_button.check_hover(mouse_pos)

                if whereWereYou_button.is_clicked(mouse_pos, mouse_pressed):
                    time_selector.show()

                if haveYouSeen_button.is_clicked(mouse_pos, mouse_pressed):
                    seenClicked = True
                    character_selector.show(current_suspect.person)

                if haveMotive_button.is_clicked(mouse_pos, mouse_pressed):
                    seenClicked = False
                    character_selector.show(current_suspect.person)
            
        if not i_rom:
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                karakter.x -= karakter.hastighet
                karakter.x = max(karakter.bredde // 2, karakter.x)

            if keys[pg.K_RIGHT] or keys[pg.K_d]:
                karakter.x += karakter.hastighet
                karakter.x = min(ny_bredde - karakter.bredde // 2, karakter.x)


        ideell_kamera_x = karakter.x - VINDU_BREDDE // 2

        begrenset_kamera_x = max(
            0, min(ideell_kamera_x, ny_bredde - VINDU_BREDDE))

        kamera_ved_venstre_kant = (begrenset_kamera_x == 0)
        kamera_ved_høyre_kant = (begrenset_kamera_x ==
                                 ny_bredde - VINDU_BREDDE)

        karakter_skjerm_x = karakter.x - kamera_x
        karakter_i_midten = abs(karakter_skjerm_x - VINDU_BREDDE // 2) < 10

        if kamera_ved_venstre_kant or kamera_ved_høyre_kant:
            if karakter_i_midten:
                mål_kamera_x = begrenset_kamera_x
        else:
            mål_kamera_x = begrenset_kamera_x

        mål_kamera_x = max(0, min(mål_kamera_x, ny_bredde - VINDU_BREDDE))
        mål_kamera_y = max(0, min(mål_kamera_y, ny_hoyde - VINDU_HOYDE))

        kamera_x += (mål_kamera_x - kamera_x) * smooth_hastighet
        kamera_y += (mål_kamera_y - kamera_y) * smooth_hastighet

        if i_rom:
            vindu.blit(bakgrunn, (0, 0))

        else:
            vindu.blit(bakgrunn, (-kamera_x, -kamera_y))

        for dør in dører:
            if not i_rom:
                dør.check_karakter_nær(karakter.x, karakter.y)
            dør.draw(vindu, kamera_x, kamera_y, vis_rektangler)

        if i_rom:
            if current_suspect:
                current_suspect.draw(vindu)

            if not time_selector.visible and not character_selector.visible:
                whereWereYou_button.draw(vindu)
                haveYouSeen_button.draw(vindu)
                haveMotive_button.draw(vindu)

            dialog_box.draw(vindu)
            time_selector.draw(vindu)
            character_selector.draw(vindu)

            pg.display.flip()
            clock.tick(FPS)
            continue

        if i_rom:
            
            vindu.blit(bakgrunn, (0, 0))

        else:
            vindu.blit(bakgrunn, (-kamera_x, -kamera_y))

            for dør in dører:
                dør.check_karakter_nær(karakter.x, karakter.y)
                dør.draw(vindu, kamera_x, kamera_y, vis_rektangler)

            karakter.draw(vindu, kamera_x, kamera_y)


        pg.display.flip()
        clock.tick(FPS)

    pg.quit()


if __name__ == "__main__":
    main()
