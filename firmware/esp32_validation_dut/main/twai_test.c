#include "twai_test.h"

#include <string.h>

#include "driver/twai.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"

#define TWAI_TX_GPIO  GPIO_NUM_25
#define TWAI_RX_GPIO  GPIO_NUM_26

#define TWAI_TIMEOUT_MS 1000

static const char *TAG = "twai_test";

static bool twai_initialized = false;


esp_err_t twai_test_init(void)
{
    if (twai_initialized)
    {
        return ESP_OK;
    }

    /*
     * No external CAN transceiver is available in Lab 5A.
     * TWAI_MODE_NO_ACK allows transmission without another
     * physical CAN node providing an acknowledgement.
     */
    twai_general_config_t general_config =
        TWAI_GENERAL_CONFIG_DEFAULT(
            TWAI_TX_GPIO,
            TWAI_RX_GPIO,
            TWAI_MODE_NO_ACK
        );

    twai_timing_config_t timing_config =
        TWAI_TIMING_CONFIG_500KBITS();

    twai_filter_config_t filter_config =
        TWAI_FILTER_CONFIG_ACCEPT_ALL();

    esp_err_t result = twai_driver_install(
        &general_config,
        &timing_config,
        &filter_config
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "Failed to install TWAI driver: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    result = twai_start();

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "Failed to start TWAI driver: %s",
            esp_err_to_name(result)
        );

        twai_driver_uninstall();

        return result;
    }

    twai_initialized = true;

    ESP_LOGI(
        TAG,
        "TWAI controller initialized in NO_ACK mode at 500 kbit/s"
    );

    return ESP_OK;
}


esp_err_t twai_test_self_test(void)
{
    if (!twai_initialized)
    {
        return ESP_ERR_INVALID_STATE;
    }

    const uint8_t expected_data[] = {
        0x11,
        0x22,
        0x33,
        0x44,
        0x55,
        0x66,
        0x77,
        0x88,
    };

    twai_message_t tx_message = {
        .identifier = 0x123,
        .data_length_code = sizeof(expected_data),
        .self = 1,
    };

    memcpy(
        tx_message.data,
        expected_data,
        sizeof(expected_data)
    );

    /*
     * Remove stale frames before starting the validation transaction.
     */
    twai_clear_receive_queue();

    esp_err_t result = twai_transmit(
        &tx_message,
        pdMS_TO_TICKS(TWAI_TIMEOUT_MS)
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "TWAI self-test transmit failed: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    twai_message_t rx_message = {0};

    result = twai_receive(
        &rx_message,
        pdMS_TO_TICKS(TWAI_TIMEOUT_MS)
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "TWAI self-test receive failed: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    if (rx_message.identifier != tx_message.identifier)
    {
        ESP_LOGE(
            TAG,
            "TWAI identifier mismatch: expected=0x%03lX received=0x%03lX",
            (unsigned long)tx_message.identifier,
            (unsigned long)rx_message.identifier
        );

        return ESP_FAIL;
    }

    if (rx_message.data_length_code != sizeof(expected_data))
    {
        ESP_LOGE(
            TAG,
            "TWAI DLC mismatch: expected=%u received=%u",
            (unsigned int)sizeof(expected_data),
            (unsigned int)rx_message.data_length_code
        );

        return ESP_FAIL;
    }

    if (memcmp(
            rx_message.data,
            expected_data,
            sizeof(expected_data)
        ) != 0)
    {
        ESP_LOGE(
            TAG,
            "TWAI payload mismatch"
        );

        return ESP_FAIL;
    }

    ESP_LOGI(
        TAG,
        "TWAI self-test passed: ID=0x%03lX DLC=%u payload verified",
        (unsigned long)rx_message.identifier,
        (unsigned int)rx_message.data_length_code
    );

    return ESP_OK;
}