"""Image generation primitives with 3-tier fallback chain.

Following Agent Native principles, these primitives provide robust image
generation capabilities with automatic failover between providers.

Tier 1 (Primary): Google Gemini - Fast, cheap (~$0.002)
Tier 2 (Backup): Glif Nano Banana Pro - High quality (~$0.01)
Tier 3 (Tertiary): Replicate Flux Schnell - Reliable fallback (~$0.003)

Key Design: NO CLOSE-UP FACES
All prompts explicitly avoid faces to prevent AI uncanny valley:
- Distant silhouettes on slopes
- Atmosphere shots (hot chocolate, gear, lodge)
- Landscapes with tiny figures
- NO close-up faces (especially children)
"""

import base64
import io
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import httpx

from ..config import settings
from ..supabase_client import get_supabase_client
from .system import log_cost, log_reasoning


# =============================================================================
# DATA CLASSES & ENUMS
# =============================================================================


class ImageType(str, Enum):
    """Types of images we generate for resorts."""

    HERO = "hero"  # Main resort hero image
    ATMOSPHERE = "atmosphere"  # Lodge/cozy scenes
    ACTIVITY = "activity"  # Ski school, families on slopes
    LANDSCAPE = "landscape"  # Mountain vistas


class ImageProvider(str, Enum):
    """Image generation providers in fallback order."""

    GEMINI = "gemini"
    GLIF = "glif"
    REPLICATE = "replicate"
    OFFICIAL = "official"  # Scraped from resort


class AspectRatio(str, Enum):
    """Supported aspect ratios."""

    SQUARE = "1:1"  # 1024x1024 - Instagram, LinkedIn
    LANDSCAPE = "16:9"  # 1280x720 - Hero banners, YouTube
    PORTRAIT = "4:5"  # 1024x1280 - Instagram feed
    WIDE = "21:9"  # 2560x1080 - Cinematic headers


@dataclass
class ImageResult:
    """Result from image generation."""

    success: bool
    url: str | None = None
    source: ImageProvider | None = None
    prompt_used: str | None = None
    aspect_ratio: str | None = None
    alt_text: str | None = None
    cost: float = 0.0
    error: str | None = None
    metadata: dict | None = None


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================


# Vibe-based prompt templates for ski resort imagery
VIBE_PROMPTS = {
    "european_alpine": """
        A serene European Alpine ski village at golden hour. Traditional wooden
        chalets with snow-covered roofs. Dramatic mountain peaks catching warm
        sunlight. Fresh powder on the slopes. Editorial travel photography,
        natural lighting, wide angle, no visible faces.
    """,
    "american_rockies": """
        Modern Rocky Mountain ski resort under brilliant blue skies. Contemporary
        lodge architecture with towering pine forests. Fresh powder on open bowls.
        Professional travel photography, wide angle, bright natural light,
        no visible faces.
    """,
    "family_atmosphere": """
        Cozy ski lodge interior with warm wood paneling. Hot chocolate mugs on
        rustic table, ski gear visible in background. Fireplace glow creating
        warm ambiance. Lifestyle photography, shallow depth of field, inviting
        warmth, no visible faces.
    """,
    "ski_school": """
        Colorful children's ski equipment lined up in snow, small figures in
        distance on gentle slope. Magic carpet lift visible. Bright sunny day,
        cheerful atmosphere. Professional photography, wide shot, distant
        silhouettes only, no close faces.
    """,
    "apres_ski": """
        Outdoor terrace of ski lodge with mountain views. Comfortable seating
        with warm blankets, drinks on table. Late afternoon golden light on
        snow-capped peaks. Lifestyle photography, warm inviting tones,
        no visible faces.
    """,
    "powder_day": """
        Fresh untouched powder snow on mountain slope. Distant tiny skier
        silhouette leaving tracks. Dramatic mountain backdrop, blue sky,
        sparkling snow. Professional ski photography, wide landscape,
        no close faces.
    """,
}


def get_resort_prompt(
    resort_name: str,
    country: str,
    image_type: ImageType,
    custom_elements: str | None = None,
) -> str:
    """Generate an optimized prompt for a resort image.

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located
        image_type: Type of image to generate
        custom_elements: Optional custom elements to include

    Returns:
        Optimized prompt string
    """
    # Determine vibe based on country/region
    if country.lower() in ["austria", "switzerland", "france", "italy", "germany"]:
        base_vibe = "european_alpine"
    elif country.lower() in ["usa", "canada"]:
        base_vibe = "american_rockies"
    else:
        base_vibe = "european_alpine"  # Default to European aesthetic

    # Select base prompt by image type
    type_vibes = {
        ImageType.HERO: base_vibe,
        ImageType.ATMOSPHERE: "family_atmosphere",
        ImageType.ACTIVITY: "ski_school",
        ImageType.LANDSCAPE: "powder_day",
    }

    base_prompt = VIBE_PROMPTS.get(type_vibes.get(image_type, base_vibe), "")

    # Build final prompt
    prompt_parts = [
        f"Ski resort {resort_name} in {country}.",
        base_prompt.strip(),
        "Ultra-detailed, professional quality, magazine editorial style.",
        "IMPORTANT: No close-up faces, only distant silhouettes if any people.",
    ]

    if custom_elements:
        prompt_parts.insert(2, custom_elements)

    return " ".join(prompt_parts)


# =============================================================================
# PROVIDER IMPLEMENTATIONS
# =============================================================================


async def generate_with_gemini(
    prompt: str,
    aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
    use_pro_model: bool = False,
) -> ImageResult:
    """Tier 1: Generate image using Google Gemini.

    Two model options:
    - gemini-2.5-flash-image: Fast, efficient, high-volume (~$0.002)
    - gemini-3-pro-image-preview: Professional production with advanced reasoning (~$0.01)

    Cost: ~$0.002-$0.01 per image
    Speed: ~20 seconds
    Quality: Excellent
    """
    if not settings.google_api_key:
        return ImageResult(
            success=False,
            error="GOOGLE_API_KEY not configured",
        )

    try:
        # Import the official google-genai SDK
        from google import genai
        from google.genai import types

        # Initialize client with API key
        client = genai.Client(api_key=settings.google_api_key)

        # Select model based on quality needs
        # - Flash: Fast, cheap, good for high volume
        # - Pro: Professional assets, complex instructions, better text
        model_name = "gemini-3-pro-image-preview" if use_pro_model else "gemini-2.5-flash-image"
        cost = 0.01 if use_pro_model else 0.002

        # Map aspect ratio to Gemini format
        aspect_map = {
            AspectRatio.SQUARE: "1:1",
            AspectRatio.LANDSCAPE: "16:9",
            AspectRatio.PORTRAIT: "9:16",
            AspectRatio.WIDE: "16:9",  # Gemini doesn't support 21:9, closest match
        }
        gemini_aspect = aspect_map.get(aspect_ratio, "16:9")

        # Generate image using the official SDK
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=gemini_aspect),
            ),
        )

        # Extract image from response parts
        for part in response.parts:
            if part.inline_data is not None:
                # Get raw image bytes
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/png"

                # Upload to Supabase Storage
                image_url = await upload_image_to_storage(
                    image_data=image_bytes,
                    mime_type=mime_type,
                    provider=ImageProvider.GEMINI,
                )

                if image_url:
                    return ImageResult(
                        success=True,
                        url=image_url,
                        source=ImageProvider.GEMINI,
                        prompt_used=prompt,
                        aspect_ratio=gemini_aspect,
                        cost=cost,
                        metadata={"model": model_name},
                    )

        return ImageResult(
            success=False,
            error="No image data in Gemini response",
        )

    except ImportError:
        return ImageResult(
            success=False,
            error="google-genai package not installed. Run: pip install google-genai",
        )

    except Exception as e:
        return ImageResult(
            success=False,
            error=f"Gemini generation failed: {str(e)}",
        )


async def generate_with_glif(
    prompt: str,
    aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
) -> ImageResult:
    """Tier 2: Generate image using Glif Nano Banana Pro.

    Cost: ~$0.01 per image
    Speed: ~20 seconds
    Quality: Excellent
    Glif ID: cmi7ne4p40000kz04yup2nxgh
    """
    if not settings.glif_api_key:
        return ImageResult(
            success=False,
            error="GLIF_API_KEY not configured",
        )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://simple-api.glif.app",
                json={
                    "id": "cmi7ne4p40000kz04yup2nxgh",  # Nano Banana Pro
                    "inputs": [prompt],
                },
                headers={
                    "Authorization": f"Bearer {settings.glif_api_key}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code != 200:
                return ImageResult(
                    success=False,
                    error=f"Glif API error: {response.status_code}",
                )

            data = response.json()

            # Glif returns the image URL directly
            image_url = data.get("output")
            if not image_url:
                return ImageResult(
                    success=False,
                    error="No image URL in Glif response",
                )

            # Download and re-upload to our storage for persistence
            async with httpx.AsyncClient() as dl_client:
                img_response = await dl_client.get(image_url)
                if img_response.status_code == 200:
                    stored_url = await upload_image_to_storage(
                        image_data=img_response.content,
                        mime_type="image/png",
                        provider=ImageProvider.GLIF,
                    )
                    if stored_url:
                        image_url = stored_url

            return ImageResult(
                success=True,
                url=image_url,
                source=ImageProvider.GLIF,
                prompt_used=prompt,
                aspect_ratio="1:1",  # Nano Banana Pro outputs square
                cost=0.01,
            )

    except Exception as e:
        return ImageResult(
            success=False,
            error=f"Glif generation failed: {str(e)}",
        )


async def generate_with_replicate(
    prompt: str,
    aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
) -> ImageResult:
    """Tier 3: Generate image using Replicate Flux Schnell.

    Cost: ~$0.003 per image
    Speed: ~30 seconds
    Quality: Good
    """
    if not settings.replicate_api_token:
        return ImageResult(
            success=False,
            error="REPLICATE_API_TOKEN not configured",
        )

    try:
        # Map aspect ratio to Replicate format
        aspect_map = {
            AspectRatio.SQUARE: "1:1",
            AspectRatio.LANDSCAPE: "16:9",
            AspectRatio.PORTRAIT: "9:16",
            AspectRatio.WIDE: "21:9",
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Create prediction
            response = await client.post(
                "https://api.replicate.com/v1/predictions",
                headers={
                    "Authorization": f"Token {settings.replicate_api_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "version": "black-forest-labs/flux-schnell",
                    "input": {
                        "prompt": prompt,
                        "aspect_ratio": aspect_map.get(aspect_ratio, "16:9"),
                        "num_outputs": 1,
                        "output_format": "png",
                    },
                },
            )

            if response.status_code != 201:
                return ImageResult(
                    success=False,
                    error=f"Replicate API error: {response.status_code}",
                )

            prediction = response.json()
            prediction_id = prediction.get("id")

            # Poll for completion
            max_attempts = 60
            for _ in range(max_attempts):
                status_response = await client.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers={
                        "Authorization": f"Token {settings.replicate_api_token}",
                    },
                )

                status_data = status_response.json()
                status = status_data.get("status")

                if status == "succeeded":
                    output = status_data.get("output", [])
                    if output:
                        image_url = output[0]

                        # Download and re-upload to our storage
                        img_response = await client.get(image_url)
                        if img_response.status_code == 200:
                            stored_url = await upload_image_to_storage(
                                image_data=img_response.content,
                                mime_type="image/png",
                                provider=ImageProvider.REPLICATE,
                            )
                            if stored_url:
                                image_url = stored_url

                        return ImageResult(
                            success=True,
                            url=image_url,
                            source=ImageProvider.REPLICATE,
                            prompt_used=prompt,
                            aspect_ratio=aspect_map.get(aspect_ratio, "16:9"),
                            cost=0.003,
                        )

                elif status == "failed":
                    return ImageResult(
                        success=False,
                        error=f"Replicate prediction failed: {status_data.get('error')}",
                    )

                # Wait before polling again
                import asyncio
                await asyncio.sleep(2)

            return ImageResult(
                success=False,
                error="Replicate prediction timed out",
            )

    except Exception as e:
        return ImageResult(
            success=False,
            error=f"Replicate generation failed: {str(e)}",
        )


# =============================================================================
# STORAGE
# =============================================================================


async def upload_image_to_storage(
    image_data: bytes,
    mime_type: str,
    provider: ImageProvider,
) -> str | None:
    """Upload image to Supabase Storage.

    Args:
        image_data: Raw image bytes
        mime_type: MIME type (e.g., 'image/png')
        provider: Which provider generated this image

    Returns:
        Public URL of uploaded image, or None if failed
    """
    try:
        client = get_supabase_client()

        # Generate unique filename
        ext = "png" if "png" in mime_type else "jpg"
        filename = f"{provider.value}/{uuid.uuid4()}.{ext}"

        # Upload to resort-images bucket
        result = client.storage.from_("resort-images").upload(
            filename,
            image_data,
            file_options={"content-type": mime_type},
        )

        # Get public URL
        url = client.storage.from_("resort-images").get_public_url(filename)
        return url

    except Exception as e:
        # Storage upload failed - return None, caller will use original URL
        print(f"Storage upload failed: {e}")
        return None


# =============================================================================
# MAIN FALLBACK FUNCTION
# =============================================================================


def provider_configured(provider: ImageProvider) -> bool:
    """Check if a provider is configured with API keys."""
    if provider == ImageProvider.GEMINI:
        return bool(settings.google_api_key)
    elif provider == ImageProvider.GLIF:
        return bool(settings.glif_api_key)
    elif provider == ImageProvider.REPLICATE:
        return bool(settings.replicate_api_token)
    return False


async def generate_image_with_fallback(
    prompt: str,
    aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE,
    task_id: str | None = None,
) -> ImageResult:
    """Generate image with automatic 3-tier provider fallback.

    Tries providers in order: Gemini → Glif → Replicate
    Skips providers that aren't configured.

    Args:
        prompt: Image generation prompt
        aspect_ratio: Desired aspect ratio
        task_id: Optional task ID for audit logging

    Returns:
        ImageResult with generated image URL or error
    """
    providers = [
        ("gemini", generate_with_gemini),
        ("glif", generate_with_glif),
        ("replicate", generate_with_replicate),
    ]

    errors = []

    for name, func in providers:
        provider_enum = ImageProvider(name)

        if not provider_configured(provider_enum):
            continue  # Skip unconfigured providers

        if task_id:
            log_reasoning(
                task_id=task_id,
                agent_name="image_generator",
                action="attempt_generation",
                reasoning=f"Attempting image generation with {name}",
                metadata={"provider": name, "prompt_length": len(prompt)},
            )

        try:
            result = await func(prompt, aspect_ratio)

            if result.success:
                # Log the cost
                log_cost(
                    api_name=f"image_{name}",
                    amount_usd=result.cost,
                    metadata={
                        "operation": "image_generation",
                        "prompt": prompt[:100],
                        "aspect_ratio": aspect_ratio.value,
                    },
                )

                if task_id:
                    log_reasoning(
                        task_id=task_id,
                        agent_name="image_generator",
                        action="generation_success",
                        reasoning=f"Successfully generated image with {name}",
                        metadata={
                            "provider": name,
                            "url": result.url,
                            "cost": result.cost,
                        },
                    )

                return result
            else:
                errors.append(f"{name}: {result.error}")

        except Exception as e:
            errors.append(f"{name}: {str(e)}")

        if task_id:
            log_reasoning(
                task_id=task_id,
                agent_name="image_generator",
                action="provider_failed",
                reasoning=f"Image generation failed with {name}, trying next...",
                metadata={"provider": name, "error": errors[-1]},
            )

    # All providers failed
    return ImageResult(
        success=False,
        error=f"All providers failed: {'; '.join(errors)}",
    )


# =============================================================================
# RESORT-SPECIFIC IMAGE GENERATION
# =============================================================================


async def generate_resort_hero_image(
    resort_name: str,
    country: str,
    task_id: str | None = None,
) -> ImageResult:
    """Generate hero image for a resort.

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located
        task_id: Optional task ID for audit logging

    Returns:
        ImageResult with hero image URL
    """
    prompt = get_resort_prompt(
        resort_name=resort_name,
        country=country,
        image_type=ImageType.HERO,
    )

    result = await generate_image_with_fallback(
        prompt=prompt,
        aspect_ratio=AspectRatio.LANDSCAPE,
        task_id=task_id,
    )

    if result.success:
        result.alt_text = f"Scenic view of {resort_name} ski resort in {country}"

    return result


async def generate_resort_atmosphere_image(
    resort_name: str,
    country: str,
    vibe: str = "family_atmosphere",
    task_id: str | None = None,
) -> ImageResult:
    """Generate atmosphere/lifestyle image for a resort.

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located
        vibe: Which vibe template to use
        task_id: Optional task ID for audit logging

    Returns:
        ImageResult with atmosphere image URL
    """
    base_prompt = VIBE_PROMPTS.get(vibe, VIBE_PROMPTS["family_atmosphere"])
    prompt = f"{resort_name} in {country}. {base_prompt.strip()} Professional quality, no visible faces."

    result = await generate_image_with_fallback(
        prompt=prompt,
        aspect_ratio=AspectRatio.SQUARE,
        task_id=task_id,
    )

    if result.success:
        result.alt_text = f"Cozy atmosphere at {resort_name} ski resort"

    return result


# =============================================================================
# DATABASE OPERATIONS
# =============================================================================


def save_resort_image(
    resort_id: str,
    image_type: ImageType,
    image_url: str,
    source: ImageProvider,
    prompt: str | None = None,
    alt_text: str | None = None,
) -> dict | None:
    """Save image metadata to database.

    Args:
        resort_id: UUID of the resort
        image_type: Type of image (hero, atmosphere, etc.)
        image_url: URL of the stored image
        source: Which provider generated this
        prompt: The prompt used (for reference)
        alt_text: Alt text for accessibility

    Returns:
        Created record or None
    """
    try:
        client = get_supabase_client()

        response = (
            client.table("resort_images")
            .insert({
                "resort_id": resort_id,
                "image_type": image_type.value,
                "image_url": image_url,
                "source": source.value,
                "prompt": prompt,
                "alt_text": alt_text,
                "created_at": datetime.utcnow().isoformat(),
            })
            .execute()
        )

        return response.data[0] if response.data else None

    except Exception as e:
        print(f"Failed to save image: {e}")
        return None


def get_resort_images(
    resort_id: str,
    image_type: ImageType | None = None,
) -> list[dict]:
    """Get images for a resort.

    Args:
        resort_id: UUID of the resort
        image_type: Optional filter by type

    Returns:
        List of image records
    """
    try:
        client = get_supabase_client()

        query = client.table("resort_images").select("*").eq("resort_id", resort_id)

        if image_type:
            query = query.eq("image_type", image_type.value)

        response = query.order("created_at", desc=True).execute()

        return response.data or []

    except Exception:
        return []


def get_resort_hero_image(resort_id: str) -> dict | None:
    """Get the hero image for a resort.

    Args:
        resort_id: UUID of the resort

    Returns:
        Most recent hero image record or None
    """
    images = get_resort_images(resort_id, ImageType.HERO)
    return images[0] if images else None


def delete_resort_images(
    resort_id: str,
    image_type: ImageType | None = None,
) -> int:
    """Delete images for a resort.

    Args:
        resort_id: UUID of the resort
        image_type: Optional filter by type

    Returns:
        Number of images deleted
    """
    try:
        client = get_supabase_client()

        query = client.table("resort_images").delete().eq("resort_id", resort_id)

        if image_type:
            query = query.eq("image_type", image_type.value)

        response = query.execute()

        return len(response.data) if response.data else 0

    except Exception:
        return 0


# =============================================================================
# BATCH OPERATIONS
# =============================================================================


async def generate_resort_image_set(
    resort_id: str,
    resort_name: str,
    country: str,
    task_id: str | None = None,
) -> dict[str, ImageResult]:
    """Generate a full set of images for a resort.

    Generates: hero + atmosphere images.

    Args:
        resort_id: UUID of the resort
        resort_name: Name of the ski resort
        country: Country where resort is located
        task_id: Optional task ID for audit logging

    Returns:
        Dict mapping image type to result
    """
    results = {}

    # Generate hero image
    hero_result = await generate_resort_hero_image(
        resort_name=resort_name,
        country=country,
        task_id=task_id,
    )
    results["hero"] = hero_result

    if hero_result.success:
        save_resort_image(
            resort_id=resort_id,
            image_type=ImageType.HERO,
            image_url=hero_result.url,
            source=hero_result.source,
            prompt=hero_result.prompt_used,
            alt_text=hero_result.alt_text,
        )

    # Generate atmosphere image
    atmosphere_result = await generate_resort_atmosphere_image(
        resort_name=resort_name,
        country=country,
        task_id=task_id,
    )
    results["atmosphere"] = atmosphere_result

    if atmosphere_result.success:
        save_resort_image(
            resort_id=resort_id,
            image_type=ImageType.ATMOSPHERE,
            image_url=atmosphere_result.url,
            source=atmosphere_result.source,
            prompt=atmosphere_result.prompt_used,
            alt_text=atmosphere_result.alt_text,
        )

    return results
