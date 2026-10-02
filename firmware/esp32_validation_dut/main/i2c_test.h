#ifndef I2C_TEST_H
#define I2C_TEST_H

#include "esp_err.h"

/*
 * Initialize the ESP32 I2C master used by the DUT validation interface.
 */
esp_err_t i2c_test_init(void);

/*
 * Scan the I2C bus.
 *
 * Returns the number of responding 7-bit I2C addresses.
 */
int i2c_test_scan(void);

#endif /* I2C_TEST_H */