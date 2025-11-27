"""
Pydantic models for Braze API responses.
"""

from typing import Any

from pydantic import BaseModel, Field


class BrazeAPIResponse(BaseModel):
    """Base model for Braze API responses."""

    message: str = Field(description="Response message from Braze API")


class SendDataSeriesResponse(BaseModel):
    """Response model for send data series endpoint."""

    message: str
    data: list[dict[str, Any]] = Field(default_factory=list)


class CampaignResponse(BaseModel):
    """Response model for campaign operations."""

    message: str
    campaign_id: str | None = None
    dispatch_id: str | None = None


class CanvasResponse(BaseModel):
    """Response model for canvas operations."""

    message: str
    canvas_id: str | None = None


class UserTrackResponse(BaseModel):
    """Response model for user tracking operations."""

    message: str
    attributes_processed: int | None = None
    events_processed: int | None = None
    purchases_processed: int | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)


class CatalogResponse(BaseModel):
    """Response model for catalog operations."""

    message: str
    items_created: int | None = None
    items_updated: int | None = None
    items_deleted: int | None = None

