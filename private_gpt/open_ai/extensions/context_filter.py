from pydantic import BaseModel, Field


class ContextFilter(BaseModel):
    docs_ids: list[str] | None = Field(
        examples=[["c202d5e6-7b69-4869-81cc-dd574ee8ee11"]]
    )
    tags: set[str] | None = Field(examples=["CHARACTER_ART", "SCI-FI"])
