"""
Example script to upload evidence packet to S3
"""
import json
import sys
from setup_s3_bucket import upload_evidence_to_s3
from cre_agent.config import load_settings

# Example evidence data (from user)
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
    # Load settings to get bucket name
    settings = load_settings()
    
    if not settings.s3_bucket:
        print("❌ S3_BUCKET not configured in .env file")
        print("   Please set S3_BUCKET=your-bucket-name in your .env file")
        sys.exit(1)
    
    print(f"Uploading evidence to bucket: {settings.s3_bucket}")
    print(f"Region: {settings.aws_region}")
    
    s3_uri = upload_evidence_to_s3(
        settings.s3_bucket,
        evidence_data,
        settings.aws_region
    )
    
    if s3_uri:
        print(f"\n✅ Success! Evidence uploaded to: {s3_uri}")
        # Update the evidence data with S3 URI
        evidence_data["s3_uri"] = s3_uri
        print(f"\nUpdated evidence data with S3 URI:")
        print(json.dumps(evidence_data, indent=2))
    else:
        print("\n❌ Failed to upload evidence")
        sys.exit(1)

