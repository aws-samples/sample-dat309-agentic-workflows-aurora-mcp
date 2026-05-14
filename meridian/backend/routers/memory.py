"""Memory API — long-term preferences from Aurora."""

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.memory.store import DEMO_TRAVELER_ID, get_memory_store

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemoryFactResponse(BaseModel):
    key: str
    value: str
    source: Optional[str] = None
    confidence: Optional[float] = None


class MemoryProfileResponse(BaseModel):
    traveler_id: str
    facts: List[MemoryFactResponse]
    profile: Optional[dict] = None


@router.get("/{traveler_id}", response_model=MemoryProfileResponse)
async def get_memory_profile(traveler_id: str = DEMO_TRAVELER_ID) -> MemoryProfileResponse:
    store = get_memory_store()
    facts = await store.recall_preferences(traveler_id)
    profile = await store.recall_profile(traveler_id)
    return MemoryProfileResponse(
        traveler_id=traveler_id,
        facts=[
            MemoryFactResponse(
                key=f["key"],
                value=f["value"],
                source=f.get("source"),
                confidence=f.get("confidence"),
            )
            for f in facts
        ],
        profile=profile,
    )
