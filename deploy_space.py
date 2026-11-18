import os

APP_FILES = [
    "gradio_app.py",
    "agent.py",
    "agent_graph.py",
    "tools.py",
    "guard.py",
    "rag.py",
    "doc_loader.py",
    "requirements.txt",
    "README.md",
    "cars_knowledge.txt",
    "docs/*",
]


def main():
    from huggingface_hub import HfApi

    HfApi(token=os.environ.get("HF_TOKEN")).upload_folder(
        folder_path=".",
        repo_id="ksufian/ai-car-assistant",
        repo_type="space",
        allow_patterns=APP_FILES,
        commit_message=f"Deploy {os.environ.get('GITHUB_SHA', 'local')[:7]} from GitHub",
    )
    print("Deployed:", ", ".join(APP_FILES))


if __name__ == "__main__":
    main()