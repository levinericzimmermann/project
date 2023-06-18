/*  f0 script for composition 10.3

    - tested arduino model: arduino uno
    - use digital output pin 9 + ground & connect to amplifier
    - for a different model you can check output pin & support at https://github.com/sensorium/Mozzi#quick-start

 */

#include <MozziGuts.h>
#include <Oscil.h>
#include <EventDelay.h>
#include <ADSR.h>
#include <tables/sin8192_int8.h>

#include "notes.h"


Oscil <8192, AUDIO_RATE> aOscil(SIN8192_DATA);

// for triggering the envelope
EventDelay noteDelay;

ADSR <AUDIO_RATE, AUDIO_RATE> envelope;

boolean note_is_on = true;


unsigned int duration, attack_duration, decay_duration, sustain_duration, release_duration;
byte attack_level, decay_level;


// Global variables
struct NoteLike currentNote;

// This synthesizer plays a list of predefined notes.
// It does so by iterating over a string where those notes are defined.
// It puts each note into an array: noteArray.
// noteArray has a predefined maximum size.
// If our text file uses more notes than noteArray size, the program
// truncates the original data (and prints a warning).

int maxNoteCount = 20;
struct NoteLike noteArray[20];

char x[] = "26428.57,884.0,138\n2142.86,0,0\n83571.43,1473.33,138\n";

int noteCount;
int noteIndex = 0;


void setup(){
    Serial.begin(115200);
    noteDelay.set(2000); // 2 second countdown

    // We initialize the noteList in "setup" so
    noteCount = f0ToNoteLikeArr(x, noteArray);

    startMozzi();
}


void updateControl(){
    if (noteDelay.ready()) {
        currentNote = getNextNote();
        printNoteLike(currentNote);
        // Rests are implicitly declared by 'isTone'
        if (isTone(currentNote)) {
            playTone(currentNote);
        }
        noteDelay.start(duration);
        noteIndex += 1;
    }
}

struct NoteLike getNextNote() {
    if (noteIndex >= noteCount) {
        // List is empty, so make rest forever
        return makeRest(10000);
    }
    return noteArray[noteIndex];
}

// play a single tone
void playTone(struct NoteLike currentNote) {
    attack_level = currentNote.velocity;
    decay_level = currentNote.velocity;
    envelope.setADLevels(attack_level, decay_level);

    attack_duration = currentNote.duration * 0.25;
    decay_duration = currentNote.duration * 0.25;
    sustain_duration = currentNote.duration * 0.25;
    release_duration = currentNote.duration * 0.25;

    duration = currentNote.duration;

    envelope.setTimes(
        attack_duration,
        decay_duration,
        sustain_duration,
        release_duration
    );
    envelope.noteOn();

    aOscil.setFreq(currentNote.frequency);  
}


AudioOutput_t updateAudio(){
    envelope.update();
    return MonoOutput::from16Bit((int) (envelope.next() * aOscil.next()));
}


void loop(){
    audioHook(); // required here
}
