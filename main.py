import pygame as pg
from constants import *
import os

pg.init()
vindu = pg.display.set_mode([VINDU_BREDDE, VINDU_HOYDE])
pg.display.set_caption("Murder Mystery")
clock = pg.time.Clock()

# Last inn og skaler bakgrunnsbildet
current_dir = os.path.dirname(__file__)


def load_and_scale_background(filename):
    """Last inn og skaler et bakgrunnsbilde"""
    bildesti = os.path.join(current_dir, filename)
    bakgrunn_original = pg.image.load(bildesti).convert()

    # Strekk bildet mer i x-retningen (1.5x bredde) og zoom inn (1.3x totalt)
    ny_bredde = int(VINDU_BREDDE * 2)
    ny_hoyde = int(VINDU_HOYDE * 1.4)
    return pg.transform.scale(bakgrunn_original, (ny_bredde, ny_hoyde))


def load_room_background(filename):
    bildesti = os.path.join(current_dir, filename)
    bilde = pg.image.load(bildesti).convert()
    return pg.transform.scale(bilde, (VINDU_BREDDE, VINDU_HOYDE))


# Last inn hovedbakgrunn
MAIN_BACKGROUND = "photos/doors.png"
bakgrunn = load_and_scale_background(MAIN_BACKGROUND)
ny_bredde = bakgrunn.get_width()
ny_hoyde = bakgrunn.get_height()

# Kamera offset (startposisjon sentrert)
kamera_x = (ny_bredde - VINDU_BREDDE) // 2
kamera_y = (ny_hoyde - VINDU_HOYDE) // 2

# Variabler for smooth kamerabevegelse
mål_kamera_x = kamera_x
mål_kamera_y = kamera_y


class Door:
    def __init__(self, x, y, bredde, høyde, navn="Dør", bakgrunn_fil=None) -> None:
        self.x = x  # Verden-koordinater
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

        # Tegn bare tekst når karakteren er nær eller døren er åpnet
        if self.is_aktiv or self.er_åpnet:
            font = pg.font.Font(None, 36)

            # "Trykk E for å åpne" eller "Trykk E for å lukke" tekst
            if self.er_åpnet:
                e_text = font.render("Trykk E for å lukke",
                                     True, (255, 255, 255))
            else:
                e_text = font.render("Trykk E for å åpne",
                                     True, (255, 255, 255))

            e_rect = e_text.get_rect(center=(skjerm_x + self.bredde // 2,
                                             skjerm_y + self.høyde // 2))

            # Tegn halvgjennomsiktig bakgrunn bak teksten
            bg_rect = e_rect.inflate(20, 10)
            s = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
            s.fill((0, 0, 0, 180))
            vindu.blit(s, bg_rect.topleft)

            # Tegn teksten
            vindu.blit(e_text, e_rect)


class Character:
    def __init__(self, x, y, bredde=50, høyde=80):
        self.x = x  # Verden-koordinater
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

        # Venstre øye
        pg.draw.circle(vindu, øye_farge,
                       (int(skjerm_x - 12), int(øye_y)), øye_størrelse)
        pg.draw.circle(vindu, (0, 0, 0),
                       (int(skjerm_x - 12), int(øye_y)), øye_størrelse // 2)

        # Høyre øye
        pg.draw.circle(vindu, øye_farge,
                       (int(skjerm_x + 12), int(øye_y)), øye_størrelse)
        pg.draw.circle(vindu, (0, 0, 0),
                       (int(skjerm_x + 12), int(øye_y)), øye_størrelse // 2)

def synk_kamera_med_karakter(karakter_x, verden_bredde):
    ideell_kamera_x = karakter_x - VINDU_BREDDE // 2
    return max(0, min(ideell_kamera_x, verden_bredde - VINDU_BREDDE))

def main():
    global kamera_x, kamera_y, mål_kamera_x, mål_kamera_y, bakgrunn, ny_bredde, ny_hoyde
    running = True
    smooth_hastighet = 0.15  # For smooth kamerabevegelse
    vis_rektangler = True  # Toggle for å vise/skjule rektangler
    current_background = MAIN_BACKGROUND  # Hold styr på gjeldende bakgrunn
    i_rom = False
    åpen_dør = None

    # Opprett noen eksempel-dører med forskjellige bakgrunner
    # Alle dører åpner samme rom-fil
    dører = [
        Door(100, 250, 225, 475, "Dør 1", "photos/room1.png"),
        Door(420, 250, 215, 475, "Dør 2", "photos/room.png"),
        Door(730, 250, 215, 475, "Dør 3", "photos/room.png"),
        Door(1020, 250, 215, 475, "Dør 4", "photos/room.png"),
        Door(1320, 250, 215, 475, "Dør 5", "photos/room.png"),
        Door(1620, 250, 215, 475, "Dør 6", "photos/room.png"),
    ]

    # Opprett karakter i midten av verden
    karakter = Character(ny_bredde // 2, VINDU_HOYDE - 150)

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_SPACE:
                    # Toggle visibility av rektangler med mellomrom
                    vis_rektangler = not vis_rektangler
                elif event.key == pg.K_e:
                    # Sjekk om karakteren er ved en dør
                    for dør in dører:
                        if dør.is_aktiv:
                            ny_bakgrunn_fil = dør.on_interact()

                            # Hvis døren åpnes (ny_bakgrunn_fil er ikke None), last inn rom
                            # Hvis døren lukkes (ny_bakgrunn_fil er None), gå tilbake til hovedbakgrunn
                            bakgrunn_fil_å_laste = ny_bakgrunn_fil if ny_bakgrunn_fil else MAIN_BACKGROUND
                            try:
                                if ny_bakgrunn_fil:
                                
                                # Åpner dør → LAST ROM
                                    bakgrunn = load_room_background(ny_bakgrunn_fil)

                                    ny_bredde = VINDU_BREDDE
                                    ny_hoyde = VINDU_HOYDE

                                    current_background = ny_bakgrunn_fil
                                    i_rom = True
                                    åpen_dør = dør
                                    kamera_x = 0
                                    kamera_y = 0
                                    mål_kamera_x = 0
                                    mål_kamera_y = 0

                                    print("Gikk inn i rom")

                                else:
                                    # Lukker dør → TILBAKE TIL HOVEDBAKGRUNN
                                    bakgrunn = load_and_scale_background(MAIN_BACKGROUND)
                                    ny_bredde = bakgrunn.get_width()
                                    ny_hoyde = bakgrunn.get_height()
                                    current_background = MAIN_BACKGROUND

                                    i_rom = False
                                    åpen_dør = None

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
                        
        # Håndter bevegelse med piltaster
        keys = pg.key.get_pressed()

        if not i_rom:
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                karakter.x -= karakter.hastighet
                karakter.x = max(karakter.bredde // 2, karakter.x)

            if keys[pg.K_RIGHT] or keys[pg.K_d]:
                karakter.x += karakter.hastighet
                karakter.x = min(ny_bredde - karakter.bredde // 2, karakter.x)


        # Beregn hvor kameraet skal være for å holde karakteren sentrert
        ideell_kamera_x = karakter.x - VINDU_BREDDE // 2

        # Begrens kameraet til bildet
        begrenset_kamera_x = max(
            0, min(ideell_kamera_x, ny_bredde - VINDU_BREDDE))

        # Sjekk om kameraet er ved kanten
        kamera_ved_venstre_kant = (begrenset_kamera_x == 0)
        kamera_ved_høyre_kant = (begrenset_kamera_x ==
                                 ny_bredde - VINDU_BREDDE)

        # Sjekk om karakteren er i midten av skjermen
        karakter_skjerm_x = karakter.x - kamera_x
        karakter_i_midten = abs(karakter_skjerm_x - VINDU_BREDDE // 2) < 10

        # Oppdater kameramål
        if kamera_ved_venstre_kant or kamera_ved_høyre_kant:
            # Kameraet er ved kanten
            if karakter_i_midten:
                # Karakteren er tilbake i midten, la kameraet følge igjen
                mål_kamera_x = begrenset_kamera_x
        else:
            # Kameraet er ikke ved kanten, følg alltid karakteren
            mål_kamera_x = begrenset_kamera_x

        # Begrens mål-kameraet
        mål_kamera_x = max(0, min(mål_kamera_x, ny_bredde - VINDU_BREDDE))
        mål_kamera_y = max(0, min(mål_kamera_y, ny_hoyde - VINDU_HOYDE))

        # Smooth kamerabevegelse mot målet
        kamera_x += (mål_kamera_x - kamera_x) * smooth_hastighet
        kamera_y += (mål_kamera_y - kamera_y) * smooth_hastighet

        # Tegn bakgrunnen med kamera-offset
        if i_rom:
            # I rommet, ingen kamera-offset
            vindu.blit(bakgrunn, (0, 0))
        else:
            # Ved dørene, bruk kamera-offset
            vindu.blit(bakgrunn, (-kamera_x, -kamera_y))

        # Sjekk om karakteren er nær noen dører og tegn dem
        for dør in dører:
            if not i_rom:
                dør.check_karakter_nær(karakter.x, karakter.y)
            dør.draw(vindu, kamera_x, kamera_y, vis_rektangler)

        if i_rom:
            pg.display.flip()
            clock.tick(FPS)
            continue

        # Tegn karakteren
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
