from __future__ import annotations

from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class OHLCVBar(BaseModel):
    """Single-bar input model; provider frames use the stricter frame contract."""

    model_config = ConfigDict(allow_inf_nan=False)

    symbol: str
    timestamp: datetime

    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        symbol = value.strip().upper()

        if not symbol:
            raise ValueError("symbol cannot be empty")

        return symbol

    def validate_price_relationships(self) -> None:
        if self.high < max(self.open, self.close, self.low):
            raise ValueError(
                "high must be greater than or equal to open, close, and low"
            )

        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be less than or equal to open, close, and high")

    @model_validator(mode="after")
    def check_price_relationships(self) -> Self:
        """Keep the public helper while enforcing relationships on construction."""
        self.validate_price_relationships()
        return self
