-- Meridian 2026 Refresh - Products Table Schema
-- Requirements: 1.1, 1.3, 5.1, 5.2, 5.3
--
-- This file documents the refreshed products table schema for the consumer
-- electronics/smart home domain. The schema uses:
-- - JSONB fields for flexible product specifications and compatibility data
-- - pgvector for 1024-dimensional Cohere Embed v4 embeddings
-- - Generated tsvector column for full-text search optimization
-- - HNSW index for approximate nearest neighbor vector search
-- - GIN indexes for JSONB pre-filtering during vector search
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
-- Drop existing products table for clean reinstall
DROP TABLE IF EXISTS products CASCADE;
-- Products table with Cohere Embed v4 embeddings (1024 dimensions)
-- Requirement 1.3: Fields include product_id, name, category, price, brand, description,
--   image_url, available_variants (JSONB), inventory (JSONB), specifications (JSONB),
--   compatibility (JSONB), embedding vector(1024), search_vector (generated tsvector)
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    -- Smart Home, Wearable Tech, Audio, Productivity, Gaming, Wellness
    price DECIMAL(10, 2) NOT NULL,
    brand VARCHAR(100),
    description TEXT,
    image_url VARCHAR(500),
    available_sizes JSONB,
    available_variants JSONB,
    -- Replaces available_sizes: {"colors": [...], "sizes": [...], "configs": [...]}
    inventory JSONB NOT NULL,
    -- {"variant_key": quantity, ...}
    specifications JSONB,
    -- Technical specs: {"connectivity": "WiFi 6E", "battery": "12h", ...}
    compatibility JSONB,
    -- Ecosystem: {"works_with": ["Matter", "HomeKit"], "requires": [...]}
    embedding vector(1024),
    -- Cohere Embed v4 (text + image in same space)
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector(
            'english',
            name || ' ' || COALESCE(description, '') || ' ' || COALESCE(brand, '')
        )
    ) STORED,
    -- Auto-generated for lexical search (Requirement 5.3)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- HNSW index for fast vector similarity search
-- Requirement 5.1: pgvector 0.8+ HNSW with improved recall, m=16, ef_construction=100
CREATE INDEX idx_products_embedding_hnsw ON products USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 100);
-- GIN index for full-text search on generated tsvector column
CREATE INDEX idx_products_search_vector ON products USING gin(search_vector);
-- GIN indexes for JSONB pre-filtering during vector search
-- Requirement 5.2: JSONB capabilities for querying specifications and compatibility
CREATE INDEX idx_products_specs ON products USING gin(specifications jsonb_path_ops);
CREATE INDEX idx_products_compat ON products USING gin(compatibility jsonb_path_ops);
-- B-tree indexes for category, brand, and price filtering
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_price ON products(price);
-- Semantic product search function (legacy, kept for Phase 1/2 compatibility)
-- Returns products ranked by cosine similarity to the query embedding
CREATE OR REPLACE FUNCTION semantic_product_search(
        query_embedding vector(1024),
        result_limit integer DEFAULT 5
    ) RETURNS TABLE (
        product_id varchar,
        name varchar,
        brand varchar,
        price decimal,
        description text,
        image_url varchar,
        category varchar,
        similarity float
    ) AS $$ BEGIN RETURN QUERY
SELECT p.product_id,
    p.name,
    p.brand,
    p.price,
    p.description,
    p.image_url,
    p.category,
    1 - (p.embedding <=> query_embedding) as similarity
FROM products p
WHERE p.embedding IS NOT NULL
ORDER BY p.embedding <=> query_embedding
LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;
-- Table and column documentation
COMMENT ON TABLE products IS 'Product catalog with Cohere Embed v4 vector embeddings, JSONB specs/compatibility, and generated tsvector for hybrid search';
COMMENT ON COLUMN products.embedding IS 'Vector embedding for semantic/visual product search (1024-dim Cohere Embed v4)';
COMMENT ON COLUMN products.search_vector IS 'Auto-generated tsvector from name, description, and brand for full-text search';
COMMENT ON COLUMN products.specifications IS 'Technical specifications as JSONB (connectivity, battery, audio, etc.)';
COMMENT ON COLUMN products.compatibility IS 'Ecosystem compatibility as JSONB (works_with, requires, pairs_with)';
COMMENT ON COLUMN products.available_variants IS 'Product variants as JSONB (colors, sizes, configs) - replaces available_sizes';
-- ============================================================================
-- Memory Schema (Phase 4 - Agentic Memory and Personalization)
-- Requirements: 3.1, 5.1, 5.2
--
-- These tables support Phase 4's Memory Agent which stores conversation history,
-- customer preferences, and interaction embeddings for semantic memory retrieval.
-- Aurora PostgreSQL serves as the persistent memory store, demonstrating that a
-- single database handles transactional, vector, and memory workloads.
-- ============================================================================
-- Conversation history - stores high-level conversation metadata
CREATE TABLE conversations (
    conversation_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    summary TEXT -- LLM-generated conversation summary
);
-- Individual messages with embeddings for semantic retrieval of past interactions
CREATE TABLE conversation_messages (
    message_id VARCHAR(50) PRIMARY KEY,
    conversation_id VARCHAR(50) REFERENCES conversations(conversation_id),
    role VARCHAR(20) NOT NULL,
    -- 'user' or 'assistant'
    content TEXT NOT NULL,
    embedding vector(1024),
    -- For semantic retrieval of past interactions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Customer preferences extracted by Memory Agent
-- Preference signals: brand_affinity, price_sensitivity, category_interest, feature_priority
CREATE TABLE customer_preferences (
    preference_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    preference_type VARCHAR(50) NOT NULL,
    -- 'brand_affinity', 'price_sensitivity', 'category_interest', 'feature_priority'
    preference_key VARCHAR(100) NOT NULL,
    -- e.g., "Sonos", "under_200", "smart_home", "noise_cancellation"
    confidence FLOAT DEFAULT 0.5,
    -- 0.0 to 1.0, increases with repeated signals
    signal_count INTEGER DEFAULT 1,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, preference_type, preference_key)
);
-- Interaction embeddings for semantic memory retrieval
-- Stores full interaction context with vector embeddings for finding similar past conversations
CREATE TABLE interaction_embeddings (
    interaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    conversation_id VARCHAR(50) REFERENCES conversations(conversation_id),
    query_text TEXT NOT NULL,
    response_summary TEXT,
    products_shown JSONB,
    -- [{product_id, name, was_selected}]
    embedding vector(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- B-tree indexes for memory retrieval by customer and time
CREATE INDEX idx_conversations_customer ON conversations(customer_id, last_message_at DESC);
CREATE INDEX idx_messages_conversation ON conversation_messages(conversation_id, created_at);
CREATE INDEX idx_preferences_customer ON customer_preferences(customer_id, preference_type);
CREATE INDEX idx_preferences_confidence ON customer_preferences(customer_id, confidence DESC);
CREATE INDEX idx_interactions_customer ON interaction_embeddings(customer_id, created_at DESC);
-- HNSW indexes for vector similarity search on memory embeddings
-- Requirement 5.1: pgvector HNSW with m=16, ef_construction=64 (smaller than products due to fewer rows)
CREATE INDEX idx_messages_embedding ON conversation_messages USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX idx_interactions_embedding ON interaction_embeddings USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- Memory table documentation
COMMENT ON TABLE conversations IS 'Conversation history metadata for Phase 4 agentic memory';
COMMENT ON TABLE conversation_messages IS 'Individual messages with vector embeddings for semantic retrieval';
COMMENT ON TABLE customer_preferences IS 'Customer preference signals extracted by Memory Agent (brand affinity, price sensitivity, etc.)';
COMMENT ON TABLE interaction_embeddings IS 'Full interaction embeddings for semantic memory retrieval of past conversations';
-- ============================================================================
-- Observability Tables (Agent Tracing)
-- Requirements: 8.1, 8.2, 8.4
--
-- These tables support agent observability: token usage tracking, latency
-- waterfall visualization, and cost estimation per interaction. The
-- parent_trace_id self-reference enables nested trace hierarchies for
-- multi-agent delegation tracking (e.g., Supervisor → Search Agent).
-- ============================================================================
-- Agent execution traces for observability
CREATE TABLE agent_traces (
    trace_id VARCHAR(50) PRIMARY KEY,
    parent_trace_id VARCHAR(50) REFERENCES agent_traces(trace_id),
    conversation_id VARCHAR(50),
    agent_name VARCHAR(100) NOT NULL,
    phase INTEGER NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    embedding_calls INTEGER DEFAULT 0,
    db_queries INTEGER DEFAULT 0,
    total_latency_ms INTEGER,
    estimated_cost_usd DECIMAL(10, 6),
    status VARCHAR(20) DEFAULT 'success',
    -- 'success', 'error', 'timeout'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Index for querying traces by conversation (observability dashboard)
CREATE INDEX idx_traces_conversation ON agent_traces(conversation_id, created_at);
-- Index for querying traces by phase (phase comparison and filtering)
CREATE INDEX idx_traces_phase ON agent_traces(phase, created_at DESC);
-- Observability table documentation
COMMENT ON TABLE agent_traces IS 'Agent execution traces for observability: token usage, latency, and cost tracking';
COMMENT ON COLUMN agent_traces.parent_trace_id IS 'References parent trace for nested multi-agent delegation tracking';
COMMENT ON COLUMN agent_traces.estimated_cost_usd IS 'Estimated cost based on Bedrock pricing for Claude + Cohere Embed v4';
-- =============================================================================
-- Memory Schema (Phase 4 - Agentic Memory and Personalization)
-- Requirements: 3.1, 5.1, 5.2
--
-- These tables support Phase 4's Memory Agent which stores conversation history,
-- customer preferences, and interaction embeddings for semantic memory retrieval.
-- Aurora PostgreSQL serves as the persistent memory store, demonstrating that a
-- single database handles transactional, vector, and memory workloads.
-- =============================================================================
-- Drop existing memory tables for clean reinstall
DROP TABLE IF EXISTS interaction_embeddings CASCADE;
DROP TABLE IF EXISTS conversation_messages CASCADE;
DROP TABLE IF EXISTS customer_preferences CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
-- Conversations table - stores high-level conversation metadata
-- Each conversation tracks a session between a customer and the agent system
CREATE TABLE conversations (
    conversation_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    summary TEXT -- LLM-generated conversation summary
);
-- Conversation messages table - individual messages with embeddings for semantic retrieval
-- The embedding column enables finding semantically similar past messages
CREATE TABLE conversation_messages (
    message_id VARCHAR(50) PRIMARY KEY,
    conversation_id VARCHAR(50) REFERENCES conversations(conversation_id),
    role VARCHAR(20) NOT NULL,
    -- 'user' or 'assistant'
    content TEXT NOT NULL,
    embedding vector(1024),
    -- Cohere Embed v4 for semantic retrieval of past interactions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Customer preferences table - preference signals extracted by Memory Agent
-- Tracks brand affinity, price sensitivity, category interests, feature priorities
-- The UNIQUE constraint ensures one entry per (customer, type, key) combination
CREATE TABLE customer_preferences (
    preference_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    preference_type VARCHAR(50) NOT NULL,
    -- 'brand_affinity', 'price_sensitivity', 'category_interest', 'feature_priority'
    preference_key VARCHAR(100) NOT NULL,
    -- e.g., "Sonos", "under_200", "smart_home", "noise_cancellation"
    confidence FLOAT DEFAULT 0.5,
    -- 0.0 to 1.0, increases with repeated signals
    signal_count INTEGER DEFAULT 1,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, preference_type, preference_key)
);
-- Interaction embeddings table - embeddings of full interactions for semantic memory
-- Stores the complete interaction context (query + response + products shown) with
-- a vector embedding for finding semantically similar past conversations
CREATE TABLE interaction_embeddings (
    interaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    conversation_id VARCHAR(50) REFERENCES conversations(conversation_id),
    query_text TEXT NOT NULL,
    response_summary TEXT,
    products_shown JSONB,
    -- [{product_id, name, was_selected}]
    embedding vector(1024),
    -- Cohere Embed v4 for semantic memory retrieval
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- =============================================================================
-- Memory Schema Indexes
-- =============================================================================
-- B-tree indexes for efficient memory retrieval by customer and time
CREATE INDEX idx_conversations_customer ON conversations(customer_id, last_message_at DESC);
CREATE INDEX idx_messages_conversation ON conversation_messages(conversation_id, created_at);
CREATE INDEX idx_preferences_customer ON customer_preferences(customer_id, preference_type);
CREATE INDEX idx_preferences_confidence ON customer_preferences(customer_id, confidence DESC);
CREATE INDEX idx_interactions_customer ON interaction_embeddings(customer_id, created_at DESC);
-- HNSW indexes for vector similarity search on memory embeddings
-- Requirement 5.1: pgvector HNSW indexes for semantic retrieval
-- Using m=16, ef_construction=64 (slightly lower than products since memory tables are smaller)
CREATE INDEX idx_messages_embedding ON conversation_messages USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX idx_interactions_embedding ON interaction_embeddings USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- =============================================================================
-- Memory Schema Documentation
-- =============================================================================
COMMENT ON TABLE conversations IS 'Conversation history metadata for Phase 4 agentic memory';
COMMENT ON TABLE conversation_messages IS 'Individual messages with vector embeddings for semantic retrieval';
COMMENT ON TABLE customer_preferences IS 'Customer preference signals extracted by Memory Agent (brand affinity, price sensitivity, etc.)';
COMMENT ON TABLE interaction_embeddings IS 'Full interaction embeddings for semantic memory retrieval of past conversations';