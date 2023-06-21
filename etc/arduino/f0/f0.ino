/*  f0 script for composition 10.3

    - tested arduino model: arduino uno
    - use digital output pin 9 + ground & connect to amplifier
    - for a different model you can check output pin & support at https://github.com/sensorium/Mozzi#quick-start

 */

// general arduino
// #include <SD.h>
#include <SD.h>

// Mozzi stuff
#include <MozziGuts.h>
#include <Oscil.h>
#include <EventDelay.h>
#include <ADSR.h>
#include <tables/sin8192_int8.h>
#include <Line.h>
#include <mozzi_rand.h>

#define CONTROL_RATE 64

// f0 helper
#include "notes.h"

// SD card init
const int chipSelect = 10;


Oscil <8192, AUDIO_RATE> aOscil(SIN8192_DATA);
Oscil <8192, CONTROL_RATE> LFO(SIN8192_DATA);

Line <unsigned int> aGain;


// for triggering the envelope
EventDelay noteDelay;
EventDelay LFOFreqDelay;


ADSR <CONTROL_RATE, AUDIO_RATE> envelope;

boolean note_is_on = true;

// Global variables

File dataFile;

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
    dataFile = SD.open(F("s.f0"));
    startMozzi();

    noteDelay.set(2000); // 2 second countdown
        LFOFreqDelay.set(2000); // 2 second countdown


    LFO.setFreq(0.4f); 
}

struct NoteLike currentNote = makeRest(100);

void updateControl(){
    if (noteDelay.ready()) {
        getNextNote(&currentNote);
        Serial.print(F("current note: "));
        printNoteLike(&currentNote);
        // Rests are implicitly declared by 'isTone'
        if (isTone(&currentNote)) {
            playTone(&currentNote);
        }
        noteDelay.start(currentNote.duration);
    }   
    envelope.update();
    unsigned int gain = (128u+LFO.next())<<8;
    aGain.set(gain, AUDIO_RATE / CONTROL_RATE);

    // Adjust LFO freq for dynamic sound
    if (LFOFreqDelay.ready()) {
      float v = (rand(500) + 50) / 1000.0f;
      LFO.setFreq(v);
      LFOFreqDelay.start(1000 + rand(1000));
    }
}

String l_line;

void getNextNote(struct NoteLike *note) {
    if (dataFile) {
        if (dataFile.available() != 0) {
          l_line = dataFile.readStringUntil('\n');
          f0ToNoteLike(note, l_line.c_str());
          return;
        } else {
          dataFile.close();
          Serial.println(F("data file no longer available"));
        }
    } else {
      Serial.println(F("error opening s.f0 (couldn't be found)"));
   }
   stopMozzi();
}



// play a single tone
void playTone(struct NoteLike *currentNote) {
    byte attack_level = currentNote->velocity * 0.5;
    byte decay_level = currentNote->velocity;
    envelope.setLevels(attack_level, decay_level, decay_level, 1);

    unsigned int duration = (currentNote->duration);

    unsigned int attack_duration = duration * 0.2;
    unsigned int decay_duration = duration * 0.3;
    unsigned int sustain_duration = duration * 0.1;
    unsigned int release_duration = duration * 0.4;

    unsigned int summed_duration = attack_duration + decay_duration + sustain_duration + release_duration;
    unsigned int difference = duration - summed_duration;
    release_duration += difference;

    envelope.setTimes(attack_duration,decay_duration,sustain_duration,release_duration);
    envelope.noteOn();

    aOscil.setFreq(currentNote->frequency);  
}


AudioOutput_t updateAudio() {
    //return MonoOutput::from16Bit((int) (envelope.next() * aOscil.next()));
    // return MonoOutput::from16Bit((int) (aOscil.next()));
    long v = aOscil.next();
    return MonoOutput::from16Bit((int)(
      ((long)((long) v * (aGain.next())) >> 16) + (v * 0.5))     
      * envelope.next()); // shifted back to audio range after multiply
}


void loop() {
    audioHook(); // required here
}
