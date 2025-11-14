"""
Deepgram client for speech-to-text transcription
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DeepgramClient:
    """Client for Deepgram speech-to-text API"""

    def __init__(self, api_key: Optional[str] = None, demo_mode: bool = False):
        self.api_key = api_key
        self.demo_mode = demo_mode
        self.client = None

        if api_key and not demo_mode:
            try:
                from deepgram import DeepgramClient as DG
                self.client = DG(api_key)
                logger.info("Deepgram client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Deepgram client: {e}. Falling back to demo mode.")
                self.demo_mode = True

    def transcribe_bytes(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """
        Transcribe audio bytes to text

        Args:
            audio_bytes: Audio file bytes
            filename: Original filename (used to determine mime type)

        Returns:
            Transcribed text
        """
        if self.demo_mode or not self.client:
            logger.info("Using demo mode for transcription")
            return self._demo_transcribe()

        try:
            # Determine mime type from extension
            mime_type = "audio/wav"
            if filename.lower().endswith(".mp3"):
                mime_type = "audio/mp3"
            elif filename.lower().endswith(".m4a"):
                mime_type = "audio/mp4"
            elif filename.lower().endswith(".flac"):
                mime_type = "audio/flac"

            # Use Deepgram API
            response = self.client.listen.rest.v("1").transcribe_file(
                {"buffer": audio_bytes, "mimetype": mime_type},
                {
                    "model": "nova-2",
                    "smart_format": True,
                    "punctuate": True,
                    "paragraphs": True
                }
            )

            # Extract transcript
            transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
            logger.info(f"Successfully transcribed {len(audio_bytes)} bytes")
            return transcript

        except Exception as e:
            logger.error(f"Deepgram transcription failed: {e}. Falling back to demo mode.")
            return self._demo_transcribe()

    def _demo_transcribe(self) -> str:
        """Demo/fallback transcription - returns realistic CRE deal transcript"""
        return """Hey, I just got off the phone with Marcus from JLL. He's got a deal in Austin, Texas
that might be interesting for us. It's a 148-unit multifamily property, Class B plus, built in 2008.
The property is currently 92% occupied and generating about $1.2 million in NOI.

They're asking $18.5 million, which puts it at a 6.5% cap rate. Location is solid - it's in the
Domain area, close to Apple's campus and a bunch of other tech companies. Units are mostly
two-bedroom, two-bath layouts, averaging around 950 square feet.

The seller is a regional operator looking to exit and redeploy capital. Marcus mentioned there's
some deferred maintenance, maybe $400K to $500K to get it to where we'd want it. Rents are
slightly below market - he thinks there's opportunity to push another $75 to $100 per unit.

They're looking for offers by next Friday. Marcus's email is marcus.thompson at jll.com. He said
he can get us the full OM by tomorrow if we're interested. Let me know if you want me to dig deeper."""
