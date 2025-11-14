"""
Script to fix S3 bucket permissions for REVA
This ensures your IAM user/role can access the bucket
"""
import boto3
import json
from botocore.exceptions import ClientError


def check_bucket_access(bucket_name: str, region: str = "us-east-1") -> bool:
    """Check if we can access the bucket"""
    try:
        s3_client = boto3.client("s3", region_name=region)
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Can access bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"❌ Cannot access bucket: {e}")
        return False


def check_object_exists(bucket_name: str, key: str, region: str = "us-east-1") -> bool:
    """Check if an object exists"""
    try:
        s3_client = boto3.client("s3", region_name=region)
        s3_client.head_object(Bucket=bucket_name, Key=key)
        print(f"✅ Object exists: {key}")
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "404":
            print(f"⚠️  Object not found: {key}")
        else:
            print(f"❌ Error checking object: {e}")
        return False


def list_objects_in_bucket(bucket_name: str, prefix: str = "", region: str = "us-east-1"):
    """List objects in the bucket"""
    try:
        s3_client = boto3.client("s3", region_name=region)
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            MaxKeys=10
        )
        
        if "Contents" in response:
            print(f"\n📁 Found {len(response['Contents'])} objects with prefix '{prefix}':")
            for obj in response["Contents"]:
                print(f"   - {obj['Key']} ({obj['Size']} bytes)")
            return response["Contents"]
        else:
            print(f"\n⚠️  No objects found with prefix '{prefix}'")
            return []
    except ClientError as e:
        print(f"❌ Error listing objects: {e}")
        return []


def get_current_iam_user() -> str:
    """Get the current IAM user/role"""
    try:
        sts_client = boto3.client("sts", region_name="us-east-1")
        identity = sts_client.get_caller_identity()
        arn = identity.get("Arn", "")
        print(f"Current AWS identity: {arn}")
        return arn
    except Exception as e:
        print(f"⚠️  Could not get IAM identity: {e}")
        return ""


def create_bucket_policy(bucket_name: str, iam_user_arn: str = None) -> dict:
    """
    Create a bucket policy that allows the IAM user to access the bucket
    
    Note: This creates a policy, but you need to attach it via AWS Console
    or use put_bucket_policy if you have permissions
    """
    if iam_user_arn:
        # Policy for specific IAM user
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowIAMUserAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": iam_user_arn
                    },
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:ListBucket",
                        "s3:DeleteObject"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ]
                }
            ]
        }
    else:
        # Policy for account (safer - uses account ID)
        sts_client = boto3.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
        
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowAccountAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:aws:iam::{account_id}:root"
                    },
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:ListBucket",
                        "s3:DeleteObject"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ]
                }
            ]
        }
    
    return policy


def apply_bucket_policy(bucket_name: str, policy: dict, region: str = "us-east-1") -> bool:
    """Apply bucket policy"""
    try:
        s3_client = boto3.client("s3", region_name=region)
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy)
        )
        print("✅ Bucket policy applied successfully!")
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "AccessDenied":
            print("⚠️  Cannot apply bucket policy (insufficient permissions)")
            print("   You'll need to apply this policy manually in AWS Console")
            return False
        else:
            print(f"❌ Error applying policy: {e}")
            return False


def diagnose_and_fix(bucket_name: str, region: str = "us-east-1"):
    """Diagnose and fix S3 access issues"""
    print("=" * 60)
    print("S3 Access Diagnostics")
    print("=" * 60)
    print()
    
    # Step 1: Check IAM identity
    print("Step 1: Checking AWS identity...")
    iam_arn = get_current_iam_user()
    print()
    
    # Step 2: Check bucket access
    print("Step 2: Checking bucket access...")
    has_access = check_bucket_access(bucket_name, region)
    print()
    
    # Step 3: List objects
    print("Step 3: Listing objects in bucket...")
    objects = list_objects_in_bucket(bucket_name, "evidence/", region)
    print()
    
    # Step 4: Check specific object
    test_key = "evidence/c2cf29cd_2025-11-14T13-05-35.567960.json"
    print(f"Step 4: Checking for specific object...")
    object_exists = check_object_exists(bucket_name, test_key, region)
    print()
    
    # Step 5: Try to fix permissions
    if not has_access or not object_exists:
        print("Step 5: Attempting to fix permissions...")
        print()
        
        # Create bucket policy
        policy = create_bucket_policy(bucket_name, iam_arn if iam_arn else None)
        
        print("Generated bucket policy:")
        print(json.dumps(policy, indent=2))
        print()
        
        # Try to apply
        applied = apply_bucket_policy(bucket_name, policy, region)
        
        if not applied:
            print("\n" + "=" * 60)
            print("MANUAL FIX REQUIRED")
            print("=" * 60)
            print("\nTo fix access, do one of the following:")
            print("\nOption 1: Add IAM Policy to your user/role")
            print("   Go to: https://console.aws.amazon.com/iam/")
            print("   Attach this policy to your IAM user/role:")
            print()
            print(json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:ListBucket",
                            "s3:DeleteObject"
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{bucket_name}",
                            f"arn:aws:s3:::{bucket_name}/*"
                        ]
                    }
                ]
            }, indent=2))
            print()
            print("\nOption 2: Apply bucket policy")
            print(f"   Go to: https://console.aws.amazon.com/s3/buckets/{bucket_name}")
            print("   Click 'Permissions' → 'Bucket policy' → 'Edit'")
            print("   Paste the policy shown above")
            print()
    
    print("=" * 60)
    print("Diagnostics Complete")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix S3 bucket permissions")
    parser.add_argument(
        "--bucket-name",
        type=str,
        default="reva-deal-evidence",
        help="S3 bucket name"
    )
    parser.add_argument(
        "--region",
        type=str,
        default="us-east-1",
        help="AWS region"
    )
    
    args = parser.parse_args()
    
    diagnose_and_fix(args.bucket_name, args.region)

