#include "i2c_test.h"

#include "driver/i2c_master.h"
#include "esp_log.h"

#define I2C_PORT              I2C_NUM_0
#define I2C_SDA_GPIO          21
#define I2C_SCL_GPIO          22
#define I2C_GLITCH_IGNORE_CNT 7

#define I2C_SCAN_START_ADDR   0x08
#define I2C_SCAN_END_ADDR     0x77
#define I2C_PROBE_TIMEOUT_MS  20

static const char *TAG = "i2c_test";

static i2c_master_bus_handle_t bus_handle = NULL;


esp_err_t i2c_test_init(void)
{
    if (bus_handle != NULL)
    {
        return ESP_OK;
    }

    i2c_master_bus_config_t bus_config = {
        .i2c_port = I2C_PORT,
        .sda_io_num = I2C_SDA_GPIO,
        .scl_io_num = I2C_SCL_GPIO,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = I2C_GLITCH_IGNORE_CNT,
        .flags.enable_internal_pullup = true,
    };

    esp_err_t result = i2c_new_master_bus(
        &bus_config,
        &bus_handle
    );

    if (result != ESP_OK)
    {
        ESP_LOGE(
            TAG,
            "Failed to initialize I2C master: %s",
            esp_err_to_name(result)
        );

        return result;
    }

    ESP_LOGI(
        TAG,
        "I2C master initialized: SDA=%d SCL=%d",
        I2C_SDA_GPIO,
        I2C_SCL_GPIO
    );

    return ESP_OK;
}


int i2c_test_scan(void)
{
    if (bus_handle == NULL)
    {
        return -1;
    }

    int device_count = 0;

    for (
        uint8_t address = I2C_SCAN_START_ADDR;
        address <= I2C_SCAN_END_ADDR;
        address++
    )
    {
        esp_err_t result = i2c_master_probe(
            bus_handle,
            address,
            I2C_PROBE_TIMEOUT_MS
        );

        if (result == ESP_OK)
        {
            ESP_LOGI(
                TAG,
                "I2C device found at address 0x%02X",
                address
            );

            device_count++;
        }
    }

    return device_count;
}