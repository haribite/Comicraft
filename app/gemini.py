import json
import time

from google import genai

from app.config import settings
from app.models import Panel


def generate_panels(req):
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Put your real key in .env"
        )

    client = genai.Client(api_key=settings.gemini_api_key)

    prompt = f"""
Create exactly {settings.panel_count} panels for a comic.

Story:
{req.prompt}

Main character:
{req.character_name}

Setting:
{req.setting}

Tone:
{req.tone}

Art style:
{req.art_style}

Return ONLY valid JSON.

The JSON must be an array containing exactly {settings.panel_count} objects.

Each object MUST contain these fields:

panel_number
title
scene_description
caption
narration
dialogue
image_prompt

Rules:
- panel_number must be 1 through {settings.panel_count}
- Keep the same character throughout the story
- Make the story coherent from panel 1 to panel {settings.panel_count}
- Keep each scene visually descriptive
- Keep dialogue short
- Do not use markdown
- Do not use ```json
- Return JSON only
"""

    last_error = None

    # Retry temporary Gemini server errors.
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[Panel],
                },
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            data = json.loads(response.text)

            if not isinstance(data, list):
                raise RuntimeError(
                    "Gemini did not return a JSON array."
                )

            panels = [
                Panel.model_validate(item)
                for item in data
            ]

            if len(panels) != settings.panel_count:
                raise RuntimeError(
                    f"Gemini returned {len(panels)} panels. "
                    f"Expected {settings.panel_count}."
                )

            return panels

        except Exception as error:
            last_error = error
            error_text = str(error)

            print(
                f"Gemini attempt {attempt + 1}/3 failed: "
                f"{error_text}"
            )

            # Temporary Gemini capacity/server error.
            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "500" in error_text
                or "INTERNAL" in error_text
            ):
                if attempt < 2:
                    wait_seconds = 5 * (attempt + 1)

                    print(
                        f"Gemini is temporarily unavailable. "
                        f"Retrying in {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)
                    continue

            # Don't hide authentication, request, or validation errors.
            raise

    raise RuntimeError(
        "Gemini is temporarily unavailable after 3 attempts. "
        "Please try again shortly."
    ) from last_error