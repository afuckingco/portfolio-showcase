#include <pspctrl.h>
#include <stdio.h>

#include "app.h"
#include "gfx.h"
#include "text.h"
#include "theme.h"
#include "widgets.h"
#include "glyphs.h"

#define REC_ROW_H    GRID
#define REC_VISIBLE  8
#define REC_LIST_TOP GY(6)
#define REC_NAME     GX(3)
#define SHUF_SZ      16

static void dab_line(float x0, float y0, float x1, float y1, float t, unsigned int c)
{
    float dx = x1 - x0, dy = y1 - y0;
    float adx = dx < 0 ? -dx : dx, ady = dy < 0 ? -dy : dy;
    int   i, n = (int)((adx > ady ? adx : ady) + 0.5f);
    if (n < 1) n = 1;
    for (i = 0; i <= n; i++) {
        float u = (float)i / (float)n;
        gfx_quad(x0 + dx * u - t * 0.5f, y0 + dy * u - t * 0.5f, t, t, c);
    }
}

static void arrow_right(float tx, float ty, float len, float hh, unsigned int c)
{
    int i, n = (int)(len + 0.5f);
    if (n < 1) n = 1;
    for (i = 0; i <= n; i++) {
        float half = (float)(n - i) / (float)n * hh;
        gfx_quad(tx - (float)i, ty - half, 1.0f, half * 2.0f + 1.0f, c);
    }
}

static void draw_shuffle(int x, int y, int s, unsigned int c)
{
    float t   = 2.0f;
    float ahl = s * 0.26f;
    float ahh = s * 0.17f;
    float top = y + ahh;
    float bot = y + s - ahh;
    float cx  = x + s * 0.40f;
    float cy  = y + s * 0.5f;
    float hx  = x + s * 0.52f;
    float tip = x + s;

    dab_line((float)x, top, cx, cy, t, c);
    dab_line(cx, cy, hx, bot, t, c);
    dab_line(hx, bot, tip - ahl, bot, t, c);
    arrow_right(tip, bot, ahl, ahh, c);

    dab_line((float)x, bot, cx, cy, t, c);
    dab_line(cx, cy, hx, top, t, c);
    dab_line(hx, top, tip - ahl, top, t, c);
    arrow_right(tip, top, ahl, ahh, c);
}

void scr_record(void)
{
    Record *r = g_app.rec;
    int mx = PAD + REC_ART + GRID;
    char buf[80];
    int i;

    if (!r) { go_library(); return; }

    if (PRESSED(PSP_CTRL_CIRCLE)) { go_library(); return; }

    if ((HELD(PSP_CTRL_LTRIGGER) && PRESSED(PSP_CTRL_SQUARE)) ||
        (HELD(PSP_CTRL_SQUARE)   && PRESSED(PSP_CTRL_LTRIGGER)))
        g_app.shuffle = !g_app.shuffle;
    if (r->track_count > 0) {
        if (PRESSED(PSP_CTRL_DOWN) && g_app.rec_sel < r->track_count - 1) g_app.rec_sel++;
        if (PRESSED(PSP_CTRL_UP)   && g_app.rec_sel > 0)                  g_app.rec_sel--;
        if (PRESSED(PSP_CTRL_RIGHT)) g_app.rec_sel += REC_VISIBLE;
        if (PRESSED(PSP_CTRL_LEFT))  g_app.rec_sel -= REC_VISIBLE;
        if (g_app.rec_sel < 0) g_app.rec_sel = 0;
        if (g_app.rec_sel > r->track_count - 1) g_app.rec_sel = r->track_count - 1;
        if (PRESSED(PSP_CTRL_CROSS)) {
            if (HELD(PSP_CTRL_LTRIGGER)) {
                g_app.queue_index = g_app.rec_sel;
                config_save();
            } else { start_play(g_app.rec_sel, 1, 1); return; }
        }
    }

    if (g_app.rec_sel < g_app.rec_top) g_app.rec_top = g_app.rec_sel;
    if (g_app.rec_sel >= g_app.rec_top + REC_VISIBLE)
        g_app.rec_top = g_app.rec_sel - REC_VISIBLE + 1;
    if (g_app.rec_top < 0) g_app.rec_top = 0;

    ui_statusbar("2TUFF.WAV", r->is_playlist ? "PLAYLIST" : "ALBUM");

    ui_frame(PAD - 1, CONTENT_TOP - 1, REC_ART + 2, REC_ART + 2);
    if (g_app.rec_thumb_tex)
        gfx_blit_nn(g_app.rec_thumb_tex, PAD, CONTENT_TOP, REC_ART, REC_ART, RGB(255, 255, 255));

    text_put_clip(F_LG, mx, CONTENT_TOP, TH.ink, r->name, SCR_W - mx - PAD);
    text_put_clip(F_SM, mx, GY(3), TH.accent,
                  r->artist[0] ? r->artist : (r->is_playlist ? "PLAYLIST" : "-"),
                  SCR_W - mx - PAD);
    if (r->year > 0)
        snprintf(buf, sizeof(buf), "YEAR %d    TRK %02d", r->year, r->track_count);
    else
        snprintf(buf, sizeof(buf), "TRK %02d", r->track_count);
    text_put(F_SM, mx, GY(4), TH.ink_dim, buf);

    draw_shuffle(SCR_W - PAD - SHUF_SZ, GY(4) + (font_ch(F_SM) - SHUF_SZ) / 2,
                 SHUF_SZ, g_app.shuffle ? TH.accent : TH.ink_mute);

    ui_rule(0, GY(5), SCR_W);

    for (i = 0; i < REC_VISIBLE; i++) {
        int idx = g_app.rec_top + i;
        int ry = REC_LIST_TOP + i * REC_ROW_H;
        int sel = (idx == g_app.rec_sel);
        Track *t;
        unsigned int cno, ctitle;
        char dur[12];
        if (idx >= r->track_count) break;
        t = &r->tracks[idx];

        if (sel) gfx_quad(PAD - 6, (float)ry, SCR_W - 2 * (PAD - 6), REC_ROW_H, TH.sel_fill);
        cno    = sel ? TH.sel_ink : TH.ink_mute;
        ctitle = sel ? TH.sel_ink : TH.ink_dim;

        snprintf(buf, sizeof(buf), "%02d", t->track_no);
        text_put(F_SM, PAD, ry, cno, buf);
        text_put_clip(F_SM, REC_NAME, ry, ctitle, t->title, SCR_W - REC_NAME - PAD - 48);
        fmt_time(dur, sizeof(dur), t->duration_sec);
        text_put_right(F_SM, SCR_W - PAD, ry, cno, dur);
    }

    snprintf(buf, sizeof(buf), "%02d/%02d", g_app.rec_sel + 1,
             r->track_count > 0 ? r->track_count : 0);
    if (g_app.queue_index >= 0 && g_app.queue_index < r->track_count) {
        char qbuf[24];
        snprintf(qbuf, sizeof(qbuf), " NEXT %02d ", g_app.queue_index + 1);
        int qw = text_w(F_SM, qbuf) + 10;
        int qx = SCR_W - PAD - qw - 70;
        ui_chip(F_SM, qx, FOOTER_TOP + (FOOTER_H - font_ch(F_SM)) / 2,
                qbuf, TH.accent, TH.accent_ink);
    }
    ui_footer(NULL, buf);
}
