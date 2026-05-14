"""
Seed Meridian Aurora: trip packages (with embeddings), travelers, profiles, preferences.
"""
import json
import os
import uuid

import boto3
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track
from rich.table import Table

from travel_catalog import (
    TRIP_PACKAGES,
    TRAVELERS,
    TRAVELER_PROFILES,
    TRAVELER_PREFERENCES,
    DEMO_TRAVELER_ID,
)

load_dotenv()
console = Console()

EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL", "global.cohere.embed-v4")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-west-2")
AURORA_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
CLUSTER_ARN = os.getenv("AURORA_CLUSTER_ARN")
SECRET_ARN = os.getenv("AURORA_SECRET_ARN")
DATABASE = os.getenv("AURORA_DATABASE", "meridian")


def bedrock():
    return boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)


def rds():
    return boto3.client("rds-data", region_name=AURORA_REGION)


def run_sql(sql: str, parameters=None):
    kwargs = dict(
        resourceArn=CLUSTER_ARN,
        secretArn=SECRET_ARN,
        database=DATABASE,
        sql=sql,
    )
    if parameters:
        kwargs["parameters"] = parameters
    return rds().execute_statement(**kwargs)


def embed(client, text: str) -> list[float]:
    body = {
        "texts": [text],
        "input_type": "search_document",
        "embedding_types": ["float"],
        "truncate": "RIGHT",
        "output_dimension": EMBEDDING_DIMENSION,
    }
    resp = client.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )
    return json.loads(resp["body"].read())["embeddings"]["float"][0]


def package_text(pkg: dict) -> str:
    return ". ".join([
        pkg["name"],
        pkg["description"],
        f"Trip type: {pkg['trip_type']}",
        f"Destination: {pkg['destination']}, {pkg['region']}",
        f"Operator: {pkg['operator']}",
        f"Durations: {', '.join(pkg['durations'])}",
    ])


def clear_data():
    for sql in [
        "DELETE FROM booking_lines",
        "DELETE FROM bookings",
        "DELETE FROM trip_interactions",
        "DELETE FROM conversation_messages",
        "DELETE FROM conversations",
        "DELETE FROM traveler_preferences",
        "DELETE FROM traveler_profiles",
        "DELETE FROM travelers",
        "DELETE FROM trip_packages",
    ]:
        try:
            run_sql(sql)
        except Exception:
            pass


def seed_packages(bedrock_client):
    ok = 0
    for pkg in track(TRIP_PACKAGES, description="Packages"):
        vec = embed(bedrock_client, package_text(pkg))
        vec_str = "[" + ",".join(str(x) for x in vec) + "]"
        run_sql(
            """
            INSERT INTO trip_packages (
                package_id, name, trip_type, destination, region,
                price_per_person, operator, description, image_url,
                durations, availability, highlights, embedding
            ) VALUES (
                :package_id, :name, :trip_type, :destination, :region,
                :price_per_person, :operator, :description, :image_url,
                :durations::jsonb, :availability::jsonb, :highlights::jsonb, :embedding::vector
            )
            ON CONFLICT (package_id) DO UPDATE SET
                name = EXCLUDED.name,
                trip_type = EXCLUDED.trip_type,
                destination = EXCLUDED.destination,
                region = EXCLUDED.region,
                price_per_person = EXCLUDED.price_per_person,
                operator = EXCLUDED.operator,
                description = EXCLUDED.description,
                image_url = EXCLUDED.image_url,
                durations = EXCLUDED.durations,
                availability = EXCLUDED.availability,
                highlights = EXCLUDED.highlights,
                embedding = EXCLUDED.embedding
            """,
            [
                {"name": "package_id", "value": {"stringValue": pkg["package_id"]}},
                {"name": "name", "value": {"stringValue": pkg["name"]}},
                {"name": "trip_type", "value": {"stringValue": pkg["trip_type"]}},
                {"name": "destination", "value": {"stringValue": pkg["destination"]}},
                {"name": "region", "value": {"stringValue": pkg["region"]}},
                {"name": "price_per_person", "value": {"doubleValue": float(pkg["price_per_person"])}},
                {"name": "operator", "value": {"stringValue": pkg["operator"]}},
                {"name": "description", "value": {"stringValue": pkg["description"]}},
                {"name": "image_url", "value": {"stringValue": pkg["image_url"]}},
                {"name": "durations", "value": {"stringValue": json.dumps(pkg["durations"])}},
                {"name": "availability", "value": {"stringValue": json.dumps(pkg["availability"])}},
                {"name": "highlights", "value": {"stringValue": json.dumps(pkg["highlights"])}},
                {"name": "embedding", "value": {"stringValue": vec_str}},
            ],
        )
        ok += 1
    return ok


def seed_travelers():
    for t in TRAVELERS:
        run_sql(
            """
            INSERT INTO travelers (traveler_id, full_name, email, home_airport)
            VALUES (:traveler_id, :full_name, :email, :home_airport)
            ON CONFLICT (traveler_id) DO UPDATE SET
                full_name = EXCLUDED.full_name,
                email = EXCLUDED.email,
                home_airport = EXCLUDED.home_airport
            """,
            [
                {"name": "traveler_id", "value": {"stringValue": t["traveler_id"]}},
                {"name": "full_name", "value": {"stringValue": t["full_name"]}},
                {"name": "email", "value": {"stringValue": t["email"]}},
                {"name": "home_airport", "value": {"stringValue": t["home_airport"]}},
            ],
        )
    for p in TRAVELER_PROFILES:
        run_sql(
            """
            INSERT INTO traveler_profiles (
                traveler_id, party_size, budget_min, budget_max,
                preferred_cabin, seat_preference, dietary_notes, trip_goal, loyalty_programs
            ) VALUES (
                :traveler_id, :party_size, :budget_min, :budget_max,
                :preferred_cabin, :seat_preference, :dietary_notes, :trip_goal, :loyalty_programs::jsonb
            )
            ON CONFLICT (traveler_id) DO UPDATE SET
                party_size = EXCLUDED.party_size,
                budget_min = EXCLUDED.budget_min,
                budget_max = EXCLUDED.budget_max,
                preferred_cabin = EXCLUDED.preferred_cabin,
                seat_preference = EXCLUDED.seat_preference,
                dietary_notes = EXCLUDED.dietary_notes,
                trip_goal = EXCLUDED.trip_goal,
                loyalty_programs = EXCLUDED.loyalty_programs,
                updated_at = CURRENT_TIMESTAMP
            """,
            [
                {"name": "traveler_id", "value": {"stringValue": p["traveler_id"]}},
                {"name": "party_size", "value": {"longValue": p["party_size"]}},
                {"name": "budget_min", "value": {"doubleValue": float(p["budget_min"])}},
                {"name": "budget_max", "value": {"doubleValue": float(p["budget_max"])}},
                {"name": "preferred_cabin", "value": {"stringValue": p["preferred_cabin"]}},
                {"name": "seat_preference", "value": {"stringValue": p["seat_preference"]}},
                {"name": "dietary_notes", "value": {"stringValue": p["dietary_notes"]}},
                {"name": "trip_goal", "value": {"stringValue": p["trip_goal"]}},
                {"name": "loyalty_programs", "value": {"stringValue": json.dumps(p["loyalty_programs"])}},
            ],
        )
    for pref in TRAVELER_PREFERENCES:
        pref_id = f"pref_{uuid.uuid4().hex[:10]}"
        run_sql(
            """
            INSERT INTO traveler_preferences (
                preference_id, traveler_id, preference_type, preference_key,
                preference_value, confidence, signal_count, source
            ) VALUES (
                :preference_id, :traveler_id, :preference_type, :preference_key,
                :preference_value, :confidence, 1, :source
            )
            ON CONFLICT (traveler_id, preference_type, preference_key) DO UPDATE SET
                preference_value = EXCLUDED.preference_value,
                confidence = EXCLUDED.confidence,
                source = EXCLUDED.source,
                last_seen_at = CURRENT_TIMESTAMP
            """,
            [
                {"name": "preference_id", "value": {"stringValue": pref_id}},
                {"name": "traveler_id", "value": {"stringValue": DEMO_TRAVELER_ID}},
                {"name": "preference_type", "value": {"stringValue": pref["preference_type"]}},
                {"name": "preference_key", "value": {"stringValue": pref["preference_key"]}},
                {"name": "preference_value", "value": {"stringValue": pref["preference_value"]}},
                {"name": "confidence", "value": {"doubleValue": float(pref["confidence"])}},
                {"name": "source", "value": {"stringValue": pref["source"]}},
            ],
        )


def main():
    if not CLUSTER_ARN or not SECRET_ARN:
        console.print("[red]Missing Aurora credentials in .env[/red]")
        return
    console.print("[bold]Seeding Meridian travel data[/bold]")
    clear_data()
    bc = bedrock()
    n = seed_packages(bc)
    seed_travelers()
    table = Table(title="Seed summary")
    table.add_column("Entity")
    table.add_column("Count")
    table.add_row("trip_packages", str(n))
    table.add_row("travelers", str(len(TRAVELERS)))
    table.add_row("traveler_profiles", str(len(TRAVELER_PROFILES)))
    table.add_row("traveler_preferences", str(len(TRAVELER_PREFERENCES)))
    console.print(table)


if __name__ == "__main__":
    main()
