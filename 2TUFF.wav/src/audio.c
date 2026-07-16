/* Decoding lives on its own thread so a disk or decode stall never freezes the
 * UI. Shared state is guarded by g_lock; the flags are volatile so the compiler
 * re-reads them instead of trusting a stale register. */

#include <pspkernel.h>
#include <pspthreadman.h>
#include <pspaudio.h>
#include <pspmp3.h>
#include <pspiofilemgr.h>
#include <psputility.h>

#include <malloc.h>
#include <string.h>

#include "audio.h"

/* Decoder scratch: mp3buf = compressed bytes in, pcmbuf = samples out. */
#define MP3_BUF_SIZE (16 * 1024)
#define PCM_BUF_SIZE (9216)

enum { REQ_NONE = 0, REQ_PLAY, REQ_STOP, REQ_PAUSE, REQ_RESUME };

static SceUID  g_lock;
static SceUID  g_thread = -1;
static volatile int g_thread_run = 1;

static volatile int g_req = REQ_NONE;
static char         g_req_path[512];
static volatile int g_req_total = 0;

static volatile int g_seek_req = 0;
static volatile int g_seek_ms  = 0;

static volatile int g_state = AUDIO_STOPPED;
static volatile int g_elapsed_ms = 0;
static volatile int g_total_sec = 0;
static volatile int g_finished = 0;

/* 200ms fade-in at track start to avoid click/pop on play */
#define FADE_MS 200
static int g_fade_remaining = 0; /* stereo samples left to ramp */

static unsigned char *g_mp3buf = NULL;
static unsigned char *g_pcmbuf = NULL;

static void lock(void)   { sceKernelWaitSema(g_lock, 1, NULL); }
static void unlock(void) { sceKernelSignalSema(g_lock, 1); }

static int g_src_spc  = 0;
static int g_src_rate = 0;

static int src_ensure(int spc, int rate)
{
    if (g_src_spc == spc && g_src_rate == rate) return 0;   /* nothing changed */
    if (g_src_spc > 0) sceAudioSRCChRelease();              /* ditch old config */
    g_src_spc = 0; g_src_rate = 0;
    if (sceAudioSRCChReserve(spc, rate, 2) < 0) return -1;  /* 2 = stereo */
    g_src_spc = spc; g_src_rate = rate;
    return 0;
}

static void play_file(const char *path, int total)
{
    SceUID fd;
    int handle, rate, eof = 0;
    int stream_start = 0, stream_end;
    int spf;
    long long played = 0;

    unsigned char id3[10];
    SceMp3InitArg arg;

    fd = sceIoOpen(path, PSP_O_RDONLY, 0777);
    if (fd < 0) { g_state = AUDIO_STOPPED; return; }

    /* seek to EOF -> that offset is the size, then rewind to byte 0 */
    stream_end = sceIoLseek32(fd, 0, PSP_SEEK_END);
    sceIoLseek32(fd, 0, PSP_SEEK_SET);

    if (sceIoRead(fd, id3, 10) == 10 &&
        id3[0] == 'I' && id3[1] == 'D' && id3[2] == '3') {
        stream_start = 10 + (((int)(id3[6] & 0x7f) << 21) |
                             ((id3[7] & 0x7f) << 14) |
                             ((id3[8] & 0x7f) << 7) |
                             (id3[9] & 0x7f));
    }
    /* bogus tag length? just decode from the top */
    if (stream_start < 0 || stream_start >= stream_end) stream_start = 0;

    memset(&arg, 0, sizeof(arg));
    arg.mp3StreamStart = stream_start;
    arg.mp3StreamEnd   = stream_end;
    arg.mp3Buf     = g_mp3buf;
    arg.mp3BufSize = MP3_BUF_SIZE;
    arg.pcmBuf     = g_pcmbuf;
    arg.pcmBufSize = PCM_BUF_SIZE;

    handle = sceMp3ReserveMp3Handle(&arg);
    if (handle < 0) { sceIoClose(fd); g_state = AUDIO_STOPPED; return; }

    /* Init() needs a first chunk before it knows rate/frame size, so prime the
     * pump by hand: the decoder says where + how much to read, we shovel the
     * bytes in and report how many actually landed. */
    {
        SceUChar8 *dst; SceInt32 towrite, srcpos; int rd;
        if (sceMp3GetInfoToAddStreamData(handle, &dst, &towrite, &srcpos) >= 0) {
            sceIoLseek32(fd, srcpos, PSP_SEEK_SET);
            rd = sceIoRead(fd, dst, towrite);
            if (rd < 0) rd = 0;
            if (rd == 0 || srcpos + rd >= stream_end) eof = 1;
            sceMp3NotifyAddStreamData(handle, rd);
        }
    }

    if (sceMp3Init(handle) < 0) {
        sceMp3ReleaseMp3Handle(handle);
        sceIoClose(fd);
        g_state = AUDIO_STOPPED;
        return;
    }

    /* decoder's chewed a frame now, so these are trustworthy.
     * spf = samples/frame (1152 is the classic layer-III number). */
    rate = sceMp3GetSamplingRate(handle);
    if (rate <= 0) rate = 44100;
    spf = sceMp3GetMaxOutputSample(handle);
    if (spf <= 0) spf = 1152;

    sceMp3SetLoopNum(handle, 0);

    g_total_sec   = (total > 0) ? total : 0;
    g_elapsed_ms  = 0;
    g_finished    = 0;
    g_fade_remaining = (rate > 0) ? FADE_MS * rate / 1000 : 0;
    g_state       = AUDIO_PLAYING;
    lock(); g_seek_req = 0; unlock();

    /* main loop, one MP3 frame per pass: poll requests, feed, decode, push out */
    for (;;) {
        int req, do_seek, seek_ms;
        short *buf = NULL;
        int dec, spc;

        /* snapshot shared state under the lock, then act on the copies once it's
         * released, so the UI thread never blocks behind a slow decode */
        lock();
        req = g_req;
        if (req == REQ_STOP) { g_req = REQ_NONE; unlock(); break; } /* kill this song */
        if (req == REQ_PLAY) { unlock(); break; }  /* new song queued: bail, let the thread restart it */
        if (req == REQ_PAUSE)  { g_req = REQ_NONE; g_state = AUDIO_PAUSED; }
        else if (req == REQ_RESUME) { g_req = REQ_NONE; g_state = AUDIO_PLAYING; }
        do_seek = g_seek_req; seek_ms = g_seek_ms; g_seek_req = 0;
        unlock();

        if (do_seek) {
            /* MP3 seeks by frame, not ms, so turn time -> frame index, clamp,
             * jump, then rebuild the clock so the progress bar doesn't lie */
            long long tframe = (long long)seek_ms * rate / 1000 / spf;
            int frames = sceMp3GetFrameNum(handle);
            if (tframe < 0) tframe = 0;
            if (frames > 0 && tframe > frames - 1) tframe = frames - 1;
            if (sceMp3ResetPlayPositionByFrame(handle, (SceUInt32)tframe) >= 0) {
                played = tframe * spf;
                g_elapsed_ms = (int)(played * 1000 / rate);
                eof = 0;                 /* seeking back un-ends the stream */
            }
        }

        /* paused: idle a beat instead of decoding, but keep polling requests */
        if (g_state == AUDIO_PAUSED) { sceKernelDelayThread(12000); continue; }

        /* streaming heart: keep a small window fed instead of loading the whole
         * file. The decoder says when it's hungry and where to read; we just
         * shuttle bytes until it's full or we hit EOF. */
        while (sceMp3CheckStreamDataNeeded(handle) > 0) {
            SceUChar8 *dst; SceInt32 towrite, srcpos; int rd;
            if (sceMp3GetInfoToAddStreamData(handle, &dst, &towrite, &srcpos) < 0)
                break;
            sceIoLseek32(fd, srcpos, PSP_SEEK_SET);
            rd = sceIoRead(fd, dst, towrite);
            if (rd <= 0) { eof = 1; sceMp3NotifyAddStreamData(handle, 0); break; }
            sceMp3NotifyAddStreamData(handle, rd);

            if (srcpos + rd >= stream_end) eof = 1;  /* that was the last of it */
        }

        dec = sceMp3Decode(handle, &buf);
        if (dec <= 0) {
            /* no samples: if the last byte's already in, song's done -> flag it.
             * otherwise it's just a stall, so nap and retry instead of spinning. */
            if (eof) { g_finished = 1; break; }
            sceKernelDelayThread(2000);
            continue;
        }

        /* dec = PCM bytes; stereo 16-bit is 4 bytes/sample, so /4 */
        spc = dec / 4;
        if (spc <= 0) continue;
        if (src_ensure(spc, rate) < 0) { sceKernelDelayThread(2000); continue; }

        /* Blocking is deliberate: it returns only once the hardware drains the
         * buffer, in real time, which paces the whole loop. Free clock. */
        if (g_fade_remaining > 0) {
            int fade_n = (g_fade_remaining < spc) ? g_fade_remaining : spc;
            int i;
            for (i = 0; i < fade_n; i++) {
                int vol = PSP_AUDIO_VOLUME_MAX * (fade_n - i) / fade_n;
                buf[i * 2]     = (short)((int)buf[i * 2]     * vol / PSP_AUDIO_VOLUME_MAX);
                buf[i * 2 + 1] = (short)((int)buf[i * 2 + 1] * vol / PSP_AUDIO_VOLUME_MAX);
            }
            g_fade_remaining -= fade_n;
        }
        sceAudioSRCOutputBlocking(PSP_AUDIO_VOLUME_MAX, buf);

        /* count samples, not wall-clock, so the timer tracks what actually played */
        played += spc;
        g_elapsed_ms = (int)(played * 1000 / rate);
    }

    sceMp3ReleaseMp3Handle(handle);
    sceIoClose(fd);
    g_state = AUDIO_STOPPED;
}

/* Outer loop = idle dispatcher. play_file() blocks for a whole song, so we just
 * sit here waiting for a REQ_PLAY and dive in. Copy the request out under the
 * lock first; the UI thread can clobber g_req_path at any moment. */
static int audio_thread(SceSize args, void *argp)
{
    (void)args; (void)argp;
    while (g_thread_run) {
        int req = REQ_NONE;
        char path[512];
        int total = 0;

        lock();
        if (g_req == REQ_PLAY) {
            req = REQ_PLAY;
            g_req = REQ_NONE;
            strncpy(path, g_req_path, sizeof(path) - 1);  /* grab our own copy */
            path[sizeof(path) - 1] = '\0';
            total = g_req_total;
        } else if (g_req == REQ_STOP) {
            g_req = REQ_NONE;          /* nothing playing, just clear it */
        }
        unlock();

        if (req == REQ_PLAY)
            play_file(path, total);
        else
            sceKernelDelayThread(15000);  /* idle, don't busy-wait */
    }
    return 0;
}

int audio_init(void)
{
    int r;

    sceUtilityLoadModule(PSP_MODULE_AV_MPEGBASE);
    sceUtilityLoadModule(PSP_MODULE_AV_AVCODEC);
    sceUtilityLoadModule(PSP_MODULE_AV_MP3);

    r = sceMp3InitResource();
    if (r < 0) {

        sceUtilityLoadModule(PSP_MODULE_AV_AVCODEC);
        if (sceMp3InitResource() < 0) return -1;
    }

    /* memalign(64), not malloc: the decoder DMAs these, so they must be
     * 64-byte aligned or it'll fail / corrupt memory */
    g_mp3buf = (unsigned char *)memalign(64, MP3_BUF_SIZE);
    g_pcmbuf = (unsigned char *)memalign(64, PCM_BUF_SIZE);
    if (!g_mp3buf || !g_pcmbuf) return -1;

    /* binary semaphore used as a mutex, starts free (count 1) */
    g_lock = sceKernelCreateSema("audio_lock", 0, 1, 1, NULL);
    if (g_lock < 0) return -1;

    g_thread_run = 1;
    g_thread = sceKernelCreateThread("audio_thread", audio_thread,
                                     0x12, 0x10000, 0, NULL);
    if (g_thread < 0) return -1;
    sceKernelStartThread(g_thread, 0, NULL);
    return 0;
}

void audio_shutdown(void)
{
    lock(); g_req = REQ_STOP; unlock();
    g_thread_run = 0;
    if (g_thread >= 0) {
        sceKernelWaitThreadEnd(g_thread, NULL);
        sceKernelDeleteThread(g_thread);
        g_thread = -1;
    }
    if (g_lock >= 0) { sceKernelDeleteSema(g_lock); g_lock = -1; }

    if (g_src_spc > 0) { sceAudioSRCChRelease(); g_src_spc = 0; g_src_rate = 0; }
    sceMp3TermResource();
    free(g_mp3buf); g_mp3buf = NULL;
    free(g_pcmbuf); g_pcmbuf = NULL;
}

void audio_play_file(const char *path, int total_sec)
{
    lock();
    g_req = REQ_PLAY;
    strncpy(g_req_path, path, sizeof(g_req_path) - 1);
    g_req_path[sizeof(g_req_path) - 1] = '\0';
    g_req_total = total_sec;
    g_finished = 0;
    unlock();
}

void audio_pause(void)
{
    lock();
    if (g_state == AUDIO_PLAYING) g_req = REQ_PAUSE;
    unlock();
}

void audio_resume(void)
{
    lock();
    if (g_state == AUDIO_PAUSED) g_req = REQ_RESUME;
    unlock();
}

void audio_toggle_pause(void)
{
    int st = g_state;
    if (st == AUDIO_PLAYING) audio_pause();
    else if (st == AUDIO_PAUSED) audio_resume();
}

void audio_stop(void)
{
    lock(); g_req = REQ_STOP; unlock();
}

void audio_seek(int target_ms)
{
    if (target_ms < 0) target_ms = 0;
    lock();
    if (g_state == AUDIO_PLAYING || g_state == AUDIO_PAUSED) {
        g_seek_ms  = target_ms;
        g_seek_req = 1;
    }
    unlock();
}

AudioState audio_state(void)   { return (AudioState)g_state; }
int audio_total_sec(void)      { return g_total_sec; }
int audio_elapsed_sec(void)    { return g_elapsed_ms / 1000; }
int audio_elapsed_ms(void)     { return g_elapsed_ms; }

float audio_progress(void)
{
    int tot = g_total_sec;
    if (tot <= 0) return 0.0f;
    {
        float p = (float)(g_elapsed_ms / 1000.0f) / (float)tot;
        if (p < 0) p = 0;
        if (p > 1) p = 1;
        return p;
    }
}

int  audio_finished(void)       { return g_finished; }
void audio_clear_finished(void) { g_finished = 0; }
