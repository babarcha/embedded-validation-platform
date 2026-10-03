#include <stdio.h>

#include "driver/uart.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "i2c_test.h"
#include "command_handler.h"
#include "uart_test.h"

#include "spi_test.h"

#include "command_handler.h"

#define DUT_UART UART_NUM_0
#define UART_RX_BUFFER_SIZE 256
#define COMMAND_BUFFER_SIZE 128

void app_main(void)
{
    char command[COMMAND_BUFFER_SIZE];
    size_t command_length = 0;

    /*
     * UART0 is used as the ESP-IDF console and as the DUT
     * control interface.
     *
     * Install the UART driver so commands can be received
     * with a finite timeout.
     */
    ESP_ERROR_CHECK(
        uart_driver_install(
            DUT_UART,
            UART_RX_BUFFER_SIZE,
            0,
            0,
            NULL,
            0));
    ESP_ERROR_CHECK(i2c_test_init());
    ESP_ERROR_CHECK(spi_test_init());
    ESP_ERROR_CHECK(uart_test_init());

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
                 * Reject an oversized command instead of
                 * allowing the command buffer to overflow.
                 */
                command_length = 0;
            }
        }
    }
}