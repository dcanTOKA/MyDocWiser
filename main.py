from pathlib import Path
import gradio as gr
import asyncio
import gc

from utils.report import (
    list_markdown_titles,
    load_markdown_content,
    save_markdown_report,
    delete_markdown_report
)
from services.retrieve.graph.rag_graph import build_rag_graph
from langgraph.checkpoint.memory import MemorySaver
from db import init_db


async def run_graph_query(user_query: str, scrape_docs_link: str) -> str:
    await init_db()

    memory = MemorySaver()
    graph = build_rag_graph().compile(checkpointer=memory)

    initial_state = {
        "user_query": user_query,
        "chat_history": [],
        "scrape_docs_link": scrape_docs_link
    }

    response = await graph.ainvoke(
        input=initial_state,
        config={"configurable": {"thread_id": "demo-thread-001"}}
    )

    md_path = save_markdown_report(response)
    gc.collect()
    await asyncio.sleep(0.1)
    return Path(md_path).read_text(encoding="utf-8")


def launch_gradio_app():
    with gr.Blocks(title="ApiDocWiser") as demo:

        with gr.Row():
            with gr.Column(scale=1, min_width=200):
                gr.Markdown("## Past Questions")
                past_queries = gr.Radio(
                    choices=list_markdown_titles(),
                    label="Past",
                    interactive=True
                )
                new_chat_btn = gr.Button("➕ New Chat")
                delete_btn = gr.Button("🗑️ Delete", visible=False)
                delete_status = gr.Markdown(visible=False)

            with gr.Column(scale=3):
                with gr.Column(visible=True) as chat_input_area:
                    scrape_docs_link = gr.Textbox(
                        placeholder="Enter docs link (e.g., https://docs.tavily.com)",
                        label="Documentation Link",
                        value="",
                        lines=1
                    )
                    user_input = gr.Textbox(
                        placeholder="Ask your API-related question...",
                        show_label=False
                    )
                    run_status = gr.Markdown(visible=False)

                past_view = gr.Markdown(visible=False)
                answer_output = gr.Markdown(visible=False)

        def handle_submit(query, link):
            if not link:
                return (
                    gr.update(visible=False),
                    gr.update(value="⚠️ Please enter a documentation link.", visible=True)
                )
            return (
                gr.update(visible=False),
                gr.update(value="⏳ Processing, please wait...", visible=True)
            )

        user_input.submit(
            fn=handle_submit,
            inputs=[user_input, scrape_docs_link],
            outputs=[answer_output, run_status]
        ).then(
            fn=lambda query, link: asyncio.run(run_graph_query(query, link)),
            inputs=[user_input, scrape_docs_link],
            outputs=answer_output
        ).then(
            fn=lambda: gr.update(visible=False),
            outputs=run_status
        ).then(
            fn=lambda: gr.update(visible=True),
            outputs=answer_output
        ).then(
            fn=lambda: gr.update(choices=list_markdown_titles()),
            outputs=past_queries
        )

        def on_past_selected(title):
            if not title:
                return (
                    gr.update(value="", visible=False),
                    gr.update(visible=False),
                    gr.update(visible=True),
                    gr.update(visible=False),
                    gr.update(value="", visible=False),
                )

            content = load_markdown_content(title)
            return (
                gr.update(value=content, visible=True),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(value="", visible=False),
            )

        past_queries.change(
            fn=on_past_selected,
            inputs=past_queries,
            outputs=[past_view, answer_output, chat_input_area, delete_btn, delete_status]
        )

        def on_new_chat():
            return (
                gr.update(visible=True),
                gr.update(value="", visible=True),
                gr.update(value="", visible=True),
                gr.update(visible=False),
                gr.update(value="", visible=False),
                gr.update(visible=False)
            )

        new_chat_btn.click(
            fn=on_new_chat,
            outputs=[
                chat_input_area,
                user_input,
                scrape_docs_link,
                past_view,
                answer_output,
                delete_btn
            ]
        )

        def on_delete(selected_filename):
            success = delete_markdown_report(selected_filename)
            if success:
                updated_choices = list_markdown_titles()
                return (
                    gr.update(choices=updated_choices, value=None),
                    gr.update(visible=False),
                    gr.update(value="", visible=False),
                    gr.update(value="", visible=False),
                    gr.update(value="✅ Chat deleted successfully.", visible=True)
                )
            else:
                return (
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(value="❌ Chat could not be deleted.", visible=True)
                )

        delete_btn.click(
            fn=on_delete,
            inputs=past_queries,
            outputs=[past_queries, past_view, answer_output, chat_input_area, delete_status]
        )

    demo.launch()


if __name__ == "__main__":
    launch_gradio_app()
