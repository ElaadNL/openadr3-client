# SPDX-FileCopyrightText: Contributors to openadr3-client <https://github.com/ElaadNL/openadr3-client>
#
# SPDX-License-Identifier: Apache-2.0

import contextlib
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta

from pydantic_extra_types.currency_code import ISO4217

from openadr3_client._models.common.attribute import Attribute
from openadr3_client._models.common.interval import Interval
from openadr3_client._models.common.interval_period import IntervalPeriod
from openadr3_client.oadr310._vtn.http.events import EventsHttpInterface
from openadr3_client.oadr310._vtn.http.programs import ProgramsHttpInterface
from openadr3_client.oadr310._vtn.http.reports import ReportsHttpInterface
from openadr3_client.oadr310._vtn.http.resources import ResourcesHttpInterface
from openadr3_client.oadr310._vtn.http.vens import VensHttpInterface
from openadr3_client.oadr310.models.event.event import ExistingEvent, NewEvent
from openadr3_client.oadr310.models.event.event_payload import EventPayload, EventPayloadDescriptor, EventPayloadType
from openadr3_client.oadr310.models.program.program import ExistingProgram, NewProgram
from openadr3_client.oadr310.models.report.report import ExistingReport, NewReport, ReportResource
from openadr3_client.oadr310.models.resource.resource import ExistingResource, NewResourceBlRequest
from openadr3_client.oadr310.models.unit import Unit
from openadr3_client.oadr310.models.ven.ven import ExistingVen, NewVenBlRequest, NewVenVenRequest
from tests.conftest import IntegrationTestVTNClient


@contextmanager
def ven_created_by_ven(vtn_client: IntegrationTestVTNClient, ven_name: str) -> Generator[ExistingVen, None, None]:
    """
    Helper function to create a ven in the VTN for testing purposes.

    Args:
        vtn_client (IntegrationTestVTNClient): vtn client configuration.
        ven_name (str): The ven name of the ven to create.

    Yields:
        Generator[ExistingVen, None, None]: _description_

    """
    ven_interface = VensHttpInterface(
        base_url=vtn_client.vtn_base_url,
        config=vtn_client.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.)
    )

    ven = NewVenVenRequest(
        ven_name=ven_name,
    )

    created_ven = ven_interface.create_ven(new_ven=ven)

    try:
        yield created_ven
    finally:
        # Do not fail if deletion fails, which can occur if the ven is manually deleted in a test.
        with contextlib.suppress(Exception):
            ven_interface.delete_ven_by_id(ven_id=created_ven.id)


@contextmanager
def ven_with_targets(vtn_client: IntegrationTestVTNClient, ven_name: str, client_id_of_ven: str, targets: tuple[str, ...] = ()) -> Generator[ExistingVen, None, None]:
    """
    Helper function to create a ven in the VTN for testing purposes.

    Args:
        vtn_client (IntegrationTestVTNClient): vtn client configuration.
        ven_name (str): The ven name of the ven to create.
        client_id_of_ven (str): The client ID of the ven object.
        targets (tuple[str, ...]): The targets of the ven to create, defaults to an empty tuple.

    Yields:
        Generator[ExistingVen, None, None]: _description_

    """
    ven_interface = VensHttpInterface(
        base_url=vtn_client.vtn_base_url,
        config=vtn_client.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.)
    )

    ven = NewVenBlRequest(
        ven_name=ven_name,
        targets=targets,
        clientID=client_id_of_ven,
    )

    created_ven = ven_interface.create_ven(new_ven=ven)

    try:
        yield created_ven
    finally:
        # Do not fail if deletion fails, which can occur if the ven is manually deleted in a test.
        with contextlib.suppress(Exception):
            ven_interface.delete_ven_by_id(ven_id=created_ven.id)


@contextmanager
def resource_for_ven(
    vtn_client: IntegrationTestVTNClient,
    ven_id: str,
    resource_name: str,
    client_id_of_resource: str,
    attributes: tuple[Attribute, ...] | None = None,
    targets: tuple[str, ...] | None = None,
) -> Generator[ExistingResource, None, None]:
    """
    Helper function to create a resource in the VTN for testing purposes.

    Args:
        vtn_client (IntegrationTestVTNClient): VTN client configuration.
        ven_id (str): The identifier of the ven the resource belongs to.
        resource_name (str): The name of the resource to create.
        client_id_of_resource (str): The client ID associated with the resource.
        attributes (tuple[Attribute, ...] | None): Attributes to set on the resource.
        targets (tuple[str, ...] | None): Targets to set on the resource.

    """
    interface = ResourcesHttpInterface(
        base_url=vtn_client.vtn_base_url,
        config=vtn_client.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    resource = NewResourceBlRequest(
        resource_name=resource_name,
        venID=ven_id,
        attributes=attributes,
        clientID=client_id_of_resource,
        targets=targets,
    )

    created_resource = interface.create_resource(new_resource=resource)

    try:
        yield created_resource
    finally:
        # Do not fail if deletion fails, which can occur if the resource is manually deleted in a test.
        with contextlib.suppress(Exception):
            interface.delete_resource_by_id(resource_id=created_resource.id)


@contextmanager
def new_program(vtn_client: IntegrationTestVTNClient, program_name: str, targets: tuple[str, ...] = ()) -> Generator[ExistingProgram, None, None]:
    """
    Helper function to create a program in the VTN for testing purposes.

    Args:
        vtn_client (IntegrationTestVTNClient): The VTN client to use.
        program_name (str): The name of the program to create.
        targets (tuple[str, ...]): Targets for the program.

    """
    program_interface = ProgramsHttpInterface(
        base_url=vtn_client.vtn_base_url,
        config=vtn_client.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )
    program = NewProgram(
        program_name=program_name,
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
            randomize_start=timedelta(seconds=0),
        ),
        targets=targets,
        payload_descriptors=(EventPayloadDescriptor(payload_type=EventPayloadType.SIMPLE, units=Unit.KWH, currency=ISO4217("EUR")),),
    )
    created_program = program_interface.create_program(new_program=program)

    try:
        yield created_program
    finally:
        # Do not fail if deletion fails, which can occur if the program is manually deleted in a test.
        with contextlib.suppress(Exception):
            program_interface.delete_program_by_id(program_id=created_program.id)


@contextmanager
def event_in_program_with_targets(
    vtn_client: IntegrationTestVTNClient,
    program: ExistingProgram,
    intervals: tuple[Interval[EventPayload], ...] | None,
    targets: tuple[str, ...] = (),
    event_name: str | None = None,
) -> Generator[ExistingEvent, None, None]:
    """
    Creates an event in the VTN for testing purposes.

    Args:
        vtn_client (IntegrationTestVTNClient): The VTN client to use.
        program (ExistingProgram): Program to create event in.
        intervals (tuple[Interval[EventPayload], ...] | None): Intervals for the event. If None, no intervals are set.
        targets (tuple[str, ...]): Targets for the event.
        event_name (str | None): Optional name for the event.

    """
    interface = EventsHttpInterface(
        base_url=vtn_client.vtn_base_url,
        config=vtn_client.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    event = NewEvent(
        programID=program.id,
        event_name=event_name,
        priority=None,
        targets=targets,
        payload_descriptors=(),
        interval_period=IntervalPeriod(
            start=datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
            duration=timedelta(minutes=5),
            randomize_start=timedelta(seconds=0),
        ),
        intervals=intervals,
        duration=timedelta(seconds=0),
    )
    created_event = interface.create_event(new_event=event)

    try:
        yield created_event
    finally:
        # Do not fail if deletion fails, which can occur if the event is manually deleted in a test.
        with contextlib.suppress(Exception):
            interface.delete_event_by_id(event_id=created_event.id)


@contextmanager
def report_from_ven_in_program(
    vtn_client: IntegrationTestVTNClient,
    ven: ExistingVen,
    event: ExistingEvent,
    resources: tuple[ReportResource, ...],
) -> Generator[ExistingReport, None, None]:
    """
    Generates a report in a program from a specific VEN.

    Args:
        vtn_client (IntegrationTestVTNClient): The VTN client to use.
        program (ExistingProgram): Program to create report for.
        ven (ExistingVen): The VEN to create the report for.
        event (ExistingEvent): The event to create the report for.
        resources (tuple[ReportResource, ...], optional): The resources inside the report. Defaults to ().

    """
    interface = ReportsHttpInterface(
        base_url=vtn_client.vtn_base_url,
        config=vtn_client.config,
        verify_tls_certificate=False,  # Self signed certificate used in integration tests.
    )

    report = NewReport(
        eventID=event.id,
        client_name=ven.ven_name,
        resources=resources,
    )

    created_report = interface.create_report(new_report=report)

    try:
        yield created_report
    finally:
        # Do not fail if deletion fails, which can occur if the report is manually deleted in a test.
        with contextlib.suppress(Exception):
            interface.delete_report_by_id(report_id=created_report.id)
