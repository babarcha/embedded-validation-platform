#include <stdio.h>
#include <string.h>

#include "driver/uart.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define DUT_MODEL "ESP32-DUT"
#define FW_VERSION "1.0.0"
#define TEMP_CDEG 2345

#define DUT_UART UART_NUM_0
#define UART_RX_BUFFER_SIZE 256
#define COMMAND_BUFFER_SIZE 128

static void process_command(const char *command)
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

void app_main(void)
{
    char command[COMMAND_BUFFER_SIZE];
    size_t command_length = 0;

    /*
     * UART0 is already used by the ESP-IDF console.
     * Install a UART driver so reads can use a finite timeout
     * instead of blocking indefinitely in fgets().
     */
    ESP_ERROR_CHECK(
        uart_driver_install(
            DUT_UART,
            UART_RX_BUFFER_SIZE,
            0,
            0,
            NULL,
            0));

    printf("ESP32 Validation DUT ready\n");
    fflush(stdout);

    while (1)
    {
        uint8_t byte;

        int received = uart_read_bytes(
            DUT_UART,
            &byte,
            1,
            pdMS_TO_TICKS(100));

        if (received > 0)
        {
            if (byte == '\r' || byte == '\n')
            {
                if (command_length > 0)
                {
                    command[command_length] = '\0';

                    process_command(command);

                    command_length = 0;
                }
            }
            else if (command_length < sizeof(command) - 1)
            {
                command[command_length++] = (char)byte;
            }
            else
            {
                /*
                 * Command exceeded our buffer.
                 * Discard it rather than overflowing the buffer.
                 */
                command_length = 0;
            }
        }
    }
}