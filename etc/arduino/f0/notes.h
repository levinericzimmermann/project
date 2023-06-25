/* Declare NoteLike struct & related functions */

const char f0DelimiterItem  = ',';
const char f0DelimiterEnd   = '\n';

const int STATE_NEW         = 0;
const int STATE_KEEP        = 1;
const int STATE_STOP        = 2;

struct NoteLike { 
    int state;
    unsigned int duration;
    float frequency;
    unsigned int velocity;
};

// False if rest, True if Tone
bool isTone(struct NoteLike *note) {
    if (note->frequency != 0 && note->velocity > 0) {
        return true;
    }
    return false;
}

// print note for easier debugging
void printNoteLike(struct NoteLike *note) {
    if (isTone(note)) {
        Serial.print(F("T(f="));
        Serial.print(note->frequency);
        Serial.print(F("; d="));
        Serial.print(note->duration / 1000.0f);
        Serial.print(F("; v="));
        Serial.print(note->velocity);
        Serial.print(F("; s="));
        Serial.print(note->state);
        Serial.println(F(")"));
    } else {
        Serial.print(F("R(d="));
        Serial.print(note->duration / 1000);
        Serial.print(F("; s="));
        Serial.print(note->state);
        Serial.println(F(")")); 
    }
}

// Initializing tones & rests
struct NoteLike makeNote(unsigned int duration, float frequency, unsigned int velocity) {
    struct NoteLike note;
    note.state      = STATE_NEW;
    note.duration   = duration;
    note.frequency  = frequency;
    note.velocity   = velocity;
    return note;
}

struct NoteLike makeRest(unsigned int duration) {
    struct NoteLike note;
    note.state      = STATE_NEW;
    note.duration   = duration;
    note.frequency  = 0;
    note.velocity   = 0;
    return note;
}

// f0 notes have the form
//  state,duration,frequency,velocity
//  (e.g. char need to be split by ",")
//
//  state can be
//      n   =   new note
//      k   =   keep
//      s   =   stop
void f0ToNoteLike (struct NoteLike *note, const char f0[]) {
    int state               = STATE_NEW;
    unsigned int duration   = 0;
    float frequency         = 0;
    unsigned int velocity   = 0;

    char *token, *str, *tofree;

    int i = 0;
    tofree = str = strdup(f0);
    while ((token = strsep(&str, ","))) {
        if (i == 0) {
            state = atoi(token);
        } else if (i == 1) {
            duration = atoi(token);
        } else if (i == 2) {
            frequency = atof(token);
        } else if (i == 3) {
            velocity = atoi(token);
        } else {
            break;
        }
        i += 1;
    }

    free(tofree);

    note->state     = state;
    note->duration  = duration;
    note->frequency = frequency;
    note->velocity  = velocity;
}
