#ifndef TWAI_TEST_H
#define TWAI_TEST_H

#include "esp_err.h"

/*
 * Initialize the ESP32 TWAI controller for CAN self-test validation.
 *
 * This lab validates the on-chip TWAI/CAN controller without an
 * external CAN transceiver. Physical CAN-bus validation can be
 * added later when suitable transceiver hardware is available.
 */
esp_err_t twai_test_init(void);

/*
 * Perform a TWAI/CAN controller self-test.
 *
 * A known CAN frame is transmitted and received using the
 * controller's self-test capability. The received identifier,
 * DLC, and payload are verified against the transmitted frame.
 *
 * Returns ESP_OK when the complete frame is verified.
 */
esp_err_t twai_test_self_test(void);

#endif /* TWAI_TEST_H */