#ifndef LIBRARY_H
#define LIBRARY_H

#define MAX_PATH_LEN 512
#define NAME_LEN     128

typedef struct {
    char path[MAX_PATH_LEN];
    char title[NAME_LEN];
    char artist[NAME_LEN];
    int  track_no;
    int  duration_sec;
} Track;

typedef struct {
    char name[NAME_LEN];
    char artist[NAME_LEN];
    char path[MAX_PATH_LEN];
    char cover_path[MAX_PATH_LEN];
    int  year;
    int  is_playlist;
    int  meta_loaded;
    Track *tracks;
    int  track_count;
} Record;

typedef struct {
    Record *albums;     int album_count;
    Record *playlists;  int playlist_count;
    int scanned;
} Library;

void library_init(Library *lib);
int  library_scan(Library *lib, const char *root);
void library_free(Library *lib);

void record_load_metadata(Record *rec);

#endif
