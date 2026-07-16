#ifndef CONTROLS_H
#define CONTROLS_H

typedef enum {
    BTN_CROSS = 0, BTN_CIRCLE, BTN_TRIANGLE, BTN_SQUARE,
    BTN_DPAD_UP, BTN_DPAD_DOWN, BTN_DPAD_LEFT, BTN_DPAD_RIGHT,
    BTN_L, BTN_R, BTN_SELECT, BTN_START
} PspButton;

int psp_btn(PspButton b, int x, int y, int s);

#define CTRL_W 300
void controls_draw(float anim);

#endif
