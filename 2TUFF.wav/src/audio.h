#ifndef AUDIO_H
#define AUDIO_H

typedef enum {
    AUDIO_STOPPED = 0,
    AUDIO_PLAYING,
    AUDIO_PAUSED
} AudioState;

int  audio_init(void);
void audio_shutdown(void);

void audio_play_file(const char *path, int total_sec);
void audio_pause(void);
void audio_resume(void);
void audio_toggle_pause(void);
void audio_stop(void);

void audio_seek(int target_ms);

AudioState audio_state(void);
int   audio_elapsed_sec(void);
int   audio_elapsed_ms(void);
int   audio_total_sec(void);
float audio_progress(void);

int   audio_finished(void);
void  audio_clear_finished(void);

#endif
