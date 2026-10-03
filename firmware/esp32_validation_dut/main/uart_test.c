#include "uart_test.h"

#include <string.h>

#include "driver/uart.h"
#include "esp_log.h"

#define UART_TEST_PORT       UART_NUM_2

#define UART_TEST_TX_GPIO    17
#define UART_TEST_RX_GPIO    16

#define UART_TEST_BAUD_RATE  115200
#define UART_RX_BUFFER_SIZE  256
#define UART_TIMEOUT_MS      500

static const char *TAG = "uart_test";

static bool uart_initialized = false;


esp_err_t uart_test_init(void)
{
    if (uart_initialized)
    {
        return ESP_OK;
    }

    uart_config_t uart_config = {
        .baud_rate = UART_TEST_BAUD_RATE,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };

    esp_err_t result = uart_param_config(
        UART_TEST_PORT,
        &uart_config
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "Failed to configure UART2: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    result = uart_set_pin(
        UART_TEST_PORT,
        UART_TEST_TX_GPIO,
        UART_TEST_RX_GPIO,
        UART_PIN_NO_CHANGE,
        UART_PIN_NO_CHANGE
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "Failed to configure UART2 pins: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    result = uart_driver_install(
        UART_TEST_PORT,
        UART_RX_BUFFER_SIZE,
        0,
        0,
        NULL,
        0
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "Failed to install UART2 driver: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    uart_initialized = true;

    ESP_LOGI(
        TAG,
        "UART2 initialized: TX=%d RX=%d baud=%d",
        UART_TEST_TX_GPIO,
        UART_TEST_RX_GPIO,
        UART_TEST_BAUD_RATE
    );

    return ESP_OK;
}


esp_err_t uart_test_loopback(void)
{
    if (!uart_initialized)
    {
        return ESP_ERR_INVALID_STATE;
    }

    const uint8_t tx_data[] = {
        0x55,
        0xAA,
        0x00,
        0xFF,
        0x12,
        0x34,
        0x56,
        0x78,
    };

    uint8_t rx_data[sizeof(tx_data)] = {0};

    /*
     * Remove any stale bytes from previous transactions before
     * starting this loopback test.
     */
    esp_err_t result = uart_flush_input(UART_TEST_PORT);

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "Failed to flush UART2 RX buffer: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    int bytes_written = uart_write_bytes(
        UART_TEST_PORT,
        tx_data,
        sizeof(tx_data)
    );

    if (bytes_written != sizeof(tx_data))
    {
        ESP_LOGE(
            TAG,
            "UART2 write failed: wrote %d of %u bytes",
            bytes_written,
            (unsigned int)sizeof(tx_data)
        );

        return ESP_FAIL;
    }

    /*
     * Ensure transmission has physically completed before evaluating
     * the received loopback data.
     */
    result = uart_wait_tx_done(
        UART_TEST_PORT,
        pdMS_TO_TICKS(UART_TIMEOUT_MS)
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "UART2 TX completion timeout: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    int total_received = 0;

    while (total_received < sizeof(tx_data))
    {
        int bytes_received = uart_read_bytes(
            UART_TEST_PORT,
            rx_data + total_received,
            sizeof(tx_data) - total_received,
            pdMS_TO_TICKS(UART_TIMEOUT_MS)
        );

        if (bytes_received <= 0)
        {
            break;
        }

        total_received += bytes_received;
    }

    if (total_received != sizeof(tx_data))
    {
        ESP_LOGE(
            TAG,
            "UART2 loopback length mismatch: received %d of %u bytes",
            total_received,
            (unsigned int)sizeof(tx_data)
        );

        return ESP_FAIL;
    }

    if (memcmp(tx_data, rx_data, sizeof(tx_data)) != 0)
    {
        ESP_LOGE(
            TAG,
            "UART2 loopback data mismatch"
        );

        return ESP_FAIL;
    }

    ESP_LOGI(
        TAG,
        "UART2 loopback passed: %u bytes verified",
        (unsigned int)sizeof(tx_data)
    );

    return ESP_OK;
}