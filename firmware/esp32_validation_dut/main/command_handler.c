#include <stdio.h>
#include <string.h>

#include "command_handler.h"

#define DUT_MODEL "ESP32-DUT"
#define FW_VERSION "1.0.0"
#define TEMP_CDEG 2345

void process_command(const char *command)
{
    if (strcmp(command, "PING") == 0)
    {
        printf("OK\n");
    }
    else if (strcmp(command, "GET_INFO") == 0)
    {
        printf("MODEL=%s;FW=%s\n", DUT_MODEL, FW_VERSION);
    }
    else if (strcmp(command, "GET_TEMP") == 0)
    {
        printf("TEMP_CDEG=%d\n", TEMP_CDEG);
    }
    else
    {
        printf("ERROR=UNKNOWN_COMMAND\n");
    }

    fflush(stdout);
}