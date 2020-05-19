#!/usr/bin/env python3

import sys, pygame, pygame.midi

import smbus
import errno

from pychord import *

from audiolazy import *

def num_devices(bus):
    addresses = []
    for device in range(3, 128):
        try:
            bus.write_byte(device, 0)
            addresses.append(device)
        except IOError as e:
            if e.errno != errno.EREMOTEIO:
                print("Error: {0} on address {1}".format(e, hex(device)))
        except Exception as e: # exception if read_byte fails
            print("Error unk: {0} on address {1}".format(e, hex(device)))
    return addresses

class Note:
    def __init__(self, name, velocity):
        self.name = name
        self.velocity = velocity

    def __repr__(self):
        return str(self.name) + " " + str(self.velocity)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other.name == self.name

if __name__ == "__main__":
    bus_number = 1
    bus = smbus.SMBus(bus_number)
    device_count = 0

    addresses = num_devices(bus)
    if len(addresses) == 0:
        print("humanophone slaves not found!")
        exit(0)

    pygame.init()
    pygame.midi.init()

    # list all midi devices
    for x in range(0, pygame.midi.get_count()):
        print(pygame.midi.get_device_info(x))

    # open a specific midi device
    inp = pygame.midi.Input(3)

    input_notes = set()
    playing_notes = set()

    while True:
        if inp.poll():
            events = inp.read(1000)
            for event in events:
                note_name = midi2str(event[0][1], False)
                on_event = False;
                if event[0][0] == 144:
                    on_event = True
                elif event[0][0] == 128:
                    on_event = False
                else:
                    continue
                print(on_event)
                velocity = event[0][2]
                note = Note(note_name, velocity)
                if on_event:
                    input_notes.add(note)
                    freq = str2freq(note.name)
                    print(freq)
                    bus.write_word_data(0x20, 0x55, int(freq))
                    bus.write_byte(0x20, 0x35)
                else:
                    input_notes.discard(note)
                    bus.write_byte(0x20, 0x33)
                print(input_notes)

        pygame.time.wait(10)

