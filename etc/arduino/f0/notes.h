/* Declare NoteLike struct & related functions */

const char f0DelimiterItem = ',';
const char f0DelimiterEnd  = '\n';

struct NoteLike { 
    unsigned int duration;
    float frequency;
    unsigned int velocity;
};

// False if rest, True if Tone
bool isTone(struct NoteLike *note) {
    if (note->frequency > 0 && note->velocity > 0) {
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
        Serial.print(note->duration / 1000);
        Serial.print(F("; v="));
        Serial.print(note->velocity);
        Serial.println(F(")"));
    } else {
        Serial.print(F("R(d="));
        Serial.print(note->duration / 1000);
        Serial.println(F(")")); 
    }
}

// Initializing tones & rests
struct NoteLike makeNote(unsigned int duration, float frequency, unsigned int velocity) {
    struct NoteLike note;
    note.duration = duration;
    note.frequency = frequency;
    note.velocity = velocity;
    return note;
}

struct NoteLike makeRest(unsigned int duration) {
    struct NoteLike note;
    note.duration = duration;
    note.frequency = 0;
    note.velocity = 0;
    return note;
}

// f0 notes have the form
//  duration,frequency,velocity
//  (e.g. char need to be split by ",")
void f0ToNoteLike (struct NoteLike *note, const char f0[]) {
    unsigned int duration = 0;
    float frequency = 0;
    unsigned int velocity = 0;

    char *token, *str, *tofree;

    int i = 0;
    tofree = str = strdup(f0);
    while ((token = strsep(&str, ","))) {
        if (i == 0) {
            duration = atoi(token);
        } else if (i == 1) {
            frequency = atof(token);
        } else if (i == 2) {
            velocity = atoi(token);
        } else {
            break;
        }
        i += 1;
    }
    free(tofree);

    note->duration = duration;
    note->frequency = frequency;
    note->velocity = velocity;

}
