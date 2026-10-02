idf_component_register(
    SRCS
        "esp32_validation_dut.c"
        "command_handler.c"
        "i2c_test.c"
    INCLUDE_DIRS "."
    REQUIRES driver
)