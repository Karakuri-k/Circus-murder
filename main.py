import pygame as pg
from constants import *
import os

pg.init()
vindu = pg.display.set_mode([VINDU_BREDDE, VINDU_HOYDE])
pg.display.set_caption("Murder Mystery")
clock = pg.time.Clock()

# Last inn og skaler bakgrunnsbildet
current_dir = os.path.dirname(__file__)
bildesti = os.path.join(current_dir, "photos/doors.png")
bakgrunn_original = pg.image.load(bildesti).convert()

# Strekk bildet mer i x-retningen (1.5x bredde) og zoom inn (1.3x totalt)
ny_bredde = int(VINDU_BREDDE * 2)
ny_hoyde = int(VINDU_HOYDE * 1.4)
bakgrunn = pg.transform.scale(bakgrunn_original, (ny_bredde, ny_hoyde))

# Kamera offset (startposisjon sentrert)
kamera_x = (ny_bredde - VINDU_BREDDE) // 2
kamera_y = (ny_hoyde - VINDU_HOYDE) // 2

# Variabler for smooth kamerabevegelse
mål_kamera_x = kamera_x
mål_kamera_y = kamera_y


class Door:
    def __init__(self, x, y, bredde, høyde, navn="Dør") -> None:
        self.x = x  # Verden-koordinater
        self.y = y
        self.bredde = bredde
        self.høyde = høyde
        self.navn = navn
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
        """Åpner/lukker døren og skifter farge"""
        self.er_åpnet = not self.er_åpnet
        status = "åpnet" if self.er_åpnet else "lukket"
        print(f"{self.navn} er nå {status}!")  # Debug melding

    def draw(self, vindu, kamera_x, kamera_y, vis_rektangler=True):
        """Tegner rektangelet på skjermen"""
        if not vis_rektangler:
            return

        skjerm_x = self.x - kamera_x
        skjerm_y = self.y - kamera_y

        # Velg farge basert på status
        if self.er_åpnet:
            farge = self.åpnet_farge
        elif self.is_aktiv:
            farge = self.aktiv_farge
        else:
            farge = self.farge

        # Lag en surface med alpha for transparency
        s = pg.Surface((self.bredde, self.høyde), pg.SRCALPHA)
        s.fill(farge)
        vindu.blit(s, (skjerm_x, skjerm_y))

        # Tegn border
        if self.er_åpnet:
            border_farge = (200, 0, 0)
            border_tykkelse = 4
        elif self.is_aktiv:
            border_farge = (255, 255, 255)
            border_tykkelse = 3
        else:
            border_farge = (0, 200, 0)
            border_tykkelse = 2
            
        pg.draw.rect(vindu, border_farge,
                     (skjerm_x, skjerm_y, self.bredde, self.høyde), border_tykkelse)

        # Tegn tekst og status
        if self.is_aktiv or self.er_åpnet:
            font = pg.font.Font(None, 28)
            
            # Dørnavn
            text = font.render(self.navn, True, (255, 255, 255))
            text_rect = text.get_rect(center=(skjerm_x + self.bredde // 2,
                                              skjerm_y - 30))
            vindu.blit(text, text_rect)
            
            # "Trykk E" eller "ÅPNET" tekst
            font_liten = pg.font.Font(None, 22)
            if self.er_åpnet:
                e_text = font_liten.render("ÅPNET", True, (255, 255, 255))
            else:
                e_text = font_liten.render("Trykk E", True, (255, 255, 255))
                
            e_rect = e_text.get_rect(center=(skjerm_x + self.bredde // 2,
                                             skjerm_y - 10))
            
            # Tegn bakgrunn bak teksten
            bg_rect = e_rect.inflate(10, 5)
            pg.draw.rect(vindu, (0, 0, 0, 180), bg_rect)
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


def main():
    global kamera_x, kamera_y, mål_kamera_x, mål_kamera_y
    running = True
    smooth_hastighet = 0.15  # For smooth kamerabevegelse
    vis_rektangler = True  # Toggle for å vise/skjule rektangler

    # Opprett noen eksempel-dører (juster posisjonene til ditt bilde)
    dører = [
        Door(100, 250, 225, 475, "Dør 1"),
        Door(395, 250, 225, 475, "Dør 2"),
        Door(690, 250, 225, 475, "Dør 3"),
        Door(985, 250, 225, 475, "Dør 4"),
        Door(1280, 250, 225, 475, "Dør 5"),
        Door(1575, 250, 225, 475, "Dør 6"),
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
                            dør.on_interact()
                            break

        # Håndter bevegelse med piltaster
        keys = pg.key.get_pressed()
        
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            # Flytt karakteren
            karakter.x -= karakter.hastighet
            # Begrens karakteren til verden
            karakter.x = max(karakter.bredde // 2, karakter.x)
            
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            # Flytt karakteren
            karakter.x += karakter.hastighet
            # Begrens karakteren til verden
            karakter.x = min(ny_bredde - karakter.bredde // 2, karakter.x)
        
        # Beregn hvor kameraet skal være for å holde karakteren sentrert
        ideell_kamera_x = karakter.x - VINDU_BREDDE // 2
        
        # Begrens kameraet til bildet
        begrenset_kamera_x = max(0, min(ideell_kamera_x, ny_bredde - VINDU_BREDDE))
        
        # Sjekk om kameraet er ved kanten
        kamera_ved_venstre_kant = (begrenset_kamera_x == 0)
        kamera_ved_høyre_kant = (begrenset_kamera_x == ny_bredde - VINDU_BREDDE)
        
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
        vindu.blit(bakgrunn, (-kamera_x, -kamera_y))

        # Sjekk om karakteren er nær noen dører og tegn dem
        for dør in dører:
            dør.check_karakter_nær(karakter.x, karakter.y)
            dør.draw(vindu, kamera_x, kamera_y, vis_rektangler)
        
        # Tegn karakteren
        karakter.draw(vindu, kamera_x, kamera_y)

        pg.display.flip()
        clock.tick(FPS)

    pg.quit()


if __name__ == "__main__":
    main()