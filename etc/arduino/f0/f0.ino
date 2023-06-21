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

#define CONTROL_RATE 64

// f0 helper
#include "notes.h"

// SD card init
const int chipSelect = 10;


Oscil <8192, AUDIO_RATE> aOscil(SIN8192_DATA);

// for triggering the envelope
EventDelay noteDelay;

ADSR <CONTROL_RATE, AUDIO_RATE> envelope;

boolean note_is_on = true;

// Global variables

File dataFile;

void setup(){
    Serial.begin(115200);
    noteDelay.set(2000); // 2 second countdown

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
}

String l_line;

void getNextNote(struct NoteLike *note) {
  Serial.println(F("getNextNote"));
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
    byte attack_level = currentNote->velocity - 1;
    byte decay_level = currentNote->velocity;
    envelope.setLevels(attack_level, decay_level, decay_level, 1);

    unsigned int duration = (currentNote->duration);

    unsigned int attack_duration = duration * 0.4;
    unsigned int decay_duration = duration * 0.1;
    unsigned int sustain_duration = duration * 0.1;
    unsigned int release_duration = duration * 0.4;

    envelope.setTimes(attack_duration,decay_duration,sustain_duration,release_duration);
    envelope.noteOn();

    aOscil.setFreq(currentNote->frequency);  
}


AudioOutput_t updateAudio() {
    return MonoOutput::from16Bit((int) (envelope.next() * aOscil.next()));
    // return MonoOutput::from16Bit((int) (aOscil.next()));
}


void loop() {
    audioHook(); // required here
}
