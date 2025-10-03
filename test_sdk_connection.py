#!/usr/bin/env python3
"""
Test Claude Agent SDK connection
"""
import os
import asyncio
from dotenv import load_dotenv
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

# Load .env
load_dotenv()

async def test_connection():
    api_key = os.environ.get('ANTHROPIC_API_KEY')

    print("\n" + "="*70)
    print("Testing Claude Agent SDK Connection")
    print("="*70 + "\n")

    if not api_key:
        print("❌ No API key found!")
        return

    print(f"✅ API Key found: {api_key[:20]}... (length: {len(api_key)})")

    try:
        print("\n🔄 Attempting to create SDK client...")

        # SDK auto-detects API key from ANTHROPIC_API_KEY environment variable
        options = ClaudeAgentOptions(
            model="sonnet",
            system_prompt="You are a helpful assistant.",
            max_turns=1
        )

        print(f"✅ Options created successfully")
        print(f"   Model: {options.model}")

        print("\n🔄 Connecting to Claude API...")

        async with ClaudeSDKClient(options=options) as client:
            print("✅ SDK Client created successfully!")

            print("\n🔄 Sending test query...")
            await client.query("Say hello in one word.")

            print("✅ Query sent successfully!")

            print("\n🔄 Receiving response...")
            response_count = 0
            async for event in client.receive_response():
                response_count += 1
                if response_count <= 5:  # Show first 5 events
                    print(f"   Event {response_count}: {type(event).__name__}")

            print(f"\n✅ Received {response_count} events")

        print("\n" + "="*70)
        print("✅ SUCCESS! SDK is working correctly.")
        print("="*70 + "\n")

    except TimeoutError as e:
        print(f"\n❌ TIMEOUT ERROR: {e}")
        print("\nPossible causes:")
        print("1. API key is invalid or expired")
        print("2. Network connection issue")
        print("3. Firewall blocking API access")
        print("\nTry:")
        print("- Verify your API key at https://console.anthropic.com/")
        print("- Check your internet connection")
        print("- Check if you can access api.anthropic.com")

    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
