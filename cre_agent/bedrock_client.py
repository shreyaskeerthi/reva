"""
AWS Bedrock client for CRE deal extraction and IC summary generation
"""
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class BedrockClient:
    """Client for AWS Bedrock Titan text model"""

    def __init__(self, region: str = "us-east-1", use_bedrock: bool = True, demo_mode: bool = False):
        self.region = region
        self.use_bedrock = use_bedrock
        self.demo_mode = demo_mode
        self.client = None

        if use_bedrock and not demo_mode:
            try:
                import boto3
                self.client = boto3.client("bedrock-runtime", region_name=region)
                logger.info(f"Bedrock client initialized for region {region}")
            except Exception as e:
                logger.warning(f"Failed to initialize Bedrock client: {e}. Falling back to demo mode.")
                self.demo_mode = True

    def extract_deal_struct(self, text: str) -> Dict:
        """
        Extract structured CRE deal data from free-form text

        Args:
            text: Raw deal text (from voice transcription, email, OM, etc.)

        Returns:
            Dictionary with structured deal fields
        """
        if self.demo_mode or not self.client:
            logger.info("Using demo mode for deal extraction")
            return self._demo_extract_deal_struct(text)

        try:
            prompt = f"""You are a commercial real estate expert. Extract structured deal information from the following text.

Return ONLY valid JSON with these fields (use null for missing data):
{{
  "property_type": "multifamily|office|industrial|retail|mixed_use|other",
  "location": {{"city": "string", "state": "string"}},
  "purchase_price": number (in dollars),
  "noi": number (in dollars, annual),
  "cap_rate": number (as decimal, e.g., 5.25 for 5.25%),
  "units": number (for multifamily),
  "square_feet": number,
  "year_built": number,
  "occupancy": number (as decimal, e.g., 0.95 for 95%),
  "asking_price": number (in dollars),
  "broker_name": "string",
  "broker_email": "string",
  "broker_company": "string",
  "seller_name": "string",
  "notes": "string"
}}

Text:
{text}

JSON:"""

            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 1024,
                    "temperature": 0.1,
                    "topP": 0.9
                }
            })

            response = self.client.invoke_model(
                modelId="amazon.titan-text-lite-v1",
                body=body,
                contentType="application/json",
                accept="application/json"
            )

            response_body = json.loads(response["body"].read())
            result_text = response_body["results"][0]["outputText"]

            # Extract JSON from response (might have extra text)
            json_start = result_text.find("{")
            json_end = result_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                result_text = result_text[json_start:json_end]

            extracted = json.loads(result_text)
            logger.info("Successfully extracted deal structure via Bedrock")
            return extracted

        except Exception as e:
            logger.error(f"Bedrock extraction failed: {e}. Falling back to demo mode.")
            return self._demo_extract_deal_struct(text)

    def generate_ic_summary(self, struct: Dict) -> str:
        """
        Generate an Investment Committee-style summary from structured deal data

        Args:
            struct: Structured deal dictionary

        Returns:
            Professional IC summary text
        """
        if self.demo_mode or not self.client:
            logger.info("Using demo mode for IC summary generation")
            return self._demo_generate_ic_summary(struct)

        try:
            prompt = f"""You are a senior investment professional preparing a summary for an Investment Committee.

Based on this commercial real estate deal data, write a concise 2-3 paragraph IC memo summary.

Deal Data:
{json.dumps(struct, indent=2)}

Focus on:
1. Property fundamentals (type, location, size, condition)
2. Financial metrics (price, NOI, cap rate, returns)
3. Key risks and opportunities
4. Recommendation context

Write in a professional, direct tone. Be analytical but concise.

Summary:"""

            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 512,
                    "temperature": 0.3,
                    "topP": 0.9
                }
            })

            response = self.client.invoke_model(
                modelId="amazon.titan-text-lite-v1",
                body=body,
                contentType="application/json",
                accept="application/json"
            )

            response_body = json.loads(response["body"].read())
            summary = response_body["results"][0]["outputText"].strip()
            logger.info("Successfully generated IC summary via Bedrock")
            return summary

        except Exception as e:
            logger.error(f"Bedrock IC summary generation failed: {e}. Falling back to demo mode.")
            return self._demo_generate_ic_summary(struct)

    def _demo_extract_deal_struct(self, text: str) -> Dict:
        """Demo/fallback extraction using simple heuristics"""
        # This will be enhanced by deal_parser.py
        return {
            "property_type": "multifamily",
            "location": {"city": "Demo City", "state": "CA"},
            "purchase_price": None,
            "noi": None,
            "cap_rate": None,
            "units": None,
            "square_feet": None,
            "year_built": None,
            "occupancy": None,
            "asking_price": None,
            "broker_name": None,
            "broker_email": None,
            "broker_company": None,
            "seller_name": None,
            "notes": text[:200] if text else None
        }

    def _demo_generate_ic_summary(self, struct: Dict) -> str:
        """Demo/fallback IC summary generation"""
        prop_type = struct.get("property_type", "commercial property")
        location = struct.get("location", {})
        city = location.get("city", "Unknown")
        state = location.get("state", "")

        price = struct.get("purchase_price") or struct.get("asking_price")
        noi = struct.get("noi")
        cap_rate = struct.get("cap_rate")

        summary = f"**Investment Opportunity: {prop_type.title()} - {city}, {state}**\n\n"

        if price:
            summary += f"The subject property is available for acquisition at ${price:,.0f}. "

        if noi and cap_rate:
            summary += f"The asset generates ${noi:,.0f} in annual NOI at a {cap_rate:.2f}% cap rate. "

        summary += f"This {prop_type} property in {city} presents an opportunity for value creation through operational improvements and market positioning. "

        summary += "\n\nKey considerations include current market dynamics, property condition, and execution risk on the business plan. Further due diligence is recommended to validate underwriting assumptions."

        return summary
