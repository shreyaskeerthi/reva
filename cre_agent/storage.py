"""
Storage layer - local JSON logging + S3 + evidence generation + daily summary
"""
import json
import logging
import os
import hashlib
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


def log_run_local(run_id: str, payload: Dict) -> str:
    """
    Log a deal run to local JSON file

    Args:
        run_id: Unique run identifier
        payload: Run data to log

    Returns:
        Path to the saved file
    """
    # Create runs directory if it doesn't exist
    runs_dir = Path("./runs")
    runs_dir.mkdir(exist_ok=True)

    # Save to JSON file
    file_path = runs_dir / f"{run_id}.json"
    with open(file_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    logger.info(f"Logged run to {file_path}")
    return str(file_path)


def log_run_s3(run_id: str, payload: Dict, bucket: str, region: str = "us-east-1") -> Optional[str]:
    """
    Log a deal run to S3

    Args:
        run_id: Unique run identifier
        payload: Run data to log
        bucket: S3 bucket name
        region: AWS region

    Returns:
        S3 URI if successful, None otherwise
    """
    if not bucket:
        logger.warning("No S3 bucket configured, skipping S3 upload")
        return None

    try:
        import boto3

        s3_client = boto3.client("s3", region_name=region)
        key = f"cre-deals/{run_id}.json"

        # Upload to S3
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(payload, indent=2, default=str),
            ContentType="application/json"
        )

        s3_uri = f"s3://{bucket}/{key}"
        logger.info(f"Uploaded run to {s3_uri}")
        return s3_uri

    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")
        return None


def build_evidence_packet(run_payload: Dict) -> Dict:
    """
    Build a compliance evidence packet from a run payload

    Args:
        run_payload: Complete run payload

    Returns:
        Evidence packet dictionary
    """
    raw_text = run_payload.get("raw_text", "")
    text_hash = hashlib.sha256(raw_text.encode()).hexdigest()[:16]

    structured = run_payload.get("structured_deal", {})
    score_data = run_payload.get("score_data", {})

    evidence = {
        "evidence_type": "cre_deal_analysis",
        "run_id": run_payload.get("run_id"),
        "timestamp": run_payload.get("timestamp"),
        "raw_text_hash": text_hash,
        "deal_summary": {
            "property_type": structured.get("property_type"),
            "location": structured.get("location"),
            "purchase_price": structured.get("purchase_price") or structured.get("asking_price"),
            "cap_rate": score_data.get("metrics", {}).get("cap_rate"),
        },
        "analysis": {
            "score": score_data.get("score"),
            "verdict": score_data.get("verdict"),
            "reasons": score_data.get("reasons", []),
        },
        "crm_records": run_payload.get("crm_records", {}),
        "s3_uri": run_payload.get("s3_uri"),
    }

    return evidence


def send_to_vanta(evidence: Dict) -> Dict:
    """
    Send evidence packet to Vanta (simulated)

    Args:
        evidence: Evidence packet

    Returns:
        Acknowledgment dictionary
    """
    # In real implementation, this would call Vanta's API
    # For now, we log to a local evidence file
    evidence_log = Path("./runs/evidence_log.jsonl")
    evidence_log.parent.mkdir(exist_ok=True)

    log_entry = {
        "destination": "vanta",
        "timestamp": datetime.now().isoformat(),
        "evidence": evidence
    }

    with open(evidence_log, "a") as f:
        f.write(json.dumps(log_entry, default=str) + "\n")

    logger.info(f"Logged evidence to Vanta simulation: {evidence_log}")

    return {
        "ack": True,
        "evidence_id": f"vanta-{evidence['run_id']}",
        "timestamp": datetime.now().isoformat()
    }


def send_to_thoropass(evidence: Dict) -> Dict:
    """
    Send evidence packet to Thoropass (simulated)

    Args:
        evidence: Evidence packet

    Returns:
        Acknowledgment dictionary
    """
    # In real implementation, this would call Thoropass's API
    # For now, we log to a local evidence file
    evidence_log = Path("./runs/evidence_log.jsonl")
    evidence_log.parent.mkdir(exist_ok=True)

    log_entry = {
        "destination": "thoropass",
        "timestamp": datetime.now().isoformat(),
        "evidence": evidence
    }

    with open(evidence_log, "a") as f:
        f.write(json.dumps(log_entry, default=str) + "\n")

    logger.info(f"Logged evidence to Thoropass simulation: {evidence_log}")

    return {
        "ack": True,
        "evidence_id": f"thoropass-{evidence['run_id']}",
        "timestamp": datetime.now().isoformat()
    }


def run_daily_summary_job() -> Dict:
    """
    Dagster-style daily summary job - analyzes recent deal runs

    Returns:
        Summary dictionary with stats and top deals
    """
    runs_dir = Path("./runs")

    if not runs_dir.exists():
        return {
            "status": "no_data",
            "message": "No runs directory found",
            "deal_count": 0
        }

    # Load all run files
    run_files = list(runs_dir.glob("*.json"))
    run_files = [f for f in run_files if f.name != "evidence_log.jsonl"]

    if not run_files:
        return {
            "status": "no_data",
            "message": "No deal runs found",
            "deal_count": 0
        }

    deals = []
    for run_file in run_files:
        try:
            with open(run_file) as f:
                data = json.load(f)
                deals.append(data)
        except Exception as e:
            logger.warning(f"Failed to load {run_file}: {e}")

    # Compute statistics
    deal_count = len(deals)

    scores = []
    for deal in deals:
        score_data = deal.get("score_data", {})
        score = score_data.get("score")
        if score is not None:
            scores.append((score, deal))

    avg_score = sum(s[0] for s in scores) / len(scores) if scores else 0

    # Top 3 deals by score
    scores.sort(reverse=True, key=lambda x: x[0])
    top_deals = []

    for score, deal in scores[:3]:
        structured = deal.get("structured_deal", {})
        location = structured.get("location", {})
        city = location.get("city", "Unknown") if isinstance(location, dict) else "Unknown"
        prop_type = structured.get("property_type", "Unknown")

        top_deals.append({
            "run_id": deal.get("run_id"),
            "score": score,
            "verdict": deal.get("score_data", {}).get("verdict"),
            "property_type": prop_type,
            "location": city,
            "price": structured.get("purchase_price") or structured.get("asking_price")
        })

    summary = {
        "status": "success",
        "job_run_time": datetime.now().isoformat(),
        "deal_count": deal_count,
        "avg_score": round(avg_score, 1),
        "top_deals": top_deals,
        "verdicts": {
            "pass": sum(1 for d in deals if d.get("score_data", {}).get("verdict") == "Pass"),
            "watch": sum(1 for d in deals if d.get("score_data", {}).get("verdict") == "Watch"),
            "hard_pass": sum(1 for d in deals if d.get("score_data", {}).get("verdict") == "Hard Pass"),
        }
    }

    logger.info(f"Daily summary job completed: {deal_count} deals analyzed")
    return summary


def get_cluster_health() -> Dict:
    """
    Spectro Cloud-style cluster health check (simulated)

    Returns:
        Cluster health status dictionary
    """
    # In real implementation, this would call Spectro Cloud API
    # For now, return simulated healthy status
    return {
        "status": "healthy",
        "cluster": "demo-cre-agent",
        "region": "us-east-1",
        "nodes": 1,
        "pods": 3,
        "last_check": datetime.now().isoformat(),
        "metrics": {
            "cpu_usage": "23%",
            "memory_usage": "41%",
            "disk_usage": "18%"
        }
    }
