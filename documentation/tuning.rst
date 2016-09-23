Tuning and Micro-tonalities
===========================

.. currentmodule:: midiutil.MidiFile

One of my interests is microtonalities/non-standard tunings, so support
for such explorations has been included in the library.

There are several ways that tuning data can be specified in the MIDI standard,
two of the most common being note pitch-bend and bulk tuning dumps. In this
library I have implemented the real-time change note tuning of the MIDI
tuning standard. I chose that as a first implementation because most of the
soft-synthesizers I use support this standard.

Note, however, that implementation of the MIDI tuning standard is somewhat spotty,
so you may want to verify that your hardware and/or software supports it before
you spend too much time.

The main function to support a tuning change is ``changeNoteTuning``.

.. automethod:: MIDIFile.changeNoteTuning

With some instruments, such as `timidity <http://timidity.sourceforge.net/>`_, this
is all you need to do: timidity will apply the tuning change to the notes.
Other instruments, such as `fluidsynth <http://www.fluidsynth.org/>`_, require
that the tuning program be explicitly assigned. This is done with the
``changeTuningProgram`` function:

.. automethod:: MIDIFile.changeTuningProgram

The tuning bank can also be specified (fluidsynth assumes that any tuning
you transmit via ``changeNoteTuning`` is assigned to bank one):

.. automethod:: MIDIFile.changeTuningBank

So, as a complete example, the following code fragment would get rid of that
pesky 440 Hz A and tell the instrument to use the tuning that you just
transmitted:

.. code:: python

  track   = 0
  channel = 0
  tuning  = [(69, 500)]
  program = 0
  bank    = 0
  time    = 0
  MyMIDI.changeNoteTuning(track, tuning, tuningProgam=program)
  MyMIDI.changeTuningBank(track, channel, time, bank) # may or may not be needed
  MyMIDI.changeTuningProgram(track, channel, time, program) # ditto


  