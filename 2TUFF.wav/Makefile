TARGET = 2TUFFwav
OBJS = $(patsubst %.c,%.o,$(wildcard src/*.c))

INCDIR =
CFLAGS  = -G0 -O2 -Wall -Wno-format-truncation -fno-strict-aliasing -Isrc
CXXFLAGS = $(CFLAGS) -fno-exceptions -fno-rtti
ASFLAGS  = $(CFLAGS)

LIBDIR =
LDFLAGS =
LIBS = -lpspgu -lpspmp3 -lpspaudio -lpsputility -lpsppower -ljpeg -lm

EXTRA_TARGETS = EBOOT.PBP
PSP_EBOOT_TITLE = 2TUFF.wav
PSP_EBOOT_ICON  = assets/ICON0.PNG

PSPSDK = $(shell psp-config --pspsdk-path)
include $(PSPSDK)/lib/build.mak
