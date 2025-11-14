# S3 Bucket Setup for REVA

This guide will help you create an S3 bucket to store REVA deal evidence and data.

## Quick Setup

### Step 1: Install AWS CLI (if not already installed)

```bash
# Windows (using pip)
pip install awscli

# Or download from: https://aws.amazon.com/cli/
```

### Step 2: Configure AWS Credentials

```bash
aws configure
```

Enter:
- **AWS Access Key ID**: Your AWS access key
- **AWS Secret Access Key**: Your AWS secret key
- **Default region**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

### Step 3: Create S3 Bucket

#### Option A: Using the Setup Script (Recommended)

```bash
python setup_s3_bucket.py --bucket-name reva-deal-evidence --region us-east-1
```

**Note**: Bucket names must be:
- Globally unique across all AWS accounts
- 3-63 characters long
- Lowercase letters, numbers, and hyphens only
- Cannot start or end with a hyphen

#### Option B: Using AWS CLI

```bash
aws s3 mb s3://reva-deal-evidence --region us-east-1
```

#### Option C: Using AWS Console

1. Go to https://console.aws.amazon.com/s3/
2. Click "Create bucket"
3. Enter bucket name (e.g., `reva-deal-evidence`)
4. Select region (e.g., `us-east-1`)
5. Configure settings:
   - **Versioning**: Enable (for audit trails)
   - **Encryption**: Enable (AES256)
   - **Block public access**: Enable (security)
6. Click "Create bucket"

### Step 4: Configure Environment Variables

Add to your `.env` file:

```bash
S3_BUCKET=reva-deal-evidence
AWS_REGION=us-east-1
DEMO_MODE=0
```

### Step 5: Test Upload

Upload your evidence data:

```bash
python upload_evidence_example.py
```

Or use the Python script directly:

```python
from cre_agent.storage import upload_evidence_to_s3
from cre_agent.config import load_settings

settings = load_settings()
evidence = {
    "evidence_type": "cre_deal_analysis",
    "run_id": "c2cf29cd",
    # ... your evidence data
}

s3_uri = upload_evidence_to_s3(
    evidence,
    settings.s3_bucket,
    settings.aws_region
)
print(f"Uploaded to: {s3_uri}")
```

## Bucket Structure

Evidence files are organized by date:

```
s3://reva-deal-evidence/
├── evidence/
│   ├── 2025/
│   │   ├── 11/
│   │   │   ├── 14/
│   │   │   │   ├── c2cf29cd_2025-11-14T13-05-35-567960.json
│   │   │   │   └── ...
│   │   │   └── ...
│   │   └── ...
│   └── ...
└── cre-deals/  (for deal runs)
    └── {run_id}.json
```

## Features Configured

The setup script automatically configures:

✅ **Versioning**: All file versions are kept for audit trails  
✅ **Encryption**: AES256 server-side encryption  
✅ **Public Access Blocked**: Bucket is private by default  
✅ **Lifecycle Policy**: Files older than 90 days transition to cheaper storage (Standard-IA)

## Troubleshooting

### "BucketAlreadyExists" Error

The bucket name is already taken. Try a different name:
```bash
python setup_s3_bucket.py --bucket-name reva-deals-yourname-2025
```

### "Access Denied" Error

Check your AWS credentials:
```bash
aws sts get-caller-identity
```

### "NoCredentialsError"

Configure AWS credentials:
```bash
aws configure
```

## Cost Estimation

- **Storage**: ~$0.023 per GB/month (first 50 TB)
- **Requests**: ~$0.005 per 1,000 PUT requests
- **Data Transfer**: Free within same region

For typical usage (1000 deals/month, ~10KB each):
- Storage: ~$0.0002/month
- Requests: ~$0.005/month
- **Total: ~$0.01/month** (essentially free)

## Security Best Practices

1. ✅ Enable versioning (done automatically)
2. ✅ Enable encryption (done automatically)
3. ✅ Block public access (done automatically)
4. ✅ Use IAM roles in production (not access keys)
5. ✅ Enable CloudTrail for audit logging
6. ✅ Set up bucket policies to restrict access

## Next Steps

After setting up S3:

1. Update your `.env` file with the bucket name
2. Set `DEMO_MODE=0` to enable real S3 uploads
3. Test by running a deal analysis in REVA
4. Check S3 console to verify files are being uploaded

