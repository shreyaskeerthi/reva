"""
Configuration module - handles environment variables and settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Demo mode - if True, use mock responses for all integrations
    demo_mode: bool = Field(default=False, alias="DEMO_MODE")

    # AWS Configuration
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_profile: Optional[str] = Field(default=None, alias="AWS_PROFILE")
    s3_bucket: Optional[str] = Field(default=None, alias="S3_BUCKET")
    use_bedrock: bool = Field(default=True, alias="USE_BEDROCK")

    # Deepgram
    deepgram_api_key: Optional[str] = Field(default=None, alias="DEEPGRAM_API_KEY")

    # Merge CRM
    merge_api_key: Optional[str] = Field(default=None, alias="MERGE_API_KEY")
    merge_base_url: str = Field(
        default="https://api.merge.dev/api/crm/v1",
        alias="MERGE_BASE_URL"
    )
    merge_account_token: Optional[str] = Field(default=None, alias="MERGE_ACCOUNT_TOKEN")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    @property
    def has_aws_config(self) -> bool:
        """Check if AWS is configured"""
        return self.use_bedrock and not self.demo_mode

    @property
    def has_s3_config(self) -> bool:
        """Check if S3 is configured"""
        return self.s3_bucket is not None and not self.demo_mode

    @property
    def has_deepgram_config(self) -> bool:
        """Check if Deepgram is configured"""
        return self.deepgram_api_key is not None and not self.demo_mode

    @property
    def has_merge_config(self) -> bool:
        """Check if Merge is configured"""
        return (
            self.merge_api_key is not None
            and self.merge_account_token is not None
            and not self.demo_mode
        )


def load_settings() -> Settings:
    """Load settings from environment"""
    return Settings()
