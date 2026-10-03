#include <stdio.h>
#include <string.h>

#include "command_handler.h"
#include "i2c_test.h"
#include "spi_test.h"
#include "uart_test.h"

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
    else if (strcmp(command, "I2C_SCAN") == 0)
    {
        int device_count = i2c_test_scan();

        if (device_count < 0)
        {
            printf("ERROR=I2C_NOT_INITIALIZED\n");
        }
        else
        {
            printf("I2C_DEVICES=%d\n", device_count);
        }
    }
    else if (strcmp(command, "SPI_LOOPBACK") == 0)
    {
        esp_err_t result = spi_test_loopback();

        if (result == ESP_OK)
        {
            printf("SPI_LOOPBACK=PASS\n");
        }
        else
        {
            printf("SPI_LOOPBACK=FAIL\n");
        }
    }
    else if (strcmp(command, "UART_LOOPBACK") == 0)
    {
        esp_err_t result = uart_test_loopback();

        if (result == ESP_OK)
        {
            printf("UART_LOOPBACK=PASS\n");
        }
        else
        {
            printf("UART_LOOPBACK=FAIL\n");
        }
    }
    else
    {
        printf("ERROR=UNKNOWN_COMMAND\n");
    }

    fflush(stdout);
}