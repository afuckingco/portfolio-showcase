#ifndef LYRICS_H
#define LYRICS_H

#define LYRICS_ENABLED 1

typedef struct {
    int   time_ms;
    char *text;
} LrcLine;

typedef struct {
    LrcLine *lines;
    int      count;
    int      offset_ms;
} Lyrics;

int  lyrics_load(Lyrics *ls, const char *lrc_path);
void lyrics_free(Lyrics *ls);

int  lyrics_index_at(const Lyrics *ls, int ms);

#endif
