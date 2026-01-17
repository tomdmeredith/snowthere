"""
Test the full agent pipeline with Park City.

Usage:
    cd agents
    python -m scripts.test_pipeline

Or with UV:
    uv run python -m scripts.test_pipeline

Requires environment variables in .env file.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from generate_guide.agent import GenerateGuideAgent
from generate_guide.schemas import GenerateInput
from optimize_for_geo.agent import OptimizeForGeoAgent
from optimize_for_geo.schemas import OptimizeInput
from research_resort.agent import ResearchResortAgent
from research_resort.schemas import ResearchInput


async def test_full_pipeline():
    """Run the full pipeline for Park City as a test."""
    print("=" * 60)
    print("Snowthere Agent Pipeline Test")
    print("=" * 60)
    print()

    # Test resort: Park City, Utah
    resort_name = "Park City Mountain Resort"
    country = "USA"
    region = "Utah"

    task_id = f"test-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    # Step 1: Research
    print("Step 1: Research Resort")
    print("-" * 40)
    print(f"Researching: {resort_name}, {region}, {country}")
    print()

    research_agent = ResearchResortAgent(task_id=task_id)
    research_input = ResearchInput(
        resort_name=resort_name,
        country=country,
        region=region,
        focus_areas=["family", "costs", "logistics"],
    )

    try:
        research_output = await research_agent.research(research_input)
        print(f"✓ Research complete")
        print(f"  - Sources found: {len(research_output.sources)}")
        print(f"  - Confidence score: {research_output.confidence_score}")
        print(f"  - Errors: {len(research_output.errors)}")
        if research_output.errors:
            for error in research_output.errors[:3]:
                print(f"    - {error[:80]}...")
        print()
    except Exception as e:
        print(f"✗ Research failed: {e}")
        return

    # Step 2: Generate Content
    print("Step 2: Generate Guide Content")
    print("-" * 40)

    generate_agent = GenerateGuideAgent(task_id=task_id)
    generate_input = GenerateInput(
        research_data=research_output,
        voice_profile="instagram_mom",
        sections=[
            "quick_take",
            "getting_there",
            "where_to_stay",
            "lift_tickets",
            "on_mountain",
            "off_mountain",
        ],
    )

    try:
        generate_output = await generate_agent.generate(generate_input)
        print(f"✓ Content generated")
        print(f"  - Sections: {list(generate_output.sections.keys())}")
        print(f"  - FAQs: {len(generate_output.faqs)}")
        print(f"  - Total tokens: {generate_output.total_tokens_used}")
        print(f"  - Errors: {len(generate_output.errors)}")
        print()

        # Show quick take preview
        if generate_output.sections.get("quick_take"):
            preview = generate_output.sections["quick_take"][:300]
            print("  Quick Take Preview:")
            print(f"  {preview}...")
            print()
    except Exception as e:
        print(f"✗ Content generation failed: {e}")
        return

    # Step 3: GEO Optimization
    print("Step 3: GEO Optimization")
    print("-" * 40)

    optimize_agent = OptimizeForGeoAgent(task_id=task_id)
    optimize_input = OptimizeInput(
        resort_name=resort_name,
        country=country,
        region=region,
        generated_content=generate_output,
        basic_info=research_output.basic_info,
        family_metrics=research_output.family_metrics,
        costs=research_output.costs,
    )

    try:
        optimize_output = await optimize_agent.optimize(optimize_input)
        print(f"✓ GEO optimization complete")
        print(f"  - Tables generated: {len(optimize_output.tables)}")
        print(f"  - FAQ schema: {'Yes' if optimize_output.faq_schema else 'No'}")
        print(f"  - GEO Score: {optimize_output.geo_score.overall_score:.2f}")
        print(f"    - Tables: {optimize_output.geo_score.tables_score:.2f}")
        print(f"    - FAQs: {optimize_output.geo_score.faqs_score:.2f}")
        print(f"    - BLUF: {optimize_output.geo_score.bluf_score:.2f}")
        print()
    except Exception as e:
        print(f"✗ GEO optimization failed: {e}")
        return

    # Save output to file for inspection
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"test-{resort_name.lower().replace(' ', '-')}.json"
    output_data = {
        "resort_name": resort_name,
        "country": country,
        "region": region,
        "task_id": task_id,
        "research": {
            "confidence": research_output.confidence_score,
            "sources_count": len(research_output.sources),
            "errors": research_output.errors,
        },
        "content": {
            "sections": list(generate_output.sections.keys()),
            "faqs_count": len(generate_output.faqs),
            "tokens_used": generate_output.total_tokens_used,
        },
        "geo": {
            "tables_count": len(optimize_output.tables),
            "geo_score": optimize_output.geo_score.model_dump(),
        },
        "generated_at": datetime.utcnow().isoformat(),
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print("=" * 60)
    print("Pipeline Test Complete!")
    print("=" * 60)
    print(f"Output saved to: {output_file}")
    print()

    # Summary
    print("Summary:")
    print(f"  Resort: {resort_name}")
    print(f"  Research confidence: {research_output.confidence_score:.2f}")
    print(f"  Content sections: {len(generate_output.sections)}")
    print(f"  GEO score: {optimize_output.geo_score.overall_score:.2f}")
    print()


async def test_research_only():
    """Quick test of just the research agent."""
    print("Quick Research Test")
    print("-" * 40)

    agent = ResearchResortAgent()
    input_data = ResearchInput(
        resort_name="Zermatt",
        country="Switzerland",
    )

    result = await agent.research(input_data)

    print(f"Resort: {result.resort_name}, {result.country}")
    print(f"Sources: {len(result.sources)}")
    print(f"Confidence: {result.confidence_score}")
    print(f"Errors: {len(result.errors)}")

    if result.sources:
        print("\nTop sources:")
        for source in result.sources[:5]:
            print(f"  - {source.title or source.url[:50]}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        asyncio.run(test_research_only())
    else:
        asyncio.run(test_full_pipeline())
