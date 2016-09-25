#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        miditest.py
# Purpose:     Unit testing harness for midiutil
#
# Author:      Mark Conway Wirt <emergentmusics) at (gmail . com>
#
# Created:     2008/04/17
# Copyright:   (c) 2009-2016, Mark Conway Wirt
# License:     Please see License.txt for the terms under which this
#              software is distributed.
#-----------------------------------------------------------------------------


from __future__ import division, print_function
import sys,  struct

import unittest
from midiutil.MidiFile import MIDIFile, writeVarLength,  \
    frequencyTransform,  returnFrequency, TICKSPERBEAT

class Decoder(object):
    '''
    An immutable comtainer for MIDI data. This is needed bcause if one indexes
    into a byte string in Python 3 one gets an ``int`` as a return.
    '''
    def __init__(self, data):
        self.data = data.decode("ISO-8859-1")
        
    def __len__(self):
        return len(self.data)
        
    def __getitem__(self, key):
        return self.data[key].encode("ISO-8859-1")
        
    def unpack_into_byte(self, key):
        return struct.unpack('>B', self[key])[0]

class TestMIDIUtils(unittest.TestCase):
    
    def testWriteVarLength(self):
        self.assertEqual(writeVarLength(0x70), [0x70])
        self.assertEqual(writeVarLength(0x80), [0x81, 0x00])
        self.assertEqual(writeVarLength(0x1FFFFF), [0xFF, 0xFF, 0x7F])
        self.assertEqual(writeVarLength(0x08000000), [0xC0, 0x80, 0x80, 0x00])
        
    def testAddNote(self):
        MyMIDI = MIDIFile(1)
        MyMIDI.addNote(0, 0, 100,0,1,100)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].type, "note")
        self.assertEqual(MyMIDI.tracks[0].eventList[0].pitch, 100)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].time, 0)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].duration, 1)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].volume, 100)
        
    def testShiftTrack(self):
        time = 1
        MyMIDI = MIDIFile(1)
        MyMIDI.addNote(0, 0, 100,time,1,100)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].type, "note")
        self.assertEqual(MyMIDI.tracks[0].eventList[0].pitch, 100)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].time, time)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].duration, 1)
        self.assertEqual(MyMIDI.tracks[0].eventList[0].volume, 100)
        MyMIDI.shiftTracks()
        self.assertEqual(MyMIDI.tracks[0].eventList[0].time, 0)

    def testDeinterleaveNotes(self):
        MyMIDI = MIDIFile(1)
        MyMIDI.addNote(0, 0, 100, 0, 2, 100)
        MyMIDI.addNote(0, 0, 100, 1, 2, 100)
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].time,  TICKSPERBEAT)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[2].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[2].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[3].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[3].time,  TICKSPERBEAT * 2)
        
    def testTimeShift(self):
        
        # With one track
        MyMIDI = MIDIFile(1)
        MyMIDI.addNote(0, 0, 100, 5, 1, 100)
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].time,  TICKSPERBEAT)
        
        # With two tracks
        MyMIDI = MIDIFile(2)
        MyMIDI.addNote(0, 0, 100, 5, 1, 100)
        MyMIDI.addNote(1, 0, 100, 6, 1, 100)
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].time,  TICKSPERBEAT)
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[0].time,  TICKSPERBEAT)
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[1].time,  TICKSPERBEAT)
        
        # Negative Time
        MyMIDI = MIDIFile(1)
        MyMIDI.addNote(0, 0, 100, -5, 1, 100)
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].time,  TICKSPERBEAT)
        
        # Negative time, two tracks
        
        MyMIDI = MIDIFile(2)
        MyMIDI.addNote(0, 0, 100, -1, 1, 100)
        MyMIDI.addNote(1, 0, 100, 0, 1, 100)
        MyMIDI.close()
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].time,  0)
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[1].time,  TICKSPERBEAT)
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[0].type, 'NoteOn')
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[0].time,  TICKSPERBEAT)
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[1].type, 'NoteOff')
        self.assertEqual(MyMIDI.tracks[1].MIDIEventList[1].time,  TICKSPERBEAT)
 
    def testFrequency(self):
        freq = frequencyTransform(8.1758)
        self.assertEqual(freq[0],  0x00)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x00)
        freq = frequencyTransform(8.66196) # 8.6620 in MIDI documentation
        self.assertEqual(freq[0],  0x01)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x00)
        freq = frequencyTransform(440.00)
        self.assertEqual(freq[0],  0x45)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x00)
        freq = frequencyTransform(440.0016)
        self.assertEqual(freq[0],  0x45)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x01)
        freq = frequencyTransform(439.9984)
        self.assertEqual(freq[0],  0x44)
        self.assertEqual(freq[1],  0x7f)
        self.assertEqual(freq[2],  0x7f)
        freq = frequencyTransform(8372.0190)
        self.assertEqual(freq[0],  0x78)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x00)
        freq = frequencyTransform(8372.062) #8372.0630 in MIDI documentation
        self.assertEqual(freq[0],  0x78)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x01)
        freq = frequencyTransform(13289.7300)
        self.assertEqual(freq[0],  0x7F)
        self.assertEqual(freq[1],  0x7F)
        self.assertEqual(freq[2],  0x7E)
        freq = frequencyTransform(12543.8760)
        self.assertEqual(freq[0],  0x7F)
        self.assertEqual(freq[1],  0x00)
        self.assertEqual(freq[2],  0x00)
        freq = frequencyTransform(8.2104) # Just plain wrong in documentation, as far as I can tell.
        #self.assertEqual(freq[0],  0x0)
        #self.assertEqual(freq[1],  0x0)
        #self.assertEqual(freq[2],  0x1)
        
        # Test the inverse
        testFreq = 15.0
        accuracy = 0.00001
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 200.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 400.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 440.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 1200.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 5000.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        testFreq = 12000.0
        x = returnFrequency(frequencyTransform(testFreq))
        delta = abs(testFreq - x)
        self.assertEqual(delta < (accuracy*testFreq), True)
        
    
    def testSysEx(self):
        #import pdb; pdb.set_trace()
        MyMIDI = MIDIFile(1)
        MyMIDI.addSysEx(0,0, 0, struct.pack('>B', 0x01))
        MyMIDI.close()
        
        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'SysEx')
        
        self.assertEqual(data.unpack_into_byte(0), 0x00)
        self.assertEqual(data.unpack_into_byte(1), 0xf0)
        self.assertEqual(data.unpack_into_byte(2), 3)
        self.assertEqual(data.unpack_into_byte(3), 0x00)
        self.assertEqual(data.unpack_into_byte(4), 0x01)
        self.assertEqual(data.unpack_into_byte(5), 0xf7)
        
    def testTempo(self):
        #import pdb; pdb.set_trace()
        tempo = 60
        MyMIDI = MIDIFile(1)
        MyMIDI.addTempo(0, 0, tempo)
        MyMIDI.close()
        
        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'Tempo')
        
        self.assertEqual(data.unpack_into_byte(0), 0x00) # time
        self.assertEqual(data.unpack_into_byte(1), 0xff) # Code
        self.assertEqual(data.unpack_into_byte(2), 0x51)
        self.assertEqual(data.unpack_into_byte(3), 0x03)
        self.assertEqual(data[4:7], struct.pack('>L', int(60000000/tempo))[1:4])
        
    def testTimeSignature(self):
        time = 0
        track = 0
        numerator = 4
        denominator = 2
        clocks_per_tick = 24
        MyMIDI = MIDIFile(1)
        MyMIDI.addTimeSignature(track, time, numerator, denominator, clocks_per_tick)
        MyMIDI.close()
        
        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'TimeSignature')
        
        self.assertEqual(data.unpack_into_byte(0), 0x00) # time
        self.assertEqual(data.unpack_into_byte(1), 0xFF) # Code
        self.assertEqual(data.unpack_into_byte(2), 0x58) # subcode
        self.assertEqual(data.unpack_into_byte(3), 0x04) # Data length
        self.assertEqual(data.unpack_into_byte(4), numerator)
        self.assertEqual(data.unpack_into_byte(5), denominator)
        self.assertEqual(data.unpack_into_byte(6), clocks_per_tick) # Data length
        self.assertEqual(data.unpack_into_byte(7), 0x08) # 32nd notes per quarter note
        
    def testProgramChange(self):
        #import pdb; pdb.set_trace()
        program = 10
        channel = 0
        MyMIDI = MIDIFile(1)
        MyMIDI.addProgramChange(0, channel, 0, program)
        MyMIDI.close()
        
        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'ProgramChange')
        self.assertEqual(data.unpack_into_byte(0), 0x00) # time
        self.assertEqual(data.unpack_into_byte(1), 0xC << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(2), program)
        
    def testTrackName(self):
        #import pdb; pdb.set_trace()
        track_name = "track"
        MyMIDI = MIDIFile(1)
        MyMIDI.addTrackName(0, 0, track_name)
        MyMIDI.close()

        data = Decoder(MyMIDI.tracks[0].MIDIdata)

        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'TrackName')
        
        self.assertEqual(data.unpack_into_byte(0), 0x00) # time
        self.assertEqual(data.unpack_into_byte(1), 0xFF) # Code
        self.assertEqual(data.unpack_into_byte(2), 0x03) # subcodes
        
    def testTuningBank(self):
        #import pdb; pdb.set_trace()
        bank = 1
        channel = 0
        MyMIDI = MIDIFile(1)
        MyMIDI.changeTuningBank(0, 0, 0, bank)
        MyMIDI.close()
        
        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'ControllerEvent')
        
        self.assertEqual(data.unpack_into_byte(0),  0x00)               # time
        self.assertEqual(data.unpack_into_byte(1),  0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(2),  0x65)               # Controller Number
        self.assertEqual(data.unpack_into_byte(3),  0x0)                # Controller Value
        self.assertEqual(data.unpack_into_byte(4),  0x00)               # time
        self.assertEqual(data.unpack_into_byte(5),  0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(6),  0x64)               # Controller Number
        self.assertEqual(data.unpack_into_byte(7),  0x4)                # Controller Value
        self.assertEqual(data.unpack_into_byte(8),  0x00)               # time
        self.assertEqual(data.unpack_into_byte(9),  0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(10), 0x06)               # Bank MSB
        self.assertEqual(data.unpack_into_byte(11), 0x00)               # Value
        self.assertEqual(data.unpack_into_byte(12), 0x00)               # time
        self.assertEqual(data.unpack_into_byte(13), 0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(14), 0x26)               # Bank LSB
        self.assertEqual(data.unpack_into_byte(15), bank)               # Bank value (bank number)
        
    def testTuningProgram(self):
        #import pdb; pdb.set_trace()
        program = 10
        channel = 0
        MyMIDI = MIDIFile(1)
        MyMIDI.changeTuningProgram(0, 0, 0, program)
        MyMIDI.close()

        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'ControllerEvent')
        
        self.assertEqual(data.unpack_into_byte(0), 0x00)               # time
        self.assertEqual(data.unpack_into_byte(1), 0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(2), 0x65)               # Controller Number
        self.assertEqual(data.unpack_into_byte(3), 0x0)                # Controller Value
        self.assertEqual(data.unpack_into_byte(4), 0x00)               # time
        self.assertEqual(data.unpack_into_byte(5), 0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(6), 0x64)               # Controller Number
        self.assertEqual(data.unpack_into_byte(7), 0x03)               # Controller Value
        self.assertEqual(data.unpack_into_byte(8), 0x00)               # time
        self.assertEqual(data.unpack_into_byte(9), 0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(10), 0x06)              # Bank MSB
        self.assertEqual(data.unpack_into_byte(11), 0x00)              # Value
        self.assertEqual(data.unpack_into_byte(12), 0x00)              # time
        self.assertEqual(data.unpack_into_byte(13), 0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(14), 0x26)               # Bank LSB
        self.assertEqual(data.unpack_into_byte(15), program)            # Bank value (bank number)
        
    def testNRPNCall(self):
        #import pdb; pdb.set_trace()
        track = 0
        time = 0
        channel = 0
        controller_msb = 1
        controller_lsb =  2
        data_msb = 3
        data_lsb = 4
        MyMIDI = MIDIFile(1)
        MyMIDI.makeNRPNCall(track, channel, time, controller_msb, controller_lsb, data_msb, data_lsb)
        MyMIDI.close()
        
        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'ControllerEvent')
        
        self.assertEqual(data.unpack_into_byte(0), 0x00)               # time
        self.assertEqual(data.unpack_into_byte(1), 0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(2), 99)                 # Controller Number
        self.assertEqual(data.unpack_into_byte(3), controller_msb)     # Controller Value
        self.assertEqual(data.unpack_into_byte(4), 0x00)               # time
        self.assertEqual(data.unpack_into_byte(5), 0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(6), 98)                 # Controller Number
        self.assertEqual(data.unpack_into_byte(7), controller_lsb)     # Controller Value
        self.assertEqual(data.unpack_into_byte(8), 0x00)               # time
        self.assertEqual(data.unpack_into_byte(9), 0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(10), 0x06)              # Bank MSB
        self.assertEqual(data.unpack_into_byte(11), data_msb)          # Value
        self.assertEqual(data.unpack_into_byte(12), 0x00)              # time
        self.assertEqual(data.unpack_into_byte(13), 0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(14), 0x26)               # Bank LSB
        self.assertEqual(data.unpack_into_byte(15), data_lsb) # Bank value (bank number)
        
    def testAddControllerEvent(self):
        #import pdb; pdb.set_trace()
        track = 0
        time = 0
        channel = 3
        controller_number = 1
        parameter =  2
        MyMIDI = MIDIFile(1)
        MyMIDI.addControllerEvent(track, channel, time, controller_number, parameter)
        MyMIDI.close()
        
        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'ControllerEvent')

        self.assertEqual(data.unpack_into_byte(0), 0x00) # time
        self.assertEqual(data.unpack_into_byte(1), 0xB << 4 | channel) # Code
        self.assertEqual(data.unpack_into_byte(2), controller_number) # Controller Number
        self.assertEqual(data.unpack_into_byte(3), parameter) # Controller Value
        
    def testNonRealTimeUniversalSysEx(self):
        code           = 1
        subcode        = 2
        payload_number = 42
        
        payload = struct.pack('>B', payload_number)

        MyMIDI = MIDIFile(1, adjust_origin=False)
        
        # Just for fun we'll use a multi-byte time
        time = 1
        time_bytes = writeVarLength(time*TICKSPERBEAT)
        MyMIDI.addUniversalSysEx(0, time, code, subcode, payload, realTime=False)
        MyMIDI.close()
        
        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'UniversalSysEx')
        
        self.assertEqual(data.unpack_into_byte(0), time_bytes[0]) # Time
        self.assertEqual(data.unpack_into_byte(1), time_bytes[1]) # Time
        self.assertEqual(data.unpack_into_byte(2), 0xf0) # UniversalSysEx == 0xF0
        self.assertEqual(data.unpack_into_byte(3), 5 + len(payload))    # Payload length = 5+actual pyayload
        self.assertEqual(data.unpack_into_byte(4), 0x7E) # 0x7E == non-realtime
        self.assertEqual(data.unpack_into_byte(5), 0x7F) # Sysex channel (always 0x7F)
        self.assertEqual(data.unpack_into_byte(6), code)
        self.assertEqual(data.unpack_into_byte(7), subcode)
        self.assertEqual(data.unpack_into_byte(8), payload_number) # Data
        self.assertEqual(data.unpack_into_byte(9), 0xf7) # End of message
        
    def testRealTimeUniversalSysEx(self):
        code           = 1
        subcode        = 2
        payload_number = 47
        
        payload = struct.pack('>B', payload_number)
        MyMIDI = MIDIFile(1)
        MyMIDI.addUniversalSysEx(0, 0, code, subcode, payload, realTime=True)
        MyMIDI.close()
        
        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'UniversalSysEx')
        
        self.assertEqual(data.unpack_into_byte(0), 0x00)
        self.assertEqual(data.unpack_into_byte(1), 0xf0)
        self.assertEqual(data.unpack_into_byte(2), 5 + len(payload))
        self.assertEqual(data.unpack_into_byte(3), 0x7F) # 0x7F == real-time
        self.assertEqual(data.unpack_into_byte(4), 0x7F)
        self.assertEqual(data.unpack_into_byte(5), code)
        self.assertEqual(data.unpack_into_byte(6), subcode)
        self.assertEqual(data.unpack_into_byte(7), payload_number)
        self.assertEqual(data.unpack_into_byte(8), 0xf7)
        
    def testTuning(self):
        MyMIDI = MIDIFile(1)
        MyMIDI.changeNoteTuning(0, [(1, 440), (2, 880)])
        MyMIDI.close()
        
        data = Decoder(MyMIDI.tracks[0].MIDIdata)
        
        self.assertEqual(MyMIDI.tracks[0].MIDIEventList[0].type, 'UniversalSysEx')
        
        self.assertEqual(data.unpack_into_byte(0), 0x00)
        self.assertEqual(data.unpack_into_byte(1), 0xf0)
        self.assertEqual(data.unpack_into_byte(2), 15)
        self.assertEqual(data.unpack_into_byte(3), 0x7F)
        self.assertEqual(data.unpack_into_byte(4), 0x7F)
        self.assertEqual(data.unpack_into_byte(5), 0x08)
        self.assertEqual(data.unpack_into_byte(6), 0x02)
        self.assertEqual(data.unpack_into_byte(7), 0x00)
        self.assertEqual(data.unpack_into_byte(8), 0x2)
        self.assertEqual(data.unpack_into_byte(9), 0x1)
        self.assertEqual(data.unpack_into_byte(10), 69)
        self.assertEqual(data.unpack_into_byte(11), 0)
        self.assertEqual(data.unpack_into_byte(12), 0)
        self.assertEqual(data.unpack_into_byte(13), 0x2)
        self.assertEqual(data.unpack_into_byte(14), 81)
        self.assertEqual(data.unpack_into_byte(15), 0)
        self.assertEqual(data.unpack_into_byte(16), 0)
        self.assertEqual(data.unpack_into_byte(17), 0xf7)
        
    def testWriteFile(self):
        # Just to make sure the stream can be written without throwing an error.
        MyMIDI = MIDIFile(1)
        MyMIDI.addNote(0, 0, 100,0,1,100)
        with open("/tmp/test.mid", "wb") as output_file:
            MyMIDI.writeFile(output_file)

def suite():
    MIDISuite = unittest.TestLoader().loadTestsFromTestCase(TestMIDIUtils)

    return MIDISuite

if __name__ == '__main__':
    print("Begining MIDIUtil Test Suite")
    MIDISuite = suite()
    unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(MIDISuite)

