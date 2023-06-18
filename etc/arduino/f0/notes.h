/* Declare NoteLike struct & related functions */

const char f0DelimiterItem = ',';
const char f0DelimiterEnd  = '\n';

struct NoteLike { 
    float duration;
    float frequency;
    unsigned int velocity;
};

// False if rest, True if Tone
bool isTone(struct NoteLike note) {
    if (note.frequency > 0 && note.velocity > 0) {
        return true;
    }
    return false;
}

// print note for easier debugging
void printNoteLike(struct NoteLike note) {
    if (isTone(note)) {
        Serial.print("T(f=");
        Serial.print(note.frequency);
        Serial.print("; d=");
        Serial.print(note.duration / 1000);
        Serial.print("; v=");
        Serial.print(note.velocity);
        Serial.println(")");
    } else {
        Serial.print("R(d=");
        Serial.print(note.duration / 1000);
        Serial.println(")"); 
    }
}

// Initializing tones & rests
struct NoteLike makeNote(float duration, float frequency, unsigned int velocity) {
    struct NoteLike note;
    note.duration = duration;
    note.frequency = frequency;
    note.velocity = velocity;
    return note;
}

struct NoteLike makeRest(float duration) {
    struct NoteLike note;
    note.duration = duration;
    note.frequency = 0;
    note.velocity = 0;
    return note;
}

// f0 notes have the form
//  duration,frequency,velocity
//  (e.g. char need to be split by ",")
struct NoteLike f0ToNoteLike (char f0[]) {
    float duration = 0;
    float frequency = 0;
    unsigned int velocity = 0;

    char *token, *str, *tofree;

    int i = 0;
    tofree = str = strdup(f0);
    while ((token = strsep(&str, ","))) {
        if (i == 0) {
            duration = atof(token);
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

    return makeNote(duration, frequency, velocity);
}



///////////////////////////////////////////////////
///////////////////////////////////////////////////

int f0ToNoteLikeArr (char f0[], struct NoteLike *buf) {
    char *token, *str, *tofree;

    // Serial.println(f0);

    int noteIndex;
    tofree = str = strdup(f0);
    while ((token = strsep(&str, "\n"))) {
        Serial.println(token);
        buf[noteIndex] = f0ToNoteLike(token);
        noteIndex += 1;
    }
    free(tofree);
    
    Serial.println("found n notes: ");
    Serial.println(noteIndex);
    return noteIndex;  // == noteCount
}
