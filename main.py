# ESP32-S3 + 8 relay board - light show with 5 modes
# Press the BOOT button to switch modes.
from machine import Pin
import time, random

PINS = [4, 5, 6, 7, 15, 16, 17, 18]   # IN1..IN8 on the relay board
ACTIVE_LOW = True    # most relay boards turn ON when the pin is LOW
SPEED = 0.15         # seconds per step (keep >= 0.1, relays wear out)

OFF = 1 if ACTIVE_LOW else 0
relays = [Pin(p, Pin.OUT, value=OFF) for p in PINS]   # start all OFF
btn = Pin(0, Pin.IN, Pin.PULL_UP)                      # BOOT button


def show(mask):
    """Each bit = one relay. bit 0 = relay 1."""
    for i, r in enumerate(relays):
        on = (mask >> i) & 1
        r.value((not on) if ACTIVE_LOW else on)


def wait(t):
    """Sleep t seconds, return True if the button was pressed."""
    end = time.ticks_add(time.ticks_ms(), int(t * 1000))
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        if btn.value() == 0:
            while btn.value() == 0:
                time.sleep_ms(10)
            return True
        time.sleep_ms(10)
    return False


# ---------- patterns (each yields an 8-bit mask) ----------
def knight_rider():
    while True:
        for i in list(range(8)) + list(range(6, 0, -1)):
            yield 1 << i


def binary_counter():
    n = 0
    while True:
        yield n
        n = (n + 1) & 0xFF


def fill_drain():
    while True:
        for i in range(1, 9):
            yield (1 << i) - 1
        for i in range(7, -1, -1):
            yield (1 << i) - 1


def center_out():
    seq = [0x18, 0x24, 0x42, 0x81, 0x42, 0x24]
    while True:
        for m in seq:
            yield m


def sparkle():
    while True:
        yield random.getrandbits(8)


PATTERNS = [
    ("Knight Rider", knight_rider),
    ("Binary counter", binary_counter),
    ("Fill & drain", fill_drain),
    ("Center out", center_out),
    ("Sparkle", sparkle),
]

mode = 0
try:
    while True:
        name, pattern = PATTERNS[mode]
        print("Mode:", name)
        for mask in pattern():
            show(mask)
            if wait(SPEED):
                break
        mode = (mode + 1) % len(PATTERNS)
finally:
    show(0)   # all OFF if you stop the script
