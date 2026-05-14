"""
Phase 4 — Strands concierge orchestration with traveler memory + hybrid search.
"""

import os
import uuid
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from strands import Agent
from strands.models import BedrockModel

from backend.agents.phase4.memory_agent import MemoryAgent, ActivityEntry as MemoryActivity
from backend.memory.store import get_memory_store


class ConciergeOrchestrator:
    """Phase 4: recall traveler context → search → persist turn (Strands @tool)."""

    AGENT_FILE = "agents/phase4/concierge.py"

    def __init__(self, activity_callback: Optional[Callable[[MemoryActivity], Any]] = None):
        self.activity_callback = activity_callback or (lambda _: None)
        self.memory_agent = MemoryAgent(activity_callback=self.activity_callback)
        self.store = get_memory_store()
        self.model = BedrockModel(
            model_id="global.anthropic.claude-opus-4-7-v1",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        )
        self.agent = Agent(
            model=self.model,
            tools=[
                self.memory_agent.recall_session_context,
                self.memory_agent.recall_traveler_preferences,
                self.memory_agent.recall_similar_interactions,
                self.memory_agent.persist_turn,
            ],
            system_prompt="Meridian concierge: load traveler memory from Aurora, search trips, save the turn.",
        )

    def _log(self, activity_type: str, title: str, details: Optional[str] = None, **kwargs) -> None:
        self.activity_callback(
            MemoryActivity(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat() + "Z",
                activity_type=activity_type,
                title=title,
                details=details,
                agent_name=kwargs.get("agent_name", "ConciergeOrchestrator"),
                agent_file=self.AGENT_FILE,
                telemetry=kwargs.get("telemetry"),
            )
        )

    async def process_turn(
        self,
        message: str,
        traveler_id: str,
        conversation_id: Optional[str],
        limit: int,
        search_fn: Callable[..., Awaitable[Tuple[List[Any], List[Any]]]],
    ) -> Tuple[List[Any], List[Any], str, str, List[Dict[str, Any]]]:
        activities: List[Any] = []

        def collect(entry: MemoryActivity) -> None:
            activities.append(entry)
            self.activity_callback(entry)

        self.memory_agent.activity_callback = collect
        conv_id = await self.store.get_or_create_conversation(traveler_id, conversation_id)
        profile = await self.store.recall_profile(traveler_id)

        self._log(
            "reasoning",
            "Concierge session start (Strands)",
            details=f"traveler={traveler_id}, conversation={conv_id}",
            telemetry={
                "category": "runtime",
                "component": "Strands Agents + Aurora",
                "status": "ok",
                "fields": [
                    {"label": "traveler_id", "value": traveler_id, "mono": True},
                    {"label": "conversation_id", "value": conv_id, "mono": True},
                ],
            },
        )

        session = await self.memory_agent.recall_session_context(conv_id)
        prefs = await self.memory_agent.recall_traveler_preferences(traveler_id)
        similar = await self.memory_agent.recall_similar_interactions(traveler_id, message)
        memory_facts: List[Dict[str, Any]] = prefs.get("facts", [])
        memory_context = self.store.format_memory_context(
            profile, session.get("turns", []), memory_facts, similar.get("interactions", [])
        )

        self._log("reasoning", "Apply traveler context to search", details=memory_context[:280])

        packages, search_activities = await search_fn(message, limit=limit)
        activities.extend(search_activities)

        shown = [
            {"package_id": getattr(p, "product_id", None) or getattr(p, "package_id", ""), "name": p.name}
            for p in packages
        ]

        if packages:
            hint = f" for {memory_facts[0]['value']}" if memory_facts else ""
            response_message = f"Welcome back — here are {len(packages)} trips that fit your profile{hint}:"
        else:
            response_message = "No exact matches yet; I've saved this search to your history."

        await self.memory_agent.persist_turn(traveler_id, conv_id, message, response_message, shown)

        self._log(
            "result",
            "Memory-grounded reply ready",
            details=f"{len(packages)} packages · Aurora memory updated",
            telemetry={"category": "synthesis", "component": "ConciergeOrchestrator", "status": "ok"},
        )

        return packages, activities, response_message, conv_id, memory_facts


def create_concierge(activity_callback=None) -> ConciergeOrchestrator:
    return ConciergeOrchestrator(activity_callback=activity_callback)

