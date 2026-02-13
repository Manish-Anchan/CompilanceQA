from langgraph.graph import StateGraph, END
from backend.src.graph.state import VideoAuditState

from backend.src.graph.nodes import (
    index_video_node,
    audit_content_node
)

def create_graph():
    """
    Constructs and compiles the LangGraph workflow.

    Returns:
        CompiledGraph: A runnable graph object ready for execution.
    """
    workflow = StateGraph(VideoAuditState)

    workflow.add_node("indexer", index_video_node)
    workflow.add_node("auditor", audit_content_node)

    workflow.set_entry_point("indexer")

    workflow.add_edge("indexer", "auditor")
    workflow.add_edge("auditor", END)

    app = workflow.compile()

    return app
app = create_graph()