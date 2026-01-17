"""
Run Snowthere agents.

Usage:
    # Run all agents on different ports
    python run.py all

    # Run individual agents
    python run.py research    # Port 8001
    python run.py generate    # Port 8002
    python run.py optimize    # Port 8003

    # Or with UV
    uv run python run.py research
"""

import sys

import uvicorn


def run_research():
    """Run research_resort agent on port 8001."""
    from research_resort.main import app
    uvicorn.run(app, host="0.0.0.0", port=8001)


def run_generate():
    """Run generate_guide agent on port 8002."""
    from generate_guide.main import app
    uvicorn.run(app, host="0.0.0.0", port=8002)


def run_optimize():
    """Run optimize_for_geo agent on port 8003."""
    from optimize_for_geo.main import app
    uvicorn.run(app, host="0.0.0.0", port=8003)


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [research|generate|optimize|all]")
        print()
        print("Agents:")
        print("  research  - Research resort data (port 8001)")
        print("  generate  - Generate guide content (port 8002)")
        print("  optimize  - GEO optimization (port 8003)")
        print("  all       - Run all agents (requires multiprocessing)")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "research":
        run_research()
    elif command == "generate":
        run_generate()
    elif command == "optimize":
        run_optimize()
    elif command == "all":
        # For running all agents, use separate terminals or docker-compose
        print("To run all agents, start each in a separate terminal:")
        print("  python run.py research")
        print("  python run.py generate")
        print("  python run.py optimize")
        print()
        print("Or use the Procfile for Railway deployment.")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
