"""
Quick test script to upload the provided evidence data to S3
"""
import json
from setup_s3_bucket import upload_evidence_to_s3, create_s3_bucket
from cre_agent.config import load_settings

# Your evidence data
evidence_data = {
    "evidence_type": "cre_deal_analysis",
    "run_id": "c2cf29cd",
    "timestamp": "2025-11-14T13:05:35.567960",
    "raw_text_hash": "1b325fed1afb3d05",
    "deal_summary": {
        "property_type": "multifamily",
        "location": {"city": "Demo City", "state": "CA"},
        "purchase_price": 18500000,
        "cap_rate": 6.5
    },
    "analysis": {
        "score": 85,
        "verdict": "Pass",
        "reasons": [
            "✓ Cap rate 6.50% within target range",
            "✓ Deal size $18,500,000 within range",
            "Market Demo City not in preferred list (−15 pts)",
            "✓ Property type multifamily is preferred"
        ]
    },
    "crm_records": {},
    "s3_uri": None
}

if __name__ == "__main__":
    # Default bucket name (change if needed)
    bucket_name = "reva-deal-evidence"
    region = "us-east-1"
    
    print("=" * 60)
    print("REVA S3 Setup & Upload Test")
    print("=" * 60)
    print()
    
    # Step 1: Create bucket (if it doesn't exist)
    print("Step 1: Creating/Checking S3 bucket...")
    create_s3_bucket(bucket_name, region)
    print()
    
    # Step 2: Upload evidence
    print("Step 2: Uploading evidence data...")
    s3_uri = upload_evidence_to_s3(bucket_name, evidence_data, region)
    print()
    
    if s3_uri:
        # Update evidence with S3 URI
        evidence_data["s3_uri"] = s3_uri
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"\nEvidence uploaded to: {s3_uri}")
        print(f"\nUpdated evidence data:")
        print(json.dumps(evidence_data, indent=2))
        print()
        print("Next steps:")
        print(f"1. Add to your .env file:")
        print(f"   S3_BUCKET={bucket_name}")
        print(f"   AWS_REGION={region}")
        print(f"   DEMO_MODE=0")
        print()
        print("2. Restart your REVA app to use S3 storage")
    else:
        print("❌ Failed to upload evidence. Check AWS credentials and permissions.")

