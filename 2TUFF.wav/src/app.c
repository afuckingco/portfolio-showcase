#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "app.h"
#include "image.h"
#include "id3.h"
#include "audio.h"

App g_app;
unsigned int g_pressed = 0;
unsigned int g_held = 0;

unsigned int str_hash(const char *s)
{
    unsigned int h = 2166136261u;
    while (*s) { h ^= (unsigned char)*s++; h *= 16777619u; }
    return h;
}

void fmt_time(char *buf, int sz, int seconds)
{
    if (seconds < 0) seconds = 0;
    snprintf(buf, sz, "%d:%02d", seconds / 60, seconds % 60);
}

Record *lib_current_list(int *count)
{
    if (g_app.mode == MODE_ALBUMS) {
        if (count) *count = g_app.lib.album_count;
        return g_app.lib.albums;
    }
    if (count) *count = g_app.lib.playlist_count;
    return g_app.lib.playlists;
}

static Texture *load_cover_for_record(Record *r, int size)
{
    Texture *t = NULL;

    if (r->cover_path[0])
        t = image_load_jpeg_file(r->cover_path, size);

    if (!t && r->track_count > 0) {
        ID3Tag tag;
        if (id3_read(r->tracks[0].path, &tag) && tag.has_art && tag.art_len > 0) {
            FILE *f = fopen(r->tracks[0].path, "rb");
            if (f) {
                unsigned char *b = (unsigned char *)malloc(tag.art_len);
                if (b) {
                    fseek(f, tag.art_offset, SEEK_SET);
                    if (fread(b, 1, tag.art_len, f) == (size_t)tag.art_len)
                        t = image_load_jpeg_mem(b, tag.art_len, size);
                    free(b);
                }
                fclose(f);
            }
        }
    }

    if (!t) t = image_make_placeholder(size, str_hash(r->name));
    return t;
}

void update_preview(void)
{
    int count = 0;
    Record *list = lib_current_list(&count);

    if (g_app.preview_for == g_app.lib_sel &&
        g_app.preview_mode == (int)g_app.mode && g_app.preview_tex)
        return;

    if (g_app.preview_tex) { tex_free(g_app.preview_tex); g_app.preview_tex = NULL; }

    if (list && count > 0 && g_app.lib_sel >= 0 && g_app.lib_sel < count)
        g_app.preview_tex = load_cover_for_record(&list[g_app.lib_sel], COVER_TEX);

    g_app.preview_for  = g_app.lib_sel;
    g_app.preview_mode = (int)g_app.mode;
}

void open_record(int index)
{
    int count = 0;
    Record *list = lib_current_list(&count);
    if (!list || index < 0 || index >= count) return;

    g_app.rec = &list[index];
    record_load_metadata(g_app.rec);
    g_app.rec_sel = 0;
    g_app.rec_top = 0;

    if (g_app.rec_tex) { tex_free(g_app.rec_tex); g_app.rec_tex = NULL; }
    if (g_app.rec_thumb_tex) { tex_free(g_app.rec_thumb_tex); g_app.rec_thumb_tex = NULL; }
    g_app.rec_tex = load_cover_for_record(g_app.rec, COVER_TEX);

    g_app.rec_thumb_tex = load_cover_for_record(g_app.rec, REC_ART);

    g_app.screen = SCREEN_RECORD;
}

void go_library(void)
{
    audio_stop();
    if (g_app.rec_tex) { tex_free(g_app.rec_tex); g_app.rec_tex = NULL; }
    if (g_app.rec_thumb_tex) { tex_free(g_app.rec_thumb_tex); g_app.rec_thumb_tex = NULL; }
    g_app.rec = NULL;
    g_app.screen = SCREEN_LIBRARY;

    g_app.preview_for = -1;
#if LYRICS_ENABLED
    lyrics_free(&g_app.lyrics);
    g_app.lyrics_view = 0;
    g_app.lyrics_anim = 0.0f;
#endif
}

#if LYRICS_ENABLED

static void lrc_path_for(const char *mp3, char *out, int n)
{
    int len = (int)strlen(mp3), dot = len, i;
    for (i = len - 1; i >= 0; i--) {
        if (mp3[i] == '/' || mp3[i] == '\\') break;
        if (mp3[i] == '.') { dot = i; break; }
    }
    if (dot > n - 5) dot = n - 5;
    memcpy(out, mp3, (size_t)dot);
    out[dot]   = '.'; out[dot + 1] = 'l';
    out[dot + 2] = 'r'; out[dot + 3] = 'c';
    out[dot + 4] = '\0';
}
#endif

void start_play(int index, int go_nowplaying, int animate)
{
    Record *r = g_app.rec;
    if (!r || index < 0 || index >= r->track_count) return;

    g_app.np_index = index;
    g_app.scrub_dir = 0;
    audio_play_file(r->tracks[index].path, r->tracks[index].duration_sec);

#if LYRICS_ENABLED
    {
        char lp[MAX_PATH_LEN];
        lrc_path_for(r->tracks[index].path, lp, sizeof(lp));
        lyrics_free(&g_app.lyrics);
        lyrics_load(&g_app.lyrics, lp);
    }
#endif

    if (go_nowplaying) {
        g_app.screen = SCREEN_NOWPLAYING;
        g_app.np_anim = animate ? 0.0f : 1.0f;
    }
}

static unsigned int rng_state = 0;
static unsigned int rng_next(void)
{
    if (rng_state == 0)
        rng_state = (unsigned int)(g_app.time * 1000.0f + 1.0f) | 1u;
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 17;
    rng_state ^= rng_state << 5;
    return rng_state;
}

int next_track_index(int cur)
{
    int n = g_app.rec ? g_app.rec->track_count : 0;
    if (n <= 1) return cur;
    if (g_app.shuffle) {
        unsigned int r = rng_next();
        /* rejection sampling: eliminate modulo bias for small n */
        unsigned int limit = (unsigned int)(n - 1);
        unsigned int max_valid = (unsigned int)(-1) - ((unsigned int)(-1) % limit);
        while (r >= max_valid) r = rng_next();
        return (cur + 1 + (int)(r % limit)) % n;
    }
    return cur + 1;
}

void handle_auto_advance(void)
{
    if (!audio_finished()) return;
    audio_clear_finished();
    if (!g_app.rec) return;

    /* queue takes priority */
    if (g_app.queue_index >= 0 && g_app.queue_index < g_app.rec->track_count) {
        int qi = g_app.queue_index;
        g_app.queue_index = -1;
        start_play(qi, 0, 0);
        return;
    }

    if (g_app.shuffle && g_app.rec->track_count > 1) {

        start_play(next_track_index(g_app.np_index), 0, 0);
    } else if (g_app.np_index < g_app.rec->track_count - 1) {

        start_play(g_app.np_index + 1, 0, 0);
    }

}
