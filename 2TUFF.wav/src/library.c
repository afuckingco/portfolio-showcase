#include <pspiofilemgr.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "library.h"
#include "id3.h"
#include "mp3meta.h"

#define MAX_TRACKS_PER_RECORD 4000

static void scopy(char *dst, int sz, const char *src)
{
    int i = 0;
    if (sz <= 0) return;
    while (src[i] && i < sz - 1) { dst[i] = src[i]; i++; }
    dst[i] = '\0';
}

static void path_join(char *out, int sz, const char *a, const char *b)
{
    int need = (int)strlen(a) + 1 + (int)strlen(b);
    if (need >= sz) { out[0] = '\0'; return; }  /* would overflow: bail */
    snprintf(out, sz, "%s/%s", a, b);
}

static void base_name(char *out, int sz, const char *path)
{
    const char *s = strrchr(path, '/');
    s = s ? s + 1 : path;
    scopy(out, sz, s);
}

static void dir_of(char *out, int sz, const char *path)
{
    char *s;
    scopy(out, sz, path);
    s = strrchr(out, '/');
    if (s) *s = '\0';
    else out[0] = '\0';
}

static void strip_ext(char *s)
{
    char *d = strrchr(s, '.');
    if (d) *d = '\0';
}

static void filename_title(char *out, int sz, const char *name)
{
    int i;
    base_name(out, sz, name);
    strip_ext(out);
    for (i = 0; out[i]; i++)
        if (out[i] == '_') out[i] = ' ';
}

static int has_ext(const char *name, const char *ext)
{
    size_t n = strlen(name), e = strlen(ext), i;
    if (n < e + 1 || name[n - e - 1] != '.') return 0;
    for (i = 0; i < e; i++)
        if (tolower((unsigned char)name[n - e + i]) != tolower((unsigned char)ext[i]))
            return 0;
    return 1;
}

static int ci_starts(const char *s, const char *prefix)
{
    while (*prefix) {
        if (tolower((unsigned char)*s) != tolower((unsigned char)*prefix)) return 0;
        s++; prefix++;
    }
    return 1;
}

static int ci_cmp(const char *a, const char *b)
{
    while (*a && *b) {
        int d = tolower((unsigned char)*a) - tolower((unsigned char)*b);
        if (d) return d;
        a++; b++;
    }
    return tolower((unsigned char)*a) - tolower((unsigned char)*b);
}

static int rec_cmp(const void *x, const void *y)
{
    return ci_cmp(((const Record *)x)->name, ((const Record *)y)->name);
}

static int track_cmp(const void *x, const void *y)
{
    return ci_cmp(((const Track *)x)->path, ((const Track *)y)->path);
}

static int is_dirent_dir(const SceIoDirent *de)
{
    return FIO_S_ISDIR(de->d_stat.st_mode) || (de->d_stat.st_attr & 0x10);
}

static Record *push_record(Record **arr, int *count)
{
    Record *n = (Record *)realloc(*arr, (*count + 1) * sizeof(Record));
    Record *r;
    if (!n) return NULL;
    *arr = n;
    r = &n[*count];
    memset(r, 0, sizeof(Record));
    (*count)++;
    return r;
}

static Track *push_track(Record *r)
{
    Track *n;
    if (r->track_count >= MAX_TRACKS_PER_RECORD) return NULL;
    n = (Track *)realloc(r->tracks, (r->track_count + 1) * sizeof(Track));
    if (!n) return NULL;
    r->tracks = n;
    memset(&n[r->track_count], 0, sizeof(Track));
    return &n[r->track_count++];
}

static int cover_rank(const char *name)
{
    if (!has_ext(name, "jpg") && !has_ext(name, "jpeg")) return -1;
    if (ci_starts(name, "cover"))    return 3;
    if (ci_starts(name, "folder"))   return 2;
    if (ci_starts(name, "front") || ci_starts(name, "albumart")) return 1;
    return 0;
}

static void find_cover_in_dir(const char *dir, char *out, int outsz)
{
    SceUID d;
    SceIoDirent de;
    int best = -1;
    out[0] = '\0';
    d = sceIoDopen(dir);
    if (d < 0) return;
    memset(&de, 0, sizeof(de));
    while (sceIoDread(d, &de) > 0) {
        if (de.d_name[0] && !is_dirent_dir(&de)) {
            int r = cover_rank(de.d_name);
            if (r > best) {
                best = r;
                path_join(out, outsz, dir, de.d_name);
            }
        }
        memset(&de, 0, sizeof(de));
    }
    sceIoDclose(d);
}

static void scan_album(Record *r, const char *dir, const char *display_name)
{
    SceUID d;
    SceIoDirent de;
    int best_cover = -1;

    scopy(r->name, NAME_LEN, display_name);
    scopy(r->path, MAX_PATH_LEN, dir);
    r->is_playlist = 0;
    r->cover_path[0] = '\0';

    d = sceIoDopen(dir);
    if (d < 0) return;
    memset(&de, 0, sizeof(de));
    while (sceIoDread(d, &de) > 0) {
        if (de.d_name[0] && !is_dirent_dir(&de)) {
            if (has_ext(de.d_name, "mp3")) {
                Track *t = push_track(r);
                if (t) {
                    path_join(t->path, MAX_PATH_LEN, dir, de.d_name);
                    filename_title(t->title, NAME_LEN, de.d_name);
                }
            } else {

                int cr = cover_rank(de.d_name);
                if (cr > best_cover) {
                    best_cover = cr;
                    path_join(r->cover_path, MAX_PATH_LEN, dir, de.d_name);
                }
            }
        }
        memset(&de, 0, sizeof(de));
    }
    sceIoDclose(d);

    if (r->track_count > 1)
        qsort(r->tracks, r->track_count, sizeof(Track), track_cmp);
}

static void normalize_slashes(char *s)
{
    for (; *s; s++) if (*s == '\\') *s = '/';
}

static int looks_absolute(const char *p)
{
    if (p[0] == '/') return 1;
    if (p[0] && p[1] == ':') return 1;
    if (strstr(p, ":/")) return 1;
    return 0;
}

static void add_playlist_track(Record *r, const char *base_dir,
                               const char *raw, const char *title)
{
    char line[MAX_PATH_LEN];
    Track *t;
    scopy(line, sizeof(line), raw);
    normalize_slashes(line);

    {
        char *s = line;
        char *e;
        while (*s == ' ' || *s == '\t') s++;
        if (s != line) memmove(line, s, strlen(s) + 1);
        e = line + strlen(line);
        while (e > line && (e[-1] == ' ' || e[-1] == '\t' || e[-1] == '\r' || e[-1] == '\n'))
            *--e = '\0';
    }
    if (!line[0]) return;

    /* reject paths with ".." to prevent directory traversal */
    {
        const char *p = line;
        while (*p) {
            if (p[0] == '.' && p[1] == '.' && (p[2] == '/' || p[2] == '\\' || p[2] == '\0'))
                return;
            p++;
        }
    }

    t = push_track(r);
    if (!t) return;
    if (looks_absolute(line)) scopy(t->path, MAX_PATH_LEN, line);
    else path_join(t->path, MAX_PATH_LEN, base_dir, line);

    if (title && title[0]) scopy(t->title, NAME_LEN, title);
    else filename_title(t->title, NAME_LEN, t->path);
}

static void scan_playlist(Record *r, const char *plpath)
{
    char dir[MAX_PATH_LEN];
    char line[1024];
    char pend_title[NAME_LEN];
    FILE *f;
    int is_pls;

    base_name(r->name, NAME_LEN, plpath);
    strip_ext(r->name);
    scopy(r->path, MAX_PATH_LEN, plpath);
    r->is_playlist = 1;
    pend_title[0] = '\0';

    dir_of(dir, sizeof(dir), plpath);
    is_pls = has_ext(plpath, "pls");

    f = fopen(plpath, "r");
    if (!f) return;
    while (fgets(line, sizeof(line), f)) {
        char *nl = strpbrk(line, "\r\n");
        if (nl) *nl = '\0';

        if (is_pls) {
            if (ci_starts(line, "File")) {
                char *eq = strchr(line, '=');
                if (eq) add_playlist_track(r, dir, eq + 1, NULL);
            } else if (ci_starts(line, "Title")) {
                char *eq = strchr(line, '=');
                if (eq && r->track_count > 0)
                    scopy(r->tracks[r->track_count - 1].title, NAME_LEN, eq + 1);
            }
        } else {
            if (line[0] == '#') {
                if (ci_starts(line, "#EXTINF:")) {
                    char *c = strchr(line, ',');
                    if (c) scopy(pend_title, NAME_LEN, c + 1);
                }
                continue;
            }
            if (!line[0]) continue;
            add_playlist_track(r, dir, line, pend_title[0] ? pend_title : NULL);
            pend_title[0] = '\0';
        }
    }
    fclose(f);

    if (r->track_count > 0) {
        char tdir[MAX_PATH_LEN];
        dir_of(tdir, sizeof(tdir), r->tracks[0].path);
        find_cover_in_dir(tdir, r->cover_path, MAX_PATH_LEN);
    }
}

#define CLASSIFY_PROBE_MAX 16
static int record_is_mixed_album(const Record *r)
{
    char first[NAME_LEN];
    int have_first = 0;
    int i;
    int n = r->track_count;
    if (n > CLASSIFY_PROBE_MAX) n = CLASSIFY_PROBE_MAX;

    for (i = 0; i < n; i++) {
        char album[NAME_LEN];
        if (id3_read_album(r->tracks[i].path, album, sizeof(album)) && album[0]) {
            if (!have_first) { scopy(first, sizeof(first), album); have_first = 1; }
            else if (ci_cmp(first, album) != 0) return 1;
        }
    }
    return 0;
}

static void place_record(Library *lib, Record *tmp)
{
    int mixed = record_is_mixed_album(tmp);
    Record *dst = mixed ? push_record(&lib->playlists, &lib->playlist_count)
                        : push_record(&lib->albums, &lib->album_count);
    if (!dst) { free(tmp->tracks); return; }
    *dst = *tmp;
    dst->is_playlist = mixed;
}

void library_init(Library *lib)
{
    memset(lib, 0, sizeof(*lib));
}

int library_scan(Library *lib, const char *root)
{
    SceUID d;
    SceIoDirent de;
    Record loose;
    int have_loose = 0;

    library_free(lib);
    library_init(lib);
    memset(&loose, 0, sizeof(loose));

    d = sceIoDopen(root);
    if (d < 0) { lib->scanned = 1; return 0; }

    memset(&de, 0, sizeof(de));
    while (sceIoDread(d, &de) > 0) {
        const char *nm = de.d_name;
        if (!nm[0] || !strcmp(nm, ".") || !strcmp(nm, "..")) {
            memset(&de, 0, sizeof(de));
            continue;
        }
        if (is_dirent_dir(&de)) {
            char sub[MAX_PATH_LEN];
            Record tmp;
            memset(&tmp, 0, sizeof(tmp));
            path_join(sub, sizeof(sub), root, nm);
            scan_album(&tmp, sub, nm);
            if (tmp.track_count > 0) place_record(lib, &tmp);
            else free(tmp.tracks);
        } else if (has_ext(nm, "m3u") || has_ext(nm, "m3u8") || has_ext(nm, "pls")) {
            char sub[MAX_PATH_LEN];
            Record tmp;
            memset(&tmp, 0, sizeof(tmp));
            path_join(sub, sizeof(sub), root, nm);
            scan_playlist(&tmp, sub);
            if (tmp.track_count > 0) place_record(lib, &tmp);
            else free(tmp.tracks);
        } else if (has_ext(nm, "mp3")) {

            Track *t;
            if (!have_loose) {
                scopy(loose.name, NAME_LEN, "UNSORTED");
                scopy(loose.path, MAX_PATH_LEN, root);
                find_cover_in_dir(root, loose.cover_path, MAX_PATH_LEN);
                have_loose = 1;
            }
            if ((t = push_track(&loose)) != NULL) {
                path_join(t->path, MAX_PATH_LEN, root, nm);
                filename_title(t->title, NAME_LEN, nm);
            }
        }
        memset(&de, 0, sizeof(de));
    }
    sceIoDclose(d);

    if (have_loose && loose.track_count > 0) {
        if (loose.track_count > 1)
            qsort(loose.tracks, loose.track_count, sizeof(Track), track_cmp);
        place_record(lib, &loose);
    } else {
        free(loose.tracks);
    }

    if (lib->album_count > 1)
        qsort(lib->albums, lib->album_count, sizeof(Record), rec_cmp);
    if (lib->playlist_count > 1)
        qsort(lib->playlists, lib->playlist_count, sizeof(Record), rec_cmp);

    lib->scanned = 1;
    return lib->album_count + lib->playlist_count;
}

void record_load_metadata(Record *r)
{
    int i;
    int artist_set = 0;
    int various = 0;

    if (!r || r->meta_loaded) return;

    for (i = 0; i < r->track_count; i++) {
        Track *t = &r->tracks[i];
        ID3Tag tag;
        if (id3_read(t->path, &tag)) {
            if (tag.title[0])  scopy(t->title, NAME_LEN, tag.title);
            if (tag.artist[0]) scopy(t->artist, NAME_LEN, tag.artist);
            if (tag.track > 0) t->track_no = tag.track;
            if (!r->year && tag.year) r->year = tag.year;

            if (tag.artist[0]) {
                if (!artist_set) { scopy(r->artist, NAME_LEN, tag.artist); artist_set = 1; }
                else if (!various && ci_cmp(r->artist, tag.artist) != 0) various = 1;
            }
        }
        if (t->track_no <= 0) t->track_no = i + 1;
        t->duration_sec = mp3_estimate_duration_sec(t->path);
    }

    if (various) scopy(r->artist, NAME_LEN, "VARIOUS ARTISTS");
    if (!artist_set && r->is_playlist) scopy(r->artist, NAME_LEN, "PLAYLIST");
    r->meta_loaded = 1;
}

static void free_records(Record *arr, int n)
{
    int i;
    for (i = 0; i < n; i++) free(arr[i].tracks);
    free(arr);
}

void library_free(Library *lib)
{
    if (!lib) return;
    free_records(lib->albums, lib->album_count);
    free_records(lib->playlists, lib->playlist_count);
    lib->albums = NULL;     lib->album_count = 0;
    lib->playlists = NULL;  lib->playlist_count = 0;
    lib->scanned = 0;
}
