#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "lyrics.h"

#if LYRICS_ENABLED

static char *trim(char *s)
{
    char *e;
    while (*s == ' ' || *s == '\t' || *s == '\r' || *s == '\n') s++;
    e = s + strlen(s);
    while (e > s && (e[-1] == ' ' || e[-1] == '\t' ||
                     e[-1] == '\r' || e[-1] == '\n'))
        *--e = '\0';
    return s;
}

static char *clean_dup(const char *src)
{
    int n = (int)strlen(src), i, j = 0, intag = 0;
    char *out = (char *)malloc(n + 1);
    if (!out) return NULL;
    for (i = 0; i < n; i++) {
        unsigned char c = (unsigned char)src[i];
        if (c == '<') { intag = 1; continue; }
        if (c == '>') { intag = 0; continue; }
        if (intag) continue;
        if (c >= 0x20 && c < 0x7F) out[j++] = (char)c;
        else if (c == '\t')        out[j++] = ' ';

    }
    while (j > 0 && out[j - 1] == ' ') j--;
    out[j] = '\0';
    return out;
}

static int parse_stamp(const char *s, int *ms)
{
    int mm; float ss;
    if (*s < '0' || *s > '9') return 0;
    if (sscanf(s, "%d:%f", &mm, &ss) == 2) {
        *ms = mm * 60000 + (int)(ss * 1000.0f + 0.5f);
        return 1;
    }
    return 0;
}

static int cmp_line(const void *a, const void *b)
{
    int ta = ((const LrcLine *)a)->time_ms;
    int tb = ((const LrcLine *)b)->time_ms;
    return (ta > tb) - (ta < tb);
}

static void push(Lyrics *ls, int *cap, int ms, const char *text)
{
    char *dup;
    if (ls->count >= *cap) {
        int nc = *cap ? *cap * 2 : 64;
        LrcLine *nl = (LrcLine *)realloc(ls->lines, (size_t)nc * sizeof(LrcLine));
        if (!nl) return;
        ls->lines = nl; *cap = nc;
    }
    dup = clean_dup(text);
    if (!dup) return;
    ls->lines[ls->count].time_ms = ms;
    ls->lines[ls->count].text    = dup;
    ls->count++;
}

int lyrics_load(Lyrics *ls, const char *lrc_path)
{
    FILE *f;
    char line[1024];
    int cap = 0;

    memset(ls, 0, sizeof(*ls));
    f = fopen(lrc_path, "rb");
    if (!f) return 0;

    while (fgets(line, sizeof(line), f)) {
        char *p = line;
        int stamps[16], ns = 0, i;

        for (;;) {
            char *close;
            const char *inside;
            int ms;
            while (*p == ' ' || *p == '\t') p++;
            if (*p != '[') break;
            close = strchr(p, ']');
            if (!close) break;
            *close = '\0';
            inside = p + 1;
            if (parse_stamp(inside, &ms)) {
                if (ns < 16) stamps[ns++] = ms;
            } else if (strncmp(inside, "offset:", 7) == 0) {
                ls->offset_ms = atoi(inside + 7);
            }
            p = close + 1;
        }

        if (ns > 0) {
            char *text = trim(p);
            for (i = 0; i < ns; i++) push(ls, &cap, stamps[i], text);
        }
    }
    fclose(f);

    if (ls->count > 1)
        qsort(ls->lines, (size_t)ls->count, sizeof(LrcLine), cmp_line);
    return ls->count;
}

void lyrics_free(Lyrics *ls)
{
    int i;
    if (!ls) return;
    for (i = 0; i < ls->count; i++) free(ls->lines[i].text);
    free(ls->lines);
    ls->lines = NULL;
    ls->count = 0;
    ls->offset_ms = 0;
}

int lyrics_index_at(const Lyrics *ls, int ms)
{
    int lo, hi, ans = -1, eff;
    if (!ls || ls->count == 0) return -1;
    eff = ms + ls->offset_ms;
    lo = 0; hi = ls->count - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        if (ls->lines[mid].time_ms <= eff) { ans = mid; lo = mid + 1; }
        else                                 hi = mid - 1;
    }
    return ans;
}

#endif
