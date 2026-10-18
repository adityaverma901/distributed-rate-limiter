# test_race_condition.py
import asyncio
import httpx

URL = "http://127.0.0.1:8000/ping"
NUM_REQUESTS = 20

async def send_request(client, results):
    response = await client.get(URL)
    results.append(response.status_code)

async def main():
    results = []
    async with httpx.AsyncClient() as client:
        # Sabhi requests ek saath, bilkul parallel mein fire karo
        tasks = [send_request(client, results) for _ in range(NUM_REQUESTS)]
        await asyncio.gather(*tasks)

    allowed = results.count(200)
    denied = results.count(429)
    print(f"Total requests: {NUM_REQUESTS}")
    print(f"Allowed (200): {allowed}")
    print(f"Denied (429): {denied}")

if __name__ == "__main__":
    asyncio.run(main())