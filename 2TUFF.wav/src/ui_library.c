#include <pspctrl.h>
#include <stdio.h>

#include "app.h"
#include "gfx.h"
#include "text.h"
#include "theme.h"
#include "widgets.h"
#include "glyphs.h"
#include "config.h"
#include "controls.h"
#include "image.h"

#define LIB_ROW_H   GRID
#define LIB_VISIBLE 10
#define LIST_X      GX(1)
#define LIST_NAME   GX(3)
#define LIST_R      GX(16)
#define LIST_DIV    GX(17)
#define LIST_TOP    GY(4)

#define PV          (7 * GRID)
#define PV_X        GX(18)
#define PV_Y        GY(4)

#define SET_W       284
#define SET_DUR     0.22f
#define SET_ROWS    3

static float ease01(float a)
{
    if (a < 0) a = 0;
    if (a > 1) a = 1;
    return a * a * (3.0f - 2.0f * a);
}

static void settings_toggle_theme(void)
{
    theme_set(theme_current() == THEME_PAPER ? THEME_TERMINAL : THEME_PAPER);
    if (g_app.preview_tex) { tex_free(g_app.preview_tex); g_app.preview_tex = NULL; }
    g_app.preview_for = -1;
    config_save();
}

static void settings_toggle_font(void)
{
    text_set_face(text_current_face() == FACE_PLEX ? FACE_PIXEL : FACE_PLEX);
    config_save();
}

static void settings_toggle_cover(void)
{
    image_set_dither(!image_dither());
    if (g_app.preview_tex) { tex_free(g_app.preview_tex); g_app.preview_tex = NULL; }
    g_app.preview_for = -1;
    config_save();
}

static void set_row(int idx, int px, int y, const char *key, const char *val)
{
    int sel = (g_app.settings_sel == idx);
    int ix  = px + 14;
    int xr  = px + SET_W - 14;
    unsigned int kc, vc;
    char buf[24];

    if (sel) {
        gfx_quad((float)(px + 8), (float)y, SET_W - 16, 22, TH.sel_fill);
        kc = vc = TH.sel_ink;
        snprintf(buf, sizeof(buf), "< %s >", val);
    } else {
        kc = TH.ink; vc = TH.ink_dim;
        snprintf(buf, sizeof(buf), "%s", val);
    }
    text_put(F_SM, ix, y + 4, kc, key);
    text_put_right(F_SM, xr, y + 4, vc, buf);
}

static void draw_settings(void)
{
    float e  = ease01(g_app.settings_anim);
    int   px = SCR_W - (int)(SET_W * e);
    int   ix = px + 14;
    int   xr = px + SET_W - 14;
    int   y;
    char  buf[32];

    gfx_quad(0, 0, SCR_W, SCR_H, RGBA(0, 0, 0, (unsigned int)(120.0f * e)));

    gfx_quad((float)px, 0, SET_W, SCR_H, TH.panel);
    gfx_quad((float)px, 0, 3, SCR_H, TH.accent);

    text_put(F_LG, ix, 12, TH.ink, "SETTINGS");
    ui_rule(px + 10, 48, SET_W - 20);

    set_row(0, px, 58, "THEME",
            theme_current() == THEME_TERMINAL ? "DARK" : "LIGHT");
    set_row(1, px, 84, "FONT",
            text_current_face() == FACE_PIXEL ? "PIXELIFY" : "PLEX MONO");
    set_row(2, px, 110, "COVER",
            image_dither() ? "DITHERED" : "ORIGINAL");

    y = 146;
    text_put(F_SM, ix, y, TH.ink_mute, "LIBRARY");
    ui_dotrule(px + 10, y + 15, SET_W - 20);
    snprintf(buf, sizeof(buf), "%d", g_app.lib.album_count);
    ui_kv_right(ix, y + 23, xr, "ALBUMS", buf);
    snprintf(buf, sizeof(buf), "%d", g_app.lib.playlist_count);
    ui_kv_right(ix, y + 39, xr, "PLAYLISTS", buf);
}

void scr_library(void)
{
    int count = 0;
    Record *list = lib_current_list(&count);
    const char *mode;
    char buf[64];
    int i;
    float dt = gfx_dt();
    float tgt;

    if (g_app.settings_open) {

        if (PRESSED(PSP_CTRL_TRIANGLE) || PRESSED(PSP_CTRL_CIRCLE))
            g_app.settings_open = 0;
        if (PRESSED(PSP_CTRL_UP)   && g_app.settings_sel > 0) g_app.settings_sel--;
        if (PRESSED(PSP_CTRL_DOWN) && g_app.settings_sel < SET_ROWS - 1)
            g_app.settings_sel++;
        if (PRESSED(PSP_CTRL_CROSS) || PRESSED(PSP_CTRL_LEFT) ||
            PRESSED(PSP_CTRL_RIGHT)) {
            if      (g_app.settings_sel == 0) settings_toggle_theme();
            else if (g_app.settings_sel == 1) settings_toggle_font();
            else                              settings_toggle_cover();
        }
    } else if (g_app.controls_open) {

        if (PRESSED(PSP_CTRL_SELECT) || PRESSED(PSP_CTRL_CIRCLE) ||
            PRESSED(PSP_CTRL_TRIANGLE))
            g_app.controls_open = 0;
    } else if (PRESSED(PSP_CTRL_TRIANGLE)) {
        g_app.settings_open = 1;
    } else if (PRESSED(PSP_CTRL_SELECT)) {
        g_app.controls_open = 1;
    } else {

        if (PRESSED(PSP_CTRL_SQUARE)) {
            g_app.mode = (g_app.mode == MODE_ALBUMS) ? MODE_PLAYLISTS : MODE_ALBUMS;
            g_app.lib_sel = 0;
            g_app.lib_top = 0;
            g_app.preview_for = -1;
            list = lib_current_list(&count);
        }
        if (count > 0) {
            if (PRESSED(PSP_CTRL_DOWN)  && g_app.lib_sel < count - 1) g_app.lib_sel++;
            if (PRESSED(PSP_CTRL_UP)    && g_app.lib_sel > 0)         g_app.lib_sel--;
            if (PRESSED(PSP_CTRL_RIGHT)) g_app.lib_sel += LIB_VISIBLE;
            if (PRESSED(PSP_CTRL_LEFT))  g_app.lib_sel -= LIB_VISIBLE;
            if (g_app.lib_sel < 0) g_app.lib_sel = 0;
            if (g_app.lib_sel > count - 1) g_app.lib_sel = count - 1;
            if (PRESSED(PSP_CTRL_CROSS)) { open_record(g_app.lib_sel); return; }
        }

    }

    tgt = g_app.settings_open ? 1.0f : 0.0f;
    if (g_app.settings_anim < tgt) {
        g_app.settings_anim += dt / SET_DUR;
        if (g_app.settings_anim > tgt) g_app.settings_anim = tgt;
    } else if (g_app.settings_anim > tgt) {
        g_app.settings_anim -= dt / SET_DUR;
        if (g_app.settings_anim < tgt) g_app.settings_anim = tgt;
    }
    tgt = g_app.controls_open ? 1.0f : 0.0f;
    if (g_app.controls_anim < tgt) {
        g_app.controls_anim += dt / SET_DUR;
        if (g_app.controls_anim > tgt) g_app.controls_anim = tgt;
    } else if (g_app.controls_anim > tgt) {
        g_app.controls_anim -= dt / SET_DUR;
        if (g_app.controls_anim < tgt) g_app.controls_anim = tgt;
    }

    if (g_app.lib_sel < g_app.lib_top) g_app.lib_top = g_app.lib_sel;
    if (g_app.lib_sel >= g_app.lib_top + LIB_VISIBLE)
        g_app.lib_top = g_app.lib_sel - LIB_VISIBLE + 1;
    if (g_app.lib_top < 0) g_app.lib_top = 0;

    update_preview();

    mode = (g_app.mode == MODE_ALBUMS) ? "ALBUMS" : "PLAYLISTS";

    ui_statusbar("2TUFF.WAV", "MS0:/MUSIC");
    text_put(F_LG, PAD, CONTENT_TOP, TH.ink, "LIBRARY");
    {
        int w = text_w(F_SM, mode) + 10;

        int chip_y = CONTENT_TOP + (font_ch(F_LG) - font_ch(F_SM)) / 2;
        ui_chip(F_SM, (PV_X + PV) - w, chip_y, mode, TH.accent, TH.accent_ink);
    }
    ui_rule(0, GY(3), SCR_W);
    ui_vrule(LIST_DIV, LIST_TOP, FOOTER_TOP - LIST_TOP);

    if (count == 0) {
        text_put(F_SM, LIST_X, LIST_TOP, TH.ink_dim,
                 (g_app.mode == MODE_ALBUMS) ? "NO ALBUMS FOUND"
                                             : "NO PLAYLISTS FOUND");
        text_put(F_SM, LIST_X, LIST_TOP + GRID, TH.ink_mute, "PUT MUSIC IN MS0:/MUSIC");
    } else {
        for (i = 0; i < LIB_VISIBLE; i++) {
            int idx = g_app.lib_top + i;
            int ry = LIST_TOP + i * LIB_ROW_H;
            int sel = (idx == g_app.lib_sel);
            unsigned int cidx, cname;
            if (idx >= count) break;

            if (sel) gfx_quad(LIST_X - 6, (float)ry, LIST_DIV - (LIST_X - 6),
                              LIB_ROW_H, TH.sel_fill);
            cidx  = sel ? TH.sel_ink : TH.ink_mute;
            cname = sel ? TH.sel_ink : TH.ink_dim;

            snprintf(buf, sizeof(buf), "%02d", idx + 1);
            text_put(F_SM, LIST_X, ry, cidx, buf);
            text_put_clip(F_SM, LIST_NAME, ry, cname, list[idx].name,
                          LIST_R - LIST_NAME - GRID);
            snprintf(buf, sizeof(buf), "%d", list[idx].track_count);
            text_put_right(F_SM, LIST_R, ry, cidx, buf);
        }
    }

    {
        ui_frame(PV_X - 2, PV_Y - 2, PV + 4, PV + 4);
        if (g_app.preview_tex)
            gfx_blit_nn(g_app.preview_tex, PV_X, PV_Y, PV, PV, RGB(255, 255, 255));
        else
            ui_grid(F_SM, PV_X, PV_Y, PV / font_cw(F_SM),
                    PV / font_ch(F_SM), GC_MED, TH.rule);

        if (count > 0) {
            Record *r = &list[g_app.lib_sel];
            text_put_clip(F_SM, PV_X, PV_Y + PV, TH.ink, r->name,
                          SCR_W - PV_X - PAD);
            snprintf(buf, sizeof(buf), "TRK %02d", r->track_count);
            text_put(F_SM, PV_X, PV_Y + PV + GRID, TH.ink_dim, buf);
            snprintf(buf, sizeof(buf), "%02d/%02d", g_app.lib_sel + 1, count);
            text_put_right(F_SM, PV_X + PV, PV_Y + PV + GRID, TH.ink_dim, buf);
        }
    }

    ui_rule(0, FOOTER_TOP, SCR_W);
    {
        int bs = 13;
        int bw = psp_btn(BTN_SELECT, PAD, FOOTER_TOP + (FOOTER_H - bs) / 2, bs);
        text_put(F_SM, PAD + bw + 8, FOOTER_TOP + 1, TH.ink_mute, "CONTROLS");
    }
    snprintf(buf, sizeof(buf), "%02d REC", count);
    text_put_right(F_SM, SCR_W - PAD, FOOTER_TOP + 1, TH.ink_mute, buf);

    if (g_app.settings_anim > 0.001f) draw_settings();
    if (g_app.controls_anim > 0.001f) controls_draw(g_app.controls_anim);
}
