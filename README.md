# OpenADR3 Client

This library provides two main interfaces for interacting with OpenADR3 (Open Automated Demand Response) systems:

1. Business Logic (BL) Client - For VTN operators (for example, DSOs).
2. Virtual End Node (VEN) Client - For end users (for example, device operators).

## Configuration

Before using the library, you need to configure the following environment variables:

```python
OAUTH_TOKEN_ENDPOINT # The oauth token endpoint to provision access tokens from
OAUTH_CLIENT_ID      # The client ID for OAuth client credential authentication
OAUTH_CLIENT_SECRET  # The client secret for OAuth client credential authentication
OAUTH_SCOPES         # Comma-delimited list of OAuth scope to request (optional)
```

## Business Logic (BL) Client

The BL client is designed for DSOs (Distribution System Operators) and VTN operators to manage OpenADR3 programs and events. It provides full control over the following interfaces:

- **Events**: Create, read, update, and delete events
- **Programs**: Create, read, update, and delete programs
- **Reports**: Read-only access to reports
- **VENS**: Read-only access to VEN information
- **Subscriptions**: Read-only access to subscriptions

### Example BL Usage

```python
from openadr3_client.bl.factory import BusinessLogicClientFactory

# Initialize the client with the base URL of the VTN as input.
bl_client = BusinessLogicClientFactory.create_http_bl_client(base_url=...)

# Create a new program (NewProgram allows for more properties, this is just a simple example).
program = NewProgram(
        id=None, # ID cannot be set by the client, assigned by the VTN.
        program_name="Example Program",
        program_long_name="Example Program Long Name",
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 12, 30, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
            randomize_start=timedelta(minutes=5),
        ),
        payload_descriptor=(EventPayloadDescriptor(payload_type=EventPayloadType.PRICE, units="price", currency="EUR"),),
        targets=(Target(type="test-target-1", values=("test-value-1",)),),
)

created_program = bl_client.programs.create_program(new_program=program)

# Create an event inside the program
event = NewEvent(
    id=None, # ID cannot be set by the client, assigned by the VTN.
    programID=created_program.id, # ID of program is known after creation
    event_name="test-event",
    priority=999,
    targets=(Target(type="test-target-1", values=("test-value-1",)),),
    payload_descriptor=(
        EventPayloadDescriptor(payload_type=EventPayloadType.PRICE, units="price", currency="EUR"),
    ),
    # Top Level interval definition, each interval specified with the None value will inherit this
    # value by default as its interval period. In this case, each interval will have an implicit
    # duration of 5 minutes.
    interval_period=IntervalPeriod(
        start=datetime(2023, 1, 1, 12, 30, 0, tzinfo=UTC),
        duration=timedelta(minutes=5),
    ),
    intervals=(
        Interval(
            id=0,
            interval_period=None,
            payloads=(EventPayload(type=EventPayloadType.PRICE, values=(2.50,)),),
        ),
    ),
)

created_event = interface.create_event(new_event=event)

```

## Virtual End Node (VEN) Client

The VEN client is designed for end users and device operators to receive and process OpenADR3 programs and events. It provides:

- **Events**: Read-only access to events
- **Programs**: Read-only access to programs
- **Reports**: Create and manage reports
- **VENS**: Register and manage VEN information
- **Subscriptions**: Manage subscriptions to programs and events

### Example VEN Client Usage

```python
from openadr3_client.ven.factory import VirtualEndNodeClientFactory

# Initialize the client with the base URL of the VTN as input.
ven_client = VirtualEndNodeClientFactory.create_http_ven_client(base_url=...)

# Search for events inside the VTN.
events = ven_client.events.get_events(target=..., pagination=..., program_id=...)

# Process the events as needed...
```

## Data Format Conversion

The library provides convenience methods to convert between OpenADR3 event intervals and common data formats. These conversions can be used both for input (creating event intervals from a common data format) and output (processing existing event intervals to a common data format).

### Pandas DataFrame Format

The library supports conversion between event intervals and pandas DataFrames. The DataFrame format is validated using a pandera schema to ensure data integrity.

#### Pandas Input Format

When creating an event interval from a DataFrame, the input must match the following schema:

| Column Name | Type | Required | Description |
|------------|------|----------|-------------|
| type | str | Yes | The type of the event interval |
| values | list[Union[int, float, str, bool, Point]] | Yes | The payload values for the interval |
| start | datetime64[ns, UTC] | Yes | The start time of the interval (UTC timezone) |
| duration | timedelta64[ns] | Yes | The duration of the interval |
| randomize_start | timedelta64[ns] | No | The randomization window for the start time |

Important notes:

- All datetime values must be timezone-aware and in UTC
- All datetime and timedelta values must use nanosecond precision (`[ns]`)
- The id column of an event interval cannot be provided as input - the client will automatically assign incrementing integer IDs to the event intervals, in the same order as they were given.

Example DataFrame:

```python
import pandas as pd

df = pd.DataFrame({
    'type': ['SIMPLE'],
    'values': [[1.0, 2.0]],
    'start': [pd.Timestamp("2023-01-01 00:00:00.000Z").as_unit("ns")],
    'duration': [pd.Timedelta(hours=1)],
    'randomize_start': [pd.Timedelta(minutes=5)]
})
```

#### Pandas Output Format

When converting an event interval to a DataFrame, the output will match the same schema as the input format, with one addition: the event interval's `id` field will be included as the DataFrame index. The conversion process includes validation to ensure the data meets the schema requirements, including timezone and precision specifications.

### TypedDict Format

The library also supports conversion between event intervals and lists of dictionaries using a TypedDict format.

#### Dictionary Input Format

When creating an event interval from a dictionary, the input must follow the `EventIntervalDictInput` format:

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| type | str | Yes | The type of the event interval |
| values | list[Union[int, float, str, bool, Point]] | Yes | The payload values for the interval |
| start | datetime | No | The start time of the interval (must be timezone aware) |
| duration | timedelta | No | The duration of the interval |
| randomize_start | timedelta | No | The randomization window for the start time |

Important notes:

- All datetime values must be timezone-aware and in UTC
- The id field cannot be provided as input - the client will automatically assign incrementing integer IDs to the event intervals, in the same order as they were given

Example input:

```python
from datetime import datetime, timedelta, UTC

dict_iterable_input = [
    {
        # Required fields
        'type': 'SIMPLE',
        'values': [1.0, 2.0],
        
        # Optional fields
        'start': datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        'duration': timedelta(hours=1),
        'randomize_start': timedelta(minutes=15)
    },
]
```

#### Dictionary Output Format

When converting an event interval to a list of dictionaries, the output is checked against the `EventIntervalDictInput` TypedDict with type hints to ensure compliance. The output is a list of `EventIntervalDictInput` values.

## Getting Started

1. Install the package
2. Configure the required environment variables
3. Choose the appropriate client interface (BL or VEN)
4. Initialize the client with the required interfaces
5. Start interacting with the OpenADR3 VTN system.