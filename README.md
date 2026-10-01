# Embedded Validation Platform

A Python-based validation platform for testing an embedded ESP32 device using both a simulator and a physical hardware-in-the-loop (HIL) setup.

The project demonstrates device abstraction, serial communication, pytest-based validation, failure injection, CI automation, and structured test reporting.

## Architecture

```text
                    pytest
                      │
          ┌───────────┴───────────┐
          │                       │
       Unit tests              HIL tests
          │                       │
   Fake serial devices      Device interface
                              │
                    ┌─────────┴─────────┐
                    │                   │
                Simulator          SerialDevice
                                        │
                                      UART
                                        │
                                      ESP32