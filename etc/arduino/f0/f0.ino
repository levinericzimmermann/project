/*  f0 script for composition 10.3

    - tested arduino model: arduino uno
    - use digital output pin 9 + ground & connect to amplifier
    - for a different model you can check output pin & support at https://github.com/sensorium/Mozzi#quick-start

    - the tone file on the sd card MUST be named        'n.f0'
    - the percussion file on the sd card MUST be named  'p.f0'
 */

// general arduino
#include <SD.h>

// Mozzi stuff
#include <MozziGuts.h>
#include <Oscil.h>
#include <EventDelay.h>
#include <Smooth.h>
#include <tables/sin8192_int8.h>
#include <Line.h>
#include <mozzi_rand.h>
#include <Sample.h>
#include <samples/bamboo/bamboo_00_2048_int8.h>

// f0 helper
#include "notes.h"

// SD card init
const int chipSelect = 10;

// Mozzi init
#define CONTROL_RATE 64

Smooth <long> aSmoothGain(0.9975f);

Oscil <8192, AUDIO_RATE> aOscil(SIN8192_DATA);
Sample <BAMBOO_00_2048_NUM_CELLS, AUDIO_RATE> aSample(BAMBOO_00_2048_DATA);
Oscil <8192, CONTROL_RATE> LFO(SIN8192_DATA);

// LFO
Line <unsigned int> aGain;

// for triggering the envelope
EventDelay noteDelay;
EventDelay percussionDelay;
EventDelay LFOFreqDelay;

File noteFile, percussionFile;
float aSampleFreq = ((float) BAMBOO_00_2048_SAMPLERATE / (float) BAMBOO_00_2048_NUM_CELLS);

bool noteOn         = true;
bool percussionOn   = true;

void setup(){
    Serial.begin(115200);

    if (!SD.begin(chipSelect)) {
        Serial.println(F("initialization failed. Things to check:"));
        Serial.println(F("1. is a card inserted?"));
        Serial.println(F("2. is your wiring correct?"));
        Serial.println(F("3. did you change the chipSelect pin to match your shield or module?"));
        Serial.println(F("Note: press reset or reopen this serial monitor after fixing your issue!"));
        while (1);
    }

    noteFile = SD.open(F("n.f0"));
    percussionFile = SD.open(F("p.f0"));

    Serial.println(F("\n\n=================\tSTART 10.3 SYNTHESIS\t=================\n"));

    startMozzi();

    percussionDelay.set(2000);
    noteDelay.set(2000);
    LFOFreqDelay.set(2000);

    LFO.setFreq(0.4f); 
}

struct NoteLike currentNote         = makeRest(100);
struct NoteLike currentPercussion   = makeRest(100);

long target_gain = 0;

void updateControl(){
    // Start note synthesis (continous sine tones)
    if (noteOn && noteDelay.ready()) {
        if (getNextNote(&currentNote, noteFile)) {
            Serial.print(F("note: "));
            printNoteLike(&currentNote);
            // Rests are implicitly declared by 'isTone'
            if (isTone(&currentNote)) {
                playTone(&currentNote);
            }
            noteDelay.start(currentNote.duration);
        } else {
            Serial.println(F("Stopped note due to error."));
            noteOn = false;
        }
    }   

    // Start percussion synthesis (short metronome-like attacks)
    if (percussionOn && percussionDelay.ready()) {
        if (getNextNote(&currentPercussion, percussionFile)) {
            Serial.print(F("perc:\t\t\t\t\t"));
            printNoteLike(&currentPercussion);
            if (isTone(&currentPercussion) && currentPercussion.state != STATE_KEEP) {
                aSample.setFreq(aSampleFreq);
                aSample.start();
            }
            percussionDelay.start(currentPercussion.duration);
        } else {
            Serial.println(F("Stopped percussion due to error."));
            percussionOn = false;
        }
    }

    // Some processing for sine tone synthesis, but on control
    // rate instead of audio rate.
    unsigned int gain = (128u + LFO.next()) << 8;
    aGain.set(gain, AUDIO_RATE / CONTROL_RATE);

    // Adjust LFO freq for dynamic sound
    if (LFOFreqDelay.ready()) {
        float v = (rand(500) + 50) / 1000.0f;
        LFO.setFreq(v);
        LFOFreqDelay.start(1000 + rand(1000));
    }

}

// Return next note from a dataFile.
// In case the file isn't available or already empty, the function returns false
// and prints a warning, but doesn't kill mozzi. In this way we can ensure the
// second -- maybe still functioning file/voice -- isn't interrupted due to a
// mistake in the other file.
bool getNextNote(struct NoteLike *note, File dataFile) {
    if (dataFile) {
        if (dataFile.available() != 0) {
            String l_line = dataFile.readStringUntil('\n');
            f0ToNoteLike(note, l_line.c_str());
            return true;
        } else {
            dataFile.close();
            Serial.println(F("error: data file no longer available"));
        }
    } else {
        Serial.println(F("error: opening data file (couldn't be found)"));
    }
    return false;
}


// play a single tone
void playTone(struct NoteLike *currentNote) {
    if (currentNote->state == STATE_NEW) {
        Serial.println(F("start new note"));
        target_gain = currentNote->velocity;
        aOscil.setFreq(currentNote->frequency);  
    } else if (currentNote->state == STATE_KEEP) {
        Serial.println(F("set new velocity"));
        target_gain = currentNote->velocity;
    } else if (currentNote->state == STATE_STOP) {
        Serial.println(F("stop note"));
        target_gain = 0;
    } else {
        Serial.print(F("error: got unexpected state = "));
        Serial.print(currentNote->state);
        Serial.println(F(""));
    }
}


AudioOutput_t updateAudio() {
    // note synthesis
    long sine               = aOscil.next();
    int modulatedSine       = (int)(((long)((long) sine * (aGain.next())) >> 16) + (sine * 0.5));
    int noteSynth           = modulatedSine* aSmoothGain.next(target_gain);

    // percussion synthesis
    int percussionSynth     = aSample.next() * 1000;

    // combined & send to output
    return MonoOutput::from16Bit(percussionSynth + noteSynth);
}


void loop() {
    audioHook(); // required here
}
