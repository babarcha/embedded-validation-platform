# Embedded DUT Validation Requirements

## VAL-001 — Communication

The DUT shall respond to a connectivity request.

Test method:
Send a PING request to the DUT.

Pass criterion:
The DUT responds successfully.

## VAL-002 — Device Identification

The DUT shall provide identification information.

Required information:
- model
- firmware version

Pass criterion:
Both fields are present and non-empty.

## VAL-003 — Temperature Measurement

The DUT shall provide a numeric temperature measurement.

Initial validation range:
- minimum: -10 °C
- maximum: 60 °C

Pass criterion:
The returned temperature is numeric and lies within the configured limits.

Note:
The range is a demonstration validation limit for this project, not a product specification.

## VAL-004 — Invalid Command Robustness

The DUT shall reject unsupported commands without becoming unresponsive.

Test method:
1. Send an unsupported command.
2. Verify an error response.
3. Send PING.

Pass criterion:
The unsupported command is rejected and the DUT still responds to PING.