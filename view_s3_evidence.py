"""
View and download evidence files from S3
"""
import boto3
import json
import sys
from cre_agent.config import load_settings


def list_evidence_files(bucket_name: str, prefix: str = "evidence/", region: str = "us-east-1"):
    """List all evidence files in the bucket"""
    try:
        s3_client = boto3.client("s3", region_name=region)
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            MaxKeys=100
        )
        
        if "Contents" in response:
            print(f"\n📁 Found {len(response['Contents'])} evidence files:\n")
            for i, obj in enumerate(response["Contents"], 1):
                size_kb = obj['Size'] / 1024
                print(f"{i}. {obj['Key']}")
                print(f"   Size: {size_kb:.2f} KB | Modified: {obj['LastModified']}")
            return response["Contents"]
        else:
            print(f"\n⚠️  No evidence files found with prefix '{prefix}'")
            return []
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return []


def view_evidence_file(bucket_name: str, key: str, region: str = "us-east-1"):
    """View an evidence file"""
    try:
        s3_client = boto3.client("s3", region_name=region)
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        content = response["Body"].read().decode("utf-8")
        evidence = json.loads(content)
        
        print("=" * 60)
        print(f"Evidence File: {key}")
        print("=" * 60)
        print(json.dumps(evidence, indent=2))
        print("=" * 60)
        
        return evidence
    except Exception as e:
        print(f"❌ Error viewing file: {e}")
        return None


def download_evidence_file(bucket_name: str, key: str, output_path: str = None, region: str = "us-east-1"):
    """Download an evidence file"""
    try:
        s3_client = boto3.client("s3", region_name=region)
        
        if not output_path:
            # Use filename from key
            output_path = key.split("/")[-1]
        
        print(f"Downloading {key} to {output_path}...")
        s3_client.download_file(bucket_name, key, output_path)
        print(f"✅ Downloaded to: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Error downloading file: {e}")
        return None


def get_s3_url(bucket_name: str, key: str, region: str = "us-east-1") -> str:
    """Generate S3 URL (requires proper permissions)"""
    return f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View and manage S3 evidence files")
    parser.add_argument(
        "--action",
        type=str,
        choices=["list", "view", "download"],
        default="list",
        help="Action to perform"
    )
    parser.add_argument(
        "--key",
        type=str,
        help="S3 object key (for view/download)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (for download)"
    )
    parser.add_argument(
        "--bucket-name",
        type=str,
        help="S3 bucket name (default: from .env)"
    )
    parser.add_argument(
        "--region",
        type=str,
        default="us-east-1",
        help="AWS region"
    )
    
    args = parser.parse_args()
    
    # Get bucket name from settings or args
    if args.bucket_name:
        bucket_name = args.bucket_name
    else:
        settings = load_settings()
        if not settings.s3_bucket:
            print("❌ S3_BUCKET not configured. Use --bucket-name or set in .env")
            sys.exit(1)
        bucket_name = settings.s3_bucket
    
    print(f"Using bucket: {bucket_name} (region: {args.region})")
    
    if args.action == "list":
        files = list_evidence_files(bucket_name, region=args.region)
        if files:
            print(f"\n💡 To view a file:")
            print(f"   python view_s3_evidence.py --action view --key \"{files[0]['Key']}\"")
            print(f"\n💡 To download a file:")
            print(f"   python view_s3_evidence.py --action download --key \"{files[0]['Key']}\"")
    
    elif args.action == "view":
        if not args.key:
            print("❌ --key is required for view action")
            sys.exit(1)
        view_evidence_file(bucket_name, args.key, args.region)
    
    elif args.action == "download":
        if not args.key:
            print("❌ --key is required for download action")
            sys.exit(1)
        download_evidence_file(bucket_name, args.key, args.output, args.region)

