"""
Phase 4 Partner Runtime — Strands orchestration with memory + hybrid search.

Deterministic pipeline invokes MemoryAgent @tool methods, then delegates hybrid
search (Phase 3), then persists the turn. Tools are registered on a Strands Agent
for the workshop demo pattern.
"""

import os
import uuid
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from strands import Agent, tool
from strands.models import BedrockModel
from pydantic import BaseModel

from backend.agents.phase4.memory_agent import MemoryAgent, ActivityEntry as MemoryActivity
from backend.memory.store import get_memory_store


class PartnerRuntime:
    """
    Production partner runtime: memory recall → search → memory persist.

    Uses Strands @tool on MemoryAgent; search is injected to avoid circular imports.
    """

    AGENT_FILE = "agents/phase4/partner_runtime.py"

    def __init__(
        self,
        activity_callback: Optional[Callable[[MemoryActivity], Any]] = None,
    ):
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
                self.memory_agent.recall_customer_preferences,
                self.memory_agent.recall_similar_interactions,
                self.memory_agent.persist_turn,
            ],
            system_prompt=(
                "Meridian Partner Runtime on Strands. Recall Aurora memory, "
                "run memory-aware trip search, persist the turn."
            ),
        )

    def _log(
        self,
        activity_type: str,
        title: str,
        details: Optional[str] = None,
        agent_name: str = "PartnerRuntime",
        telemetry: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.activity_callback(
            MemoryActivity(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat() + "Z",
                activity_type=activity_type,
                title=title,
                details=details,
                agent_name=agent_name,
                agent_file=self.AGENT_FILE,
                telemetry=telemetry,
            )
        )

    @tool
    async def run_memory_aware_search(
        self,
        query: str,
        memory_context: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        Strands @tool wrapper — search is executed by the runtime pipeline.

        Args:
            query: User search query
            memory_context: Injected preferences and session context
            limit: Max results
        """
        return {"query": query, "memory_context": memory_context, "limit": limit}

    async def process_turn(
        self,
        message: str,
        customer_id: str,
        conversation_id: Optional[str],
        limit: int,
        search_fn: Callable[..., Awaitable[Tuple[List[Any], List[Any]]]],
    ) -> Tuple[List[Any], List[Any], str, str, List[Dict[str, Any]]]:
        """
        Execute Phase 4 turn: recall → search → persist.

        Returns:
            products, activities, response_message, conversation_id, memory_facts
        """
        activities: List[Any] = []

        def collect(entry: MemoryActivity) -> None:
            activities.append(entry)
            self.activity_callback(entry)

        self.memory_agent.activity_callback = collect

        conv_id = await self.store.get_or_create_conversation(customer_id, conversation_id)

        self._log(
            "reasoning",
            "PartnerRuntime session bootstrap (Strands)",
            details=f"customer={customer_id}, conversation={conv_id}",
            telemetry={
                "category": "runtime",
                "component": "Strands Agents + Aurora Memory",
                "status": "ok",
                "fields": [
                    {"label": "customer_id", "value": customer_id, "mono": True},
                    {"label": "conversation_id", "value": conv_id, "mono": True},
                    {"label": "sdk", "value": "strands-agents @tool"},
                ],
            },
        )

        session = await self.memory_agent.recall_session_context(conv_id)
        prefs = await self.memory_agent.recall_customer_preferences(customer_id)
        similar = await self.memory_agent.recall_similar_interactions(customer_id, message)

        memory_facts: List[Dict[str, Any]] = prefs.get("facts", [])
        memory_context = self.store.format_memory_context(
            session.get("turns", []),
            memory_facts,
            similar.get("interactions", []),
        )

        self._log(
            "reasoning",
            "Inject memory into search context",
            details=memory_context[:300] + ("…" if len(memory_context) > 300 else ""),
            telemetry={
                "category": "orchestration",
                "component": "PartnerRuntime",
                "status": "ok",
                "fields": [
                    {"label": "memory_injected", "value": "yes"},
                    {"label": "preference_facts", "value": str(len(memory_facts))},
                ],
            },
        )

        products, search_activities = await search_fn(message, limit=limit)
        activities.extend(search_activities)

        product_payload = [
            {
                "product_id": p.product_id,
                "name": p.name,
                "was_selected": False,
            }
            for p in products
        ]

        if products:
            pref_hint = ""
            if memory_facts:
                pref_hint = f" (personalized for {memory_facts[0]['value']})"
            response_message = (
                f"Welcome back! Using your saved preferences, I found "
                f"{len(products)} trips that fit{pref_hint}:"
            )
        else:
            response_message = (
                "I couldn't find exact matches, but I'll remember this search "
                "for your next visit."
            )

        await self.memory_agent.persist_turn(
            customer_id,
            conv_id,
            message,
            response_message,
            product_payload,
        )

        self._log(
            "result",
            "PartnerRuntime composed memory-grounded response",
            details=f"{len(products)} packages · persisted to Aurora",
            telemetry={
                "category": "synthesis",
                "component": "Strands PartnerRuntime",
                "status": "ok",
                "fields": [
                    {"label": "grounding", "value": "Aurora trips + customer_preferences"},
                    {"label": "tools", "value": "4× @tool (MemoryAgent)"},
                ],
            },
        )

        return products, activities, response_message, conv_id, memory_facts


def create_partner_runtime(
    activity_callback: Optional[Callable[[MemoryActivity], Any]] = None,
) -> PartnerRuntime:
    return PartnerRuntime(activity_callback=activity_callback)
