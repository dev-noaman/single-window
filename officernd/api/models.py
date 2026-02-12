"""
Data models and endpoint definitions for OfficeRnD API Tester.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class HttpMethod(Enum):
    """Supported HTTP methods."""
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()


class ActionType(Enum):
    """API action types."""
    GET_LIST = auto()
    GET_ONE = auto()
    POST_DRY = auto()
    POST_WRITE = auto()


@dataclass
class ApiEndpoint:
    """Represents a single API endpoint configuration."""
    
    resource: str
    actions: List[ActionType]
    description: Optional[str] = None
    requires_id: bool = False
    write_payload: Optional[Dict[str, Any]] = None
    optional: bool = False
    query_params: Optional[Dict[str, Any]] = None

    @property
    def path(self) -> str:
        return self.resource


@dataclass
class EndpointGroup:
    """Group of related endpoints."""
    
    name: str
    endpoints: List[ApiEndpoint]


@dataclass
class ApiResponse:
    """Represents an API response."""
    
    status_code: int
    payload: Any
    error: Optional[str] = None
    url: str = ""
    method: str = "GET"

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 400

    @property
    def is_error(self) -> bool:
        return self.status_code >= 400 or self.error is not None


@dataclass
class EndpointResult:
    """Result of testing an endpoint."""
    
    endpoint: ApiEndpoint
    list_response: Optional[ApiResponse] = None
    single_response: Optional[ApiResponse] = None
    write_response: Optional[ApiResponse] = None
    first_item_id: Optional[str] = None
    inferred_fields: List[str] = field(default_factory=list)


# Endpoint Definitions
ENDPOINT_GROUPS: List[EndpointGroup] = [
    EndpointGroup(
        name="Community API",
        endpoints=[
            ApiEndpoint("members", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("companies", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("visitors", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("opportunities", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("passes", [ActionType.GET_LIST, ActionType.GET_ONE]),
        ]
    ),
    EndpointGroup(
        name="Space API",
        endpoints=[
            ApiEndpoint("resources", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("resource-types", [ActionType.GET_LIST]),
            ApiEndpoint("bookings", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("bookings/occurrences", [ActionType.GET_LIST], query_params={"seriesStart": "2024-01-01", "seriesEnd": "2024-12-31"}),
            ApiEndpoint("assignments", [ActionType.GET_LIST], query_params={"resource": "5b39bfde5a8a1b1500f989dc"}),
            ApiEndpoint("locations", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("floors", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("amenities", [ActionType.GET_LIST, ActionType.GET_ONE]),
        ]
    ),
    EndpointGroup(
        name="Collaboration API",
        endpoints=[
            ApiEndpoint("posts", [ActionType.GET_LIST]),
            ApiEndpoint("events", [ActionType.GET_LIST]),
            ApiEndpoint("tickets", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("ticket-options", [ActionType.GET_LIST]),
        ]
    ),
    EndpointGroup(
        name="Billing & Product API",
        endpoints=[
            ApiEndpoint("payments", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("payments/6953953d042e9fa0b51a931e/documents", [ActionType.GET_ONE]),
            ApiEndpoint("charges", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("credits", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("coins/stats", [ActionType.GET_LIST], query_params={"company": "601fce130186ac38944cb37d", "month": "2024-01"}),
            ApiEndpoint("fees", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("revenue-accounts", [ActionType.GET_LIST]),
            ApiEndpoint("tax-rates", [ActionType.GET_LIST]),
            ApiEndpoint("memberships", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("plans", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("resource-rates", [ActionType.GET_LIST]),
            ApiEndpoint("contracts", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("benefits", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("payment-details", [ActionType.GET_LIST]),
        ]
    ),
    EndpointGroup(
        name="Visits & Check-ins",
        endpoints=[
            ApiEndpoint("visits", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("checkins", [ActionType.GET_LIST, ActionType.GET_ONE]),
        ]
    ),
    EndpointGroup(
        name="Webhooks & Settings",
        endpoints=[
            ApiEndpoint("webhooks", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("checkout", [ActionType.POST_DRY]),
            ApiEndpoint("billing-settings", [ActionType.GET_LIST]),
            ApiEndpoint("business-hours", [ActionType.GET_LIST]),
            ApiEndpoint("custom-properties", [ActionType.GET_LIST]),
            ApiEndpoint("opportunity-statuses", [ActionType.GET_LIST]),
            ApiEndpoint("reception-flows", [ActionType.GET_LIST]),
            ApiEndpoint("secondary-currencies", [ActionType.GET_LIST, ActionType.GET_ONE]),
            ApiEndpoint("organizations", [ActionType.GET_LIST]),
        ]
    ),
]
