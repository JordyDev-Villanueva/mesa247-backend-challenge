"""
Event loader script for Mesa 24/7 Backend Challenge.

Loads events from events.jsonl file and sends them to the API.
"""
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any

import httpx


API_BASE_URL = "http://localhost:8000"
EVENTS_FILE = Path(__file__).parent.parent / "events" / "events.jsonl"


async def load_events() -> List[Dict[str, Any]]:
    """Load events from JSONL file."""
    events = []
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events


async def send_event(client: httpx.AsyncClient, event: Dict[str, Any]) -> Dict[str, Any]:
    """Send a single event to the API."""
    try:
        response = await client.post(
            f"{API_BASE_URL}/v1/processor/events",
            json=event,
            timeout=10.0,
        )
        return {
            "event_id": event["event_id"],
            "status_code": response.status_code,
            "success": response.status_code in [200, 201],
            "response": response.json() if response.status_code < 400 else None,
        }
    except Exception as e:
        return {
            "event_id": event["event_id"],
            "status_code": 0,
            "success": False,
            "error": str(e),
        }


async def main():
    """Main function to load and send all events."""
    print("=" * 80)
    print("Mesa 24/7 Event Loader")
    print("=" * 80)

    # Load events
    print(f"\nLoading events from: {EVENTS_FILE}")
    events = await load_events()
    print(f"Loaded {len(events)} events")

    # Send events
    print(f"\nSending events to: {API_BASE_URL}")
    print("-" * 80)

    async with httpx.AsyncClient() as client:
        # Test API connectivity
        try:
            health_response = await client.get(f"{API_BASE_URL}/health", timeout=5.0)
            if health_response.status_code != 200:
                print("ERROR: API is not healthy")
                return
            print("API is healthy")
        except Exception as e:
            print(f"ERROR: Cannot connect to API: {e}")
            print("Make sure the API is running: uvicorn app.main:app --reload")
            return

        print("\nProcessing events...")
        results = []
        for i, event in enumerate(events, 1):
            result = await send_event(client, event)
            results.append(result)

            # Print progress
            status = "OK" if result["success"] else "FAIL"
            status_code = result["status_code"]
            event_id = result["event_id"]
            print(f"[{i:3d}/{len(events)}] {status:4s} ({status_code:3d}) - {event_id}")

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful

        print(f"Total events:    {len(results)}")
        print(f"Successful:      {successful}")
        print(f"Failed:          {failed}")

        # Show 201 vs 200 breakdown
        created = sum(1 for r in results if r["status_code"] == 201)
        duplicates = sum(1 for r in results if r["status_code"] == 200)
        print(f"\nBreakdown:")
        print(f"  201 Created:   {created} (new events)")
        print(f"  200 OK:        {duplicates} (duplicates)")

        if failed > 0:
            print(f"\nFailed events:")
            for r in results:
                if not r["success"]:
                    print(f"  - {r['event_id']}: {r.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main())
