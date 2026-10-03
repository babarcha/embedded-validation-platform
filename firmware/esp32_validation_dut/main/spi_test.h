#ifndef SPI_TEST_H
#define SPI_TEST_H

#include "esp_err.h"

/*
 * Initialize the ESP32 SPI master used by the DUT validation interface.
 */
esp_err_t spi_test_init(void);

/*
 * Perform a physical MOSI-to-MISO SPI loopback transaction.
 *
 * Returns ESP_OK when the received bytes exactly match
 * the transmitted bytes.
 */
esp_err_t spi_test_loopback(void);

#endif /* SPI_TEST_H */