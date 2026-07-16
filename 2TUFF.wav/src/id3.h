#ifndef ID3_H
#define ID3_H

typedef struct {
    char title[128];
    char artist[128];
    char album[128];
    int  track;
    int  year;
    int  has_art;
    long art_offset;
    long art_len;
} ID3Tag;

int id3_read(const char *path, ID3Tag *out);

int id3_read_album(const char *path, char *out, int outsz);

#endif
