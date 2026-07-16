#ifndef APP_H
#define APP_H

#include "library.h"
#include "gfx.h"
#include "theme.h"
#include "lyrics.h"

#define COVER_TEX (7 * GRID)
#define REC_ART   72

typedef enum { SCREEN_LIBRARY = 0, SCREEN_RECORD, SCREEN_NOWPLAYING } Screen;
typedef enum { MODE_ALBUMS = 0, MODE_PLAYLISTS } LibMode;

typedef struct {
    Library lib;
    Screen  screen;
    LibMode mode;

    int       lib_sel;
    int       lib_top;
    Texture  *preview_tex;
    int       preview_for;
    int       preview_mode;

    Record   *rec;
    int       rec_sel;
    int       rec_top;
    Texture  *rec_tex;
    Texture  *rec_thumb_tex;

    int       np_index;
    float     np_anim;
    int       scrub_dir;
    float     scrub_ms;
    float     scrub_seek_t;
    float     l_replay_t;

    int       shuffle;
    int       queue_index;   /* -1 = empty; else track index in g_app.rec */

#if LYRICS_ENABLED

    Lyrics    lyrics;
    int       lyrics_view;
    float     lyrics_anim;
#endif

    int       settings_open;
    float     settings_anim;
    int       settings_sel;

    int       controls_open;
    float     controls_anim;

    float        time;
    unsigned int btn_prev;
} App;

extern App g_app;

extern unsigned int g_pressed;
extern unsigned int g_held;
#define PRESSED(b) ((g_pressed & (b)) != 0)
#define HELD(b)    ((g_held & (b)) != 0)

void scr_library(void);
void scr_record(void);
void scr_nowplaying(void);

Record *lib_current_list(int *count);
void    update_preview(void);
void    open_record(int index);
void    go_library(void);
void    start_play(int index, int go_nowplaying, int animate);
int     next_track_index(int cur);
void    handle_auto_advance(void);
void    fmt_time(char *buf, int sz, int seconds);
unsigned int str_hash(const char *s);

#endif
