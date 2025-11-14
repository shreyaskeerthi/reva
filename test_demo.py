#!/usr/bin/env python3
"""
Quick test script to verify demo mode functionality
Run this before starting the full Streamlit app
"""

import os
os.environ["DEMO_MODE"] = "1"

print("🏢 CRE Deal Voice Agent - Demo Mode Test")
print("=" * 50)

# Test imports
print("\n1. Testing imports...")
try:
    from cre_agent.config import load_settings
    from cre_agent.deepgram_client import DeepgramClient
    from cre_agent.bedrock_client import BedrockClient
    from cre_agent.merge_client import MergeClient
    from cre_agent.deal_parser import heuristic_parse
    from cre_agent.scoring import score_deal, get_default_buybox
    from cre_agent.agent_orchestrator import run_deal_agent
    from cre_agent.storage import run_daily_summary_job, get_cluster_health
    from cre_agent.examples import get_all_examples
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    exit(1)

# Test configuration
print("\n2. Testing configuration...")
try:
    settings = load_settings()
    print(f"   ✅ Settings loaded (demo_mode={settings.demo_mode})")
except Exception as e:
    print(f"   ❌ Config failed: {e}")
    exit(1)

# Test deal parser
print("\n3. Testing deal parser...")
try:
    test_text = "148-unit multifamily in Austin, Texas. Asking $18.5M, NOI of $1.2M, 6.5% cap."
    parsed = heuristic_parse(test_text)
    print(f"   ✅ Parsed deal: {parsed.get('property_type')} in {parsed.get('location')}")
except Exception as e:
    print(f"   ❌ Parser failed: {e}")
    exit(1)

# Test scoring
print("\n4. Testing buy-box scoring...")
try:
    buybox = get_default_buybox()
    score_result = score_deal(parsed, buybox)
    print(f"   ✅ Score: {score_result['score']}/100, Verdict: {score_result['verdict']}")
except Exception as e:
    print(f"   ❌ Scoring failed: {e}")
    exit(1)

# Test Deepgram client
print("\n5. Testing Deepgram client (demo mode)...")
try:
    deepgram = DeepgramClient(demo_mode=True)
    transcript = deepgram.transcribe_bytes(b"fake_audio", "test.wav")
    print(f"   ✅ Transcript length: {len(transcript)} chars")
except Exception as e:
    print(f"   ❌ Deepgram failed: {e}")
    exit(1)

# Test Bedrock client
print("\n6. Testing Bedrock client (demo mode)...")
try:
    bedrock = BedrockClient(demo_mode=True)
    extracted = bedrock.extract_deal_struct(test_text)
    print(f"   ✅ Extracted property type: {extracted.get('property_type')}")

    summary = bedrock.generate_ic_summary(extracted)
    print(f"   ✅ IC summary length: {len(summary)} chars")
except Exception as e:
    print(f"   ❌ Bedrock failed: {e}")
    exit(1)

# Test Merge client
print("\n7. Testing Merge client (demo mode)...")
try:
    merge = MergeClient(demo_mode=True)
    contact_id = merge.upsert_contact(
        email="test@example.com",
        name="Test Broker",
        company="Test Company"
    )
    print(f"   ✅ Created contact: {contact_id}")
except Exception as e:
    print(f"   ❌ Merge failed: {e}")
    exit(1)

# Test full agent orchestrator
print("\n8. Testing full agent pipeline...")
try:
    examples = get_all_examples()
    first_example = list(examples.values())[0]

    result = run_deal_agent(
        raw_text=first_example,
        buybox=buybox,
        config=settings
    )

    print(f"   ✅ Run ID: {result['run_id']}")
    print(f"   ✅ Score: {result['score_data']['score']}/100")
    print(f"   ✅ Verdict: {result['score_data']['verdict']}")
    print(f"   ✅ Local path: {result.get('local_path', 'N/A')}")
except Exception as e:
    print(f"   ❌ Agent failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test daily summary job
print("\n9. Testing daily summary job...")
try:
    summary = run_daily_summary_job()
    print(f"   ✅ Summary status: {summary['status']}")
    if summary['status'] == 'success':
        print(f"   ✅ Total deals: {summary['deal_count']}")
except Exception as e:
    print(f"   ❌ Summary job failed: {e}")
    exit(1)

# Test cluster health
print("\n10. Testing cluster health check...")
try:
    health = get_cluster_health()
    print(f"   ✅ Cluster status: {health['status']}")
    print(f"   ✅ Nodes: {health['nodes']}, Pods: {health['pods']}")
except Exception as e:
    print(f"   ❌ Health check failed: {e}")
    exit(1)

print("\n" + "=" * 50)
print("✅ ALL TESTS PASSED!")
print("\nYou can now run the full application:")
print("  streamlit run app.py")
print("=" * 50)
