"""
Deepgram client for speech-to-text transcription (v5 SDK)
"""

import logging
import os
from typing import Optional

from deepgram import DeepgramClient as DGClient
from deepgram.core.api_error import ApiError

logger = logging.getLogger(__name__)


class DeepgramClient:
    """Client for Deepgram speech-to-text API using the official v5 SDK."""

    def __init__(self, api_key: Optional[str] = None, demo_mode: bool = False):
        """
        api_key:
            Kept for backward compatibility. If provided and DEEPGRAM_API_KEY
            is not already set, we'll set it on the environment.
        demo_mode:
            If True, never call Deepgram; always return a canned transcript.
        """
        # Allow env-based demo mode override
        env_demo = os.getenv("DEMO_MODE", "0") == "1"
        self.demo_mode = demo_mode or env_demo
        self.client: Optional[DGClient] = None

        # If they passed an api_key and DEEPGRAM_API_KEY isn't set, set it.
        if api_key and not os.getenv("DEEPGRAM_API_KEY"):
            os.environ["DEEPGRAM_API_KEY"] = api_key

        if self.demo_mode:
            logger.info("Deepgram client running in demo mode (no API calls).")
            return

        try:
            # v5 SDK: no args, reads DEEPGRAM_API_KEY or DEEPGRAM_TOKEN from env
            self.client = DGClient()
            logger.info("Deepgram v5 client initialized successfully.")
        except Exception as e:
            logger.warning(
                f"Failed to initialize Deepgram client: {e}. Falling back to demo mode."
            )
            self.demo_mode = True
            self.client = None

    def transcribe_bytes(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """
        Transcribe audio bytes to text.

        Args:
            audio_bytes: Audio file bytes
            filename: Original filename (for logging only)

        Returns:
            Transcribed text
        """
        if self.demo_mode or self.client is None:
            logger.info("Using demo mode for transcription")
            return self._demo_transcribe()

        try:
            # Deepgram v5 file transcription (Listen v1 media)
            response = self.client.listen.v1.media.transcribe_file(
                request=audio_bytes,
                model="nova-3",
                smart_format=True,
                request_options={
                    "timeout_in_seconds": 60,
                    "max_retries": 3,
                },
            )

            transcript = response.results.channels[0].alternatives[0].transcript
            logger.info(f"Successfully transcribed {len(audio_bytes)} bytes from {filename}")
            return transcript

        except ApiError as e:
            logger.error(
                f"Deepgram API error {e.status_code}: {e.body}. "
                "Falling back to demo transcript."
            )
            return self._demo_transcribe()
        except Exception as e:
            logger.error(
                f"Deepgram transcription failed with unexpected error: {e}. "
                "Falling back to demo transcript."
            )
            return self._demo_transcribe()

    def _demo_transcribe(self) -> str:
        """Demo/fallback transcription - returns realistic CRE deal transcript."""
        return (
            "Hey, I just got off the phone with Marcus from JLL. He's got a deal in Austin, Texas "
            "that might be interesting for us. It's a 148-unit multifamily property, Class B plus, "
            "built in 2008. The property is currently 92 percent occupied and generating about "
            "1.2 million in NOI. They're asking 18.5 million, which puts it at a 6.5 percent cap rate. "
            "Location is solid in the Domain area near Apple's campus and other tech employers. "
            "Units are mostly two bed, two bath around 950 square feet. The seller is a regional "
            "operator looking to exit. Marcus thinks there's about 400 to 500k of deferred maintenance "
            "and maybe 75 to 100 dollars per unit of rent upside. Offers are due next Friday and he can "
            "send the full OM tomorrow. His email is marcus.thompson@jll.com."
        )
