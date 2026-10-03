#include "spi_test.h"

#include <string.h>

#include "driver/spi_master.h"
#include "esp_log.h"

#define SPI_HOST_USED       SPI2_HOST

#define SPI_MOSI_GPIO       23
#define SPI_MISO_GPIO       19
#define SPI_SCLK_GPIO       18

#define SPI_CLOCK_HZ        1000000

static const char *TAG = "spi_test";

static spi_device_handle_t spi_device = NULL;


esp_err_t spi_test_init(void)
{
    if (spi_device != NULL)
    {
        return ESP_OK;
    }

    spi_bus_config_t bus_config = {
        .mosi_io_num = SPI_MOSI_GPIO,
        .miso_io_num = SPI_MISO_GPIO,
        .sclk_io_num = SPI_SCLK_GPIO,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 32,
    };

    esp_err_t result = spi_bus_initialize(
        SPI_HOST_USED,
        &bus_config,
        SPI_DMA_DISABLED
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "Failed to initialize SPI bus: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    spi_device_interface_config_t device_config = {
        .clock_speed_hz = SPI_CLOCK_HZ,
        .mode = 0,
        .spics_io_num = -1,
        .queue_size = 1,
    };

    result = spi_bus_add_device(
        SPI_HOST_USED,
        &device_config,
        &spi_device
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "Failed to add SPI device: %s",
            esp_err_to_name(result)
        );

        spi_bus_free(SPI_HOST_USED);

        return result;
    }

    ESP_LOGI(
        TAG,
        "SPI master initialized: MOSI=%d MISO=%d SCLK=%d",
        SPI_MOSI_GPIO,
        SPI_MISO_GPIO,
        SPI_SCLK_GPIO
    );

    return ESP_OK;
}


esp_err_t spi_test_loopback(void)
{
    if (spi_device == NULL)
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

    spi_transaction_t transaction = {
        .length = sizeof(tx_data) * 8,
        .tx_buffer = tx_data,
        .rx_buffer = rx_data,
    };

    esp_err_t result = spi_device_transmit(
        spi_device,
        &transaction
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "SPI transaction failed: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    if (memcmp(tx_data, rx_data, sizeof(tx_data)) != 0)
    {
        ESP_LOGE(TAG, "SPI loopback data mismatch");

        return ESP_FAIL;
    }

    ESP_LOGI(
        TAG,
        "SPI loopback passed: %u bytes verified",
        (unsigned int)sizeof(tx_data)
    );

    return ESP_OK;
}