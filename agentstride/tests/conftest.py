"""
Pytest configuration for AgentStride tests.

Configures Hypothesis settings and shared fixtures for property-based testing.
"""
import os
import json
import pytest
from hypothesis import settings, Verbosity, Phase

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import boto3


# Configure Hypothesis default settings
settings.register_profile(
    "default",
    max_examples=100,
    verbosity=Verbosity.normal,
    phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.shrink],
    deadline=5000,  # 5 second deadline per test
)

settings.register_profile(
    "ci",
    max_examples=200,
    verbosity=Verbosity.verbose,
    deadline=10000,  # 10 second deadline for CI
)

settings.register_profile(
    "debug",
    max_examples=10,
    verbosity=Verbosity.verbose,
    deadline=None,  # No deadline for debugging
)

# Load profile from environment or use default
profile = os.getenv("HYPOTHESIS_PROFILE", "default")
settings.load_profile(profile)


@pytest.fixture(scope="session")
def rds_data_client():
    """
    Session-scoped RDS Data API client fixture.
    
    Provides a reusable client for tests that need database access.
    """
    try:
        client = boto3.client(
            'rds-data',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        yield client
    except Exception as e:
        pytest.skip(f"RDS Data API client not available: {e}")


@pytest.fixture(scope="session")
def db_config():
    """Database configuration for RDS Data API."""
    return {
        'cluster_arn': os.getenv('AURORA_CLUSTER_ARN'),
        'secret_arn': os.getenv('AURORA_SECRET_ARN'),
        'database': os.getenv('AURORA_DATABASE', 'clickshop')
    }


def execute_sql(client, config, sql, params=None):
    """Helper to execute SQL via RDS Data API."""
    response = client.execute_statement(
        resourceArn=config['cluster_arn'],
        secretArn=config['secret_arn'],
        database=config['database'],
        sql=sql,
        parameters=params or [],
        includeResultMetadata=True
    )
    
    column_metadata = response.get("columnMetadata", [])
    column_names = [col.get("name", f"col{i}") for i, col in enumerate(column_metadata)]
    
    results = []
    for record in response.get("records", []):
        row = {}
        for i, field in enumerate(record):
            if i < len(column_names):
                if "isNull" in field and field["isNull"]:
                    value = None
                elif "stringValue" in field:
                    value = field["stringValue"]
                elif "longValue" in field:
                    value = field["longValue"]
                elif "doubleValue" in field:
                    value = field["doubleValue"]
                else:
                    value = None
                row[column_names[i]] = value
        results.append(row)
    
    return results


@pytest.fixture
def products_with_embeddings(rds_data_client, db_config):
    """
    Fixture providing all products with non-null embeddings.
    
    Returns:
        List of product dictionaries with embedding dimensions
    """
    results = execute_sql(
        rds_data_client,
        db_config,
        """
        SELECT 
            product_id,
            name,
            category,
            vector_dims(embedding) as embedding_dimension
        FROM products
        WHERE embedding IS NOT NULL
        """
    )
    return results


# Expected constants for tests
EXPECTED_EMBEDDING_DIMENSION = 1024  # Nova Multimodal uses 1024 dims
EXPECTED_PRODUCT_COUNT = 30
PRODUCT_CATEGORIES = [
    "Running Shoes",
    "Training Shoes", 
    "Fitness Equipment",
    "Apparel",
    "Accessories",
    "Recovery"
]
