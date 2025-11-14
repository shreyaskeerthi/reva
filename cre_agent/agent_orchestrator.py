"""
CRE Deal Agent Orchestrator - chains all components together
"""
import logging
from datetime import datetime
from typing import Dict
import uuid

from .config import Settings
from .bedrock_client import BedrockClient
from .deal_parser import heuristic_parse
from .scoring import score_deal

logger = logging.getLogger(__name__)


def merge_deal_data(bedrock_result: Dict, heuristic_result: Dict) -> Dict:
    """
    Merge Bedrock extraction with heuristic parsing, preferring Bedrock when available

    Args:
        bedrock_result: Result from Bedrock extraction
        heuristic_result: Result from heuristic parsing

    Returns:
        Merged dictionary
    """
    merged = heuristic_result.copy()

    # Override with Bedrock values where they exist
    for key, value in bedrock_result.items():
        if value is not None:
            merged[key] = value

    return merged


def run_deal_agent(
    raw_text: str,
    buybox: Dict,
    config: Settings
) -> Dict:
    """
    Main agent pipeline - orchestrates the entire CRE deal analysis

    Args:
        raw_text: Raw deal text (from transcription, email, etc.)
        buybox: Buy-box criteria
        config: Application settings

    Returns:
        Complete run payload with all analysis results
    """
    run_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    logger.info(f"Starting deal agent run {run_id}")

    # Step 1: Extract structured data
    logger.info("Step 1: Extracting deal structure")

    # Always run heuristic parsing
    heuristic_result = heuristic_parse(raw_text)

    # Run Bedrock extraction (will use demo mode if not configured)
    bedrock_client = BedrockClient(
        region=config.aws_region,
        use_bedrock=config.use_bedrock and config.has_aws_config,
        demo_mode=config.demo_mode or not config.has_aws_config
    )
    bedrock_result = bedrock_client.extract_deal_struct(raw_text)

    # Merge results
    structured_deal = merge_deal_data(bedrock_result, heuristic_result)
    logger.info(f"Extracted deal structure: {structured_deal.get('property_type')} in {structured_deal.get('location')}")

    # Step 2: Score the deal
    logger.info("Step 2: Scoring deal against buy-box")
    score_data = score_deal(structured_deal, buybox)
    logger.info(f"Deal score: {score_data['score']}/100 - {score_data['verdict']}")

    # Step 3: Generate IC summary
    logger.info("Step 3: Generating IC summary")
    ic_summary = ""

    # Always create a Bedrock client (will use demo mode if not configured)
    bedrock_client = BedrockClient(
        region=config.aws_region,
        use_bedrock=config.use_bedrock and config.has_aws_config,
        demo_mode=config.demo_mode or not config.has_aws_config
    )
    ic_summary = bedrock_client.generate_ic_summary(structured_deal)

    # Step 4: Build run payload
    run_payload = {
        "run_id": run_id,
        "timestamp": timestamp,
        "raw_text": raw_text,
        "structured_deal": structured_deal,
        "score_data": score_data,
        "ic_summary": ic_summary,
        "buybox": buybox,
        "config": {
            "demo_mode": config.demo_mode,
            "used_bedrock": config.has_aws_config,
            "has_s3": config.has_s3_config,
        }
    }

    # Step 5: Log locally
    from .storage import log_run_local, log_run_s3

    local_path = log_run_local(run_id, run_payload)
    run_payload["local_path"] = local_path

    # Step 6: Log to S3 if configured
    if config.has_s3_config:
        s3_uri = log_run_s3(run_id, run_payload, config.s3_bucket, config.aws_region)
        if s3_uri:
            run_payload["s3_uri"] = s3_uri

    logger.info(f"Deal agent run {run_id} completed successfully")

    return run_payload
