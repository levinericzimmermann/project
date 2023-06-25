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
#include <tables/sin2048_int8.h>
#include <tables/brownnoise8192_int8.h>
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

Oscil <SIN2048_NUM_CELLS, AUDIO_RATE> aOscil(SIN2048_DATA);
Oscil <BROWNNOISE8192_NUM_CELLS, AUDIO_RATE> aNoise(BROWNNOISE8192_DATA);
Sample <BAMBOO_00_2048_NUM_CELLS, AUDIO_RATE> aSample(BAMBOO_00_2048_DATA);
Oscil <SIN2048_NUM_CELLS, CONTROL_RATE> LFO(SIN2048_DATA);

// LFO
Line <unsigned int> aGain;

// for triggering the envelope
EventDelay noteDelay;
EventDelay percussionDelay;
EventDelay LFOFreqDelay;

File noteFile, percussionFile;
float aSampleFreq   = ((float) BAMBOO_00_2048_SAMPLERATE / (float) BAMBOO_00_2048_NUM_CELLS);

// stop individual audio units for some time, if inactive,
// to save CPU
bool notePitch      = false;
bool noteNoise      = false;
bool percussion     = false;

// global stop variables: if error they are set to false
// & voice doesn't run anymore.
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

    aNoise.setFreq((float)AUDIO_RATE/BROWNNOISE8192_SAMPLERATE);
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
            } else {
                stopPitch();
                stopNoise();
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
                startPercussion();
                // 'frequency' is actually 'factor' here:
                // see mutwo/project_converters/f0.py: DataToPercussiveF0
                //   & project/render/f0.py:           METRONOME_PITCH_TUPLE
                aSample.setFreq(aSampleFreq * currentPercussion.frequency);
                aSample.start();
            }
            percussionDelay.start(currentPercussion.duration);
        } else {
            Serial.println(F("Stopped percussion due to error."));
            percussionOn = false;
            stopPercussion();
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

    // jump around in audio noise table to disrupt obvious looping
    aNoise.setPhase(rand((unsigned int)BROWNNOISE8192_NUM_CELLS));


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
        // Serial.println(F("start new note"));  // debug
        if (currentNote->frequency > 0) {
            startPitch();
            stopNoise();
        } else {
            stopPitch();
            startNoise();
        }
    }

    if (currentNote->state == STATE_NEW || currentNote->state == STATE_KEEP) {
        if (currentNote->frequency > 0) {
            aOscil.setFreq(currentNote->frequency);
        }
        target_gain = currentNote->velocity;

    } else if (currentNote->state == STATE_STOP) {
        // Serial.println(F("stop note"));  // debug
        target_gain = 0;
    } else {
        Serial.print(F("error: got unexpected state = "));
        Serial.print(currentNote->state);
        Serial.println(F("; note is ignored"));
    }
}

// start/stop function to avoid unnecessary
// audio calculations.
void startPitch() {
    notePitch = true;
}

void stopPitch() {
    notePitch = false;
}

void startNoise() {
    noteNoise = true;
}

void stopNoise() {
    noteNoise = false;
}

void startPercussion() {
    percussion = true;
}

void stopPercussion() {
    percussion = false;
}

AudioOutput_t updateAudio() {
    // note synthesis
    int noteSynthBase, noteSynth;
    //      cheap synthesis: only calculate oscillator if active
    if (noteNoise) {
        noteSynthBase           = aNoise.next() * 0.7f;
    } else if (notePitch) {
        long sine               = aOscil.next();
        noteSynthBase           = (int)(((long)((long) sine * (aGain.next())) >> 16) + (sine * 0.5f));
    }
    if (notePitch || noteNoise) {
        noteSynth               = noteSynthBase * aSmoothGain.next(target_gain);
    }

    // percussion synthesis
    int percussionSynth;
    if (percussion) {
        percussionSynth         = aSample.next() * 1000;
    } else {
        percussionSynth         = 0;
    }

    // combined & send to output
    return MonoOutput::from16Bit(percussionSynth + noteSynth);
}


void loop() {
    audioHook(); // required here
}
