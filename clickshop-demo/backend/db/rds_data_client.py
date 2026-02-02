"""
RDS Data API Client for ClickShop.

Provides database access through AWS RDS Data API for Aurora Serverless v2.
This is used when the cluster is in a private VPC and not directly accessible.
"""

import os
import json
from typing import Optional, List, Any, Dict
from decimal import Decimal

import boto3


class RDSDataClient:
    """
    RDS Data API client for Aurora PostgreSQL.
    
    Uses the RDS Data API to execute SQL statements against Aurora Serverless v2
    clusters that are not directly accessible (e.g., in private VPCs).
    """
    
    def __init__(
        self,
        cluster_arn: Optional[str] = None,
        secret_arn: Optional[str] = None,
        database: Optional[str] = None,
        region: Optional[str] = None
    ):
        """
        Initialize RDS Data API client.
        
        Args:
            cluster_arn: Aurora cluster ARN (defaults to AURORA_CLUSTER_ARN env var)
            secret_arn: Secrets Manager ARN (defaults to AURORA_SECRET_ARN env var)
            database: Database name (defaults to AURORA_DATABASE env var)
            region: AWS region (defaults to AWS_DEFAULT_REGION env var)
        """
        self.cluster_arn = cluster_arn or os.getenv("AURORA_CLUSTER_ARN")
        self.secret_arn = secret_arn or os.getenv("AURORA_SECRET_ARN")
        self.database = database or os.getenv("AURORA_DATABASE", "clickshop")
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        self.client = boto3.client('rds-data', region_name=self.region)
    
    def _format_parameters(self, params: Optional[tuple]) -> List[Dict]:
        """Convert tuple parameters to RDS Data API format."""
        if not params:
            return []
        
        formatted = []
        for i, value in enumerate(params):
            param = {"name": f"p{i}"}
            
            if value is None:
                param["value"] = {"isNull": True}
            elif isinstance(value, bool):
                param["value"] = {"booleanValue": value}
            elif isinstance(value, int):
                param["value"] = {"longValue": value}
            elif isinstance(value, float):
                param["value"] = {"doubleValue": value}
            elif isinstance(value, Decimal):
                param["value"] = {"stringValue": str(value)}
                param["typeHint"] = "DECIMAL"
            elif isinstance(value, (list, dict)):
                param["value"] = {"stringValue": json.dumps(value)}
            else:
                param["value"] = {"stringValue": str(value)}
            
            formatted.append(param)
        
        return formatted
    
    def _convert_sql_placeholders(self, sql: str, param_count: int) -> str:
        """Convert %s placeholders to :pN named parameters."""
        result = sql
        for i in range(param_count):
            result = result.replace("%s", f":p{i}", 1)
        return result
    
    def _parse_value(self, field: Dict) -> Any:
        """Parse a single field value from RDS Data API response."""
        if "isNull" in field and field["isNull"]:
            return None
        if "stringValue" in field:
            return field["stringValue"]
        if "longValue" in field:
            return field["longValue"]
        if "doubleValue" in field:
            return field["doubleValue"]
        if "booleanValue" in field:
            return field["booleanValue"]
        if "arrayValue" in field:
            return self._parse_array(field["arrayValue"])
        return None
    
    def _parse_array(self, array_value: Dict) -> List:
        """Parse array value from RDS Data API response."""
        if "stringValues" in array_value:
            return array_value["stringValues"]
        if "longValues" in array_value:
            return array_value["longValues"]
        if "doubleValues" in array_value:
            return array_value["doubleValues"]
        if "booleanValues" in array_value:
            return array_value["booleanValues"]
        if "arrayValues" in array_value:
            return [self._parse_array(v) for v in array_value["arrayValues"]]
        return []
    
    def _parse_response(self, response: Dict, column_names: List[str]) -> List[Dict]:
        """Parse RDS Data API response into list of dictionaries."""
        records = response.get("records", [])
        results = []
        
        for record in records:
            row = {}
            for i, field in enumerate(record):
                if i < len(column_names):
                    value = self._parse_value(field)
                    # Try to parse JSON strings for JSONB columns
                    if isinstance(value, str) and column_names[i] in ['inventory', 'available_sizes']:
                        try:
                            value = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            pass
                    row[column_names[i]] = value
            results.append(row)
        
        return results
    
    async def execute(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> List[Dict]:
        """
        Execute a query and return results.
        
        Args:
            query: SQL query string with %s placeholders
            params: Optional query parameters
            
        Returns:
            List of result rows as dictionaries
        """
        # Convert placeholders
        param_count = query.count("%s")
        sql = self._convert_sql_placeholders(query, param_count)
        parameters = self._format_parameters(params)
        
        response = self.client.execute_statement(
            resourceArn=self.cluster_arn,
            secretArn=self.secret_arn,
            database=self.database,
            sql=sql,
            parameters=parameters,
            includeResultMetadata=True
        )
        
        # Extract column names from metadata
        column_metadata = response.get("columnMetadata", [])
        column_names = [col.get("name", f"col{i}") for i, col in enumerate(column_metadata)]
        
        return self._parse_response(response, column_names)
    
    async def execute_one(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> Optional[Dict]:
        """
        Execute a query and return a single result.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Single result row as dictionary, or None
        """
        results = await self.execute(query, params)
        return results[0] if results else None


# Global client instance
_client: Optional[RDSDataClient] = None


def get_rds_data_client() -> RDSDataClient:
    """Get or create the global RDS Data API client instance."""
    global _client
    if _client is None:
        _client = RDSDataClient()
    return _client
