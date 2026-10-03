#ifndef UART_TEST_H
#define UART_TEST_H

#include "esp_err.h"

/*
 * Initialize the secondary hardware UART used for DUT validation.
 *
 * UART0 remains the PC/DUT control interface.
 * This module uses UART2 for the physical loopback test.
 */
esp_err_t uart_test_init(void);

/*
 * Perform a physical UART TX-to-RX loopback test.
 *
 * Returns ESP_OK when the received bytes exactly match
 * the transmitted bytes.
 */
esp_err_t uart_test_loopback(void);

#endif /* UART_TEST_H */