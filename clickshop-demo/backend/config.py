"""
Configuration settings for ClickShop backend.

Centralizes all configurable values that were previously hardcoded.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SearchConfig:
    """Search-related configuration."""

    # Default result limit
    default_limit: int = 5

    # Hybrid search weights (Phase 3)
    semantic_weight: float = 0.7
    lexical_weight: float = 0.3

    # Category keyword mappings for Phase 1/2 search
    # Only exact category names or very specific keywords should match
    # Semantic queries like "help with muscle recovery" should NOT match
    category_keywords: Dict[str, str | None] = field(default_factory=lambda: {
        "running shoes": "Running Shoes",
        "training shoes": "Training Shoes",
        "gym shoes": "Training Shoes",
        "fitness equipment": "Fitness Equipment",
        "fitness gear": "Fitness Equipment",
        "apparel": "Apparel",
        "clothes": "Apparel",
        "clothing": "Apparel",
        "accessories": "Accessories",
        "recovery products": "Recovery",
        "recovery gear": "Recovery",
        "foam roller": "Recovery",
        "massage gun": "Recovery",
    })


@dataclass
class OrderConfig:
    """Order processing configuration."""

    # Tax rate (8% = 0.08)
    tax_rate: float = 0.08

    # Shipping fee when below threshold
    shipping_fee: float = 5.99

    # Free shipping threshold
    free_shipping_threshold: float = 50.0

    # Delivery estimate range (business days)
    min_delivery_days: int = 3
    max_delivery_days: int = 5


@dataclass
class UploadConfig:
    """File upload configuration."""

    # Maximum image size in bytes (5MB)
    max_image_size: int = 5 * 1024 * 1024

    # Allowed image MIME types
    allowed_image_types: List[str] = field(default_factory=lambda: [
        "image/jpeg",
        "image/png",
        "image/webp",
    ])


@dataclass
class AgentConfig:
    """Agent configuration by phase."""

    # Agent names and files for each phase
    search_agents: Dict[int, tuple] = field(default_factory=lambda: {
        1: ("Phase1Agent", "agents/phase1/agent.py"),
        2: ("Phase2Agent", "agents/phase2/agent.py"),
        3: ("SupervisorAgent", "agents/phase3/supervisor.py"),
    })

    order_agents: Dict[int, tuple] = field(default_factory=lambda: {
        1: ("OrderAgent", "agents/phase1/agent.py"),
        2: ("OrderAgent", "agents/phase2/agent.py"),
        3: ("OrderAgent", "agents/phase3/order_agent.py"),
    })

    # Progressive reveal delays (ms) - for demo purposes
    phase_delays: Dict[int, int] = field(default_factory=lambda: {
        1: 600,  # Slower to show process
        2: 450,
        3: 350,  # Faster (more sophisticated)
    })


@dataclass
class Config:
    """Main configuration container."""

    search: SearchConfig = field(default_factory=SearchConfig)
    order: OrderConfig = field(default_factory=OrderConfig)
    upload: UploadConfig = field(default_factory=UploadConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)

    # Environment overrides
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


# Global configuration instance
config = Config()
