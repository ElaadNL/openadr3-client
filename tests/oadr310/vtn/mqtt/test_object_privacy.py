"""This module validates that the object privacy of events published to the MQTT broker is enforced.

In practice, this requires the following:

1. An event to be published in the VTN with a specific target, hereafter called target-A
2. A VEN object created within the VTN with target-A in the targets array (allowing the VEN to view objects with this target).
3. A subscription to a topic of /ven/{ven_id} with the ven_id being the ID of the object in step 2.
The subscriber in the MQTT broker MUST have the same client_id as the VEN object in step 2, otherwise topic subscription MUST be rejected.
4. Only events with the targets of the VEN object in step 2 (only target-A in this case) must be published to the MQTT topic of step 3.
"""

