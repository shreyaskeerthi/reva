"""
Script to create and configure S3 bucket for REVA deal storage
"""
import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime
import sys


def create_s3_bucket(bucket_name: str, region: str = "us-east-1") -> bool:
    """
    Create an S3 bucket with proper configuration for REVA
    
    Args:
        bucket_name: Name of the bucket (must be globally unique, lowercase, no underscores)
        region: AWS region (default: us-east-1)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        s3_client = boto3.client("s3", region_name=region)
        
        # Check if bucket already exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' already exists!")
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code != "404":
                print(f"❌ Error checking bucket: {e}")
                return False
        
        # Create bucket
        print(f"Creating S3 bucket '{bucket_name}' in region '{region}'...")
        
        if region == "us-east-1":
            # us-east-1 doesn't need LocationConstraint
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region}
            )
        
        print(f"✅ Bucket '{bucket_name}' created successfully!")
        
        # Enable versioning for audit trails
        print("Enabling versioning...")
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={"Status": "Enabled"}
        )
        print("✅ Versioning enabled!")
        
        # Set up encryption
        print("Configuring encryption...")
        s3_client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }
        )
        print("✅ Encryption configured!")
        
        # Block public access (security best practice)
        print("Configuring public access settings...")
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True
            }
        )
        print("✅ Public access blocked!")
        
        # Add lifecycle policy to transition old files to cheaper storage (optional)
        print("Setting up lifecycle policy...")
        try:
            s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={
                    "Rules": [
                        {
                            "Id": "TransitionToIA",
                            "Status": "Enabled",
                            "Transitions": [
                                {
                                    "Days": 90,
                                    "StorageClass": "STANDARD_IA"
                                }
                            ]
                        }
                    ]
                }
            )
            print("✅ Lifecycle policy configured!")
        except Exception as e:
            print(f"⚠️  Could not set lifecycle policy: {e}")
        
        print(f"\n🎉 S3 bucket '{bucket_name}' is ready!")
        print(f"   Region: {region}")
        print(f"   URI: s3://{bucket_name}/")
        print(f"\nAdd to your .env file:")
        print(f"   S3_BUCKET={bucket_name}")
        print(f"   AWS_REGION={region}")
        
        return True
        
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "BucketAlreadyOwnedByYou":
            print(f"✅ Bucket '{bucket_name}' already exists and is owned by you!")
            return True
        elif error_code == "BucketAlreadyExists":
            print(f"❌ Bucket name '{bucket_name}' is already taken. Choose a different name.")
            return False
        else:
            print(f"❌ Error creating bucket: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def upload_evidence_to_s3(bucket_name: str, evidence_data: dict, region: str = "us-east-1") -> str:
    """
    Upload evidence packet to S3
    
    Args:
        bucket_name: S3 bucket name
        evidence_data: Evidence packet dictionary
        region: AWS region
    
    Returns:
        S3 URI of uploaded file
    """
    try:
        s3_client = boto3.client("s3", region_name=region)
        
        run_id = evidence_data.get("run_id", "unknown")
        timestamp = evidence_data.get("timestamp", datetime.now().isoformat())
        
        # Create key with timestamp for organization
        key = f"evidence/{run_id}_{timestamp.replace(':', '-')}.json"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(evidence_data, indent=2, default=str),
            ContentType="application/json",
            Metadata={
                "run_id": run_id,
                "evidence_type": evidence_data.get("evidence_type", "unknown"),
                "timestamp": timestamp
            }
        )
        
        s3_uri = f"s3://{bucket_name}/{key}"
        print(f"✅ Evidence uploaded to: {s3_uri}")
        return s3_uri
        
    except Exception as e:
        print(f"❌ Error uploading to S3: {e}")
        return ""


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create S3 bucket for REVA")
    parser.add_argument(
        "--bucket-name",
        type=str,
        default="reva-deal-evidence",
        help="S3 bucket name (must be globally unique, lowercase, no underscores)"
    )
    parser.add_argument(
        "--region",
        type=str,
        default="us-east-1",
        help="AWS region (default: us-east-1)"
    )
    parser.add_argument(
        "--upload-evidence",
        type=str,
        help="Path to JSON file with evidence data to upload (optional)"
    )
    
    args = parser.parse_args()
    
    # Validate bucket name
    bucket_name = args.bucket_name.lower().replace("_", "-")
    if not bucket_name.replace("-", "").isalnum():
        print("❌ Bucket name must contain only lowercase letters, numbers, and hyphens")
        sys.exit(1)
    
    if len(bucket_name) < 3 or len(bucket_name) > 63:
        print("❌ Bucket name must be between 3 and 63 characters")
        sys.exit(1)
    
    # Create bucket
    success = create_s3_bucket(bucket_name, args.region)
    
    if not success:
        sys.exit(1)
    
    # Upload evidence if provided
    if args.upload_evidence:
        try:
            with open(args.upload_evidence, "r") as f:
                evidence_data = json.load(f)
            upload_evidence_to_s3(bucket_name, evidence_data, args.region)
        except Exception as e:
            print(f"❌ Error uploading evidence: {e}")
            sys.exit(1)

