#include "theme.h"

const Theme THEME_TABLE[2] = {

    {
        .bg          = RGB(228, 225, 214),
        .panel       = RGB(216, 213, 201),
        .ink         = RGB(26, 26, 23),
        .ink_dim     = RGB(92, 90, 82),
        .ink_mute    = RGB(140, 138, 128),
        .rule        = RGB(44, 44, 40),
        .accent      = RGB(192, 72, 42),
        .accent_ink  = RGB(228, 225, 214),
        .sel_fill    = RGB(26, 26, 23),
        .sel_ink     = RGB(228, 225, 214),
        .meter_on    = RGB(26, 26, 23),
        .meter_off   = RGB(196, 193, 182),
        .grid        = RGBA(40, 40, 36, 20),
        .cover_ink   = RGB(26, 26, 23),
        .cover_bg    = RGB(222, 219, 208),
        .cover_invert = 0,
    },

    {
        .bg          = RGB(13, 14, 16),
        .panel       = RGB(22, 24, 27),
        .ink         = RGB(226, 224, 214),
        .ink_dim     = RGB(150, 152, 146),
        .ink_mute    = RGB(96, 100, 98),
        .rule        = RGB(62, 66, 68),
        .accent      = RGB(204, 162, 92),
        .accent_ink  = RGB(13, 14, 16),
        .sel_fill    = RGB(204, 162, 92),
        .sel_ink     = RGB(13, 14, 16),
        .meter_on    = RGB(226, 224, 214),
        .meter_off   = RGB(48, 51, 54),
        .grid        = RGBA(120, 128, 130, 22),
        .cover_ink   = RGB(214, 210, 196),
        .cover_bg    = RGB(18, 20, 22),
        .cover_invert = 1,
    },
};

const Theme *g_theme = &THEME_TABLE[ACTIVE_THEME];

void theme_set(ThemeId id)
{
    if (id == THEME_PAPER || id == THEME_TERMINAL)
        g_theme = &THEME_TABLE[id];
}

ThemeId theme_current(void)
{
    return (g_theme == &THEME_TABLE[THEME_TERMINAL]) ? THEME_TERMINAL : THEME_PAPER;
}
