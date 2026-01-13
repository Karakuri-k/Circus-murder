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
ny_bredde = int(VINDU_BREDDE * 1.5 * 1.3)
ny_hoyde = int(VINDU_HOYDE * 1.3)
bakgrunn = pg.transform.scale(bakgrunn_original, (ny_bredde, ny_hoyde))

# Kamera offset (startposisjon sentrert)
kamera_x = (ny_bredde - VINDU_BREDDE) // 2
kamera_y = (ny_hoyde - VINDU_HOYDE) // 2

class Doors:
    def __init__(self, x, y, bredde, høyde) -> None:
        self.x = x
        self.y = y
        self.bredde = bredde
        self.høyde = høyde

    #def draw(self, vindu):
    #    pg.draw.rect(vindu, RED, self.bredde, self.høyde, (self.x, self.y))


def main():
    global kamera_x, kamera_y
    running = True
    kamera_hastighet = 10

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

        # Håndter piltaster for kamerabevegelse
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            kamera_x -= kamera_hastighet
        if keys[pg.K_RIGHT]:
            kamera_x += kamera_hastighet
        if keys[pg.K_UP]:
            kamera_y -= kamera_hastighet
        if keys[pg.K_DOWN]:
            kamera_y += kamera_hastighet

        # Begrens kameraet til bakgrunnsbildets grenser
        kamera_x = max(0, min(kamera_x, ny_bredde - VINDU_BREDDE))
        kamera_y = max(0, min(kamera_y, ny_hoyde - VINDU_HOYDE))

        # Tegn bakgrunnen med kamera-offset
        vindu.blit(bakgrunn, (-kamera_x, -kamera_y))

        # Eksempel: Tegn et objekt på en fast posisjon i verden
        objekt_verden_x = 400
        objekt_verden_y = 300
        objekt_skjerm_x = objekt_verden_x - kamera_x
        objekt_skjerm_y = objekt_verden_y - kamera_y
        pg.draw.circle(vindu, (255, 0, 0),
                       (objekt_skjerm_x, objekt_skjerm_y), 20)

        pg.display.flip()
        clock.tick(FPS)

    pg.quit()


if __name__ == "__main__":
    main()
