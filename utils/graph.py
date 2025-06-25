from datetime import datetime

from langchain_core.runnables.graph import MermaidDrawMethod


def save_graph_png(runnable, filepath: str = None):
    png_bytes = runnable.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.API
    )

    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"langgraph_{timestamp}.png"

    with open(filepath, "wb") as f:
        f.write(png_bytes)

    print(f"[Graph Saved] → {filepath}")