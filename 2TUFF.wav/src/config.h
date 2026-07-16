#ifndef CONFIG_H
#define CONFIG_H

void config_init(const char *eboot_argv0);
void config_load(void);
void config_save(void);

#endif
