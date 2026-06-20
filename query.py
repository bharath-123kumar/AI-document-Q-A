import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from src.utils import get_chroma_dir, get_top_k, get_gemini_api_key
from src.embedder import Embedder
from src.vector_store import VectorStore
from src.retriever import Retriever
from src.generator import Generator

def main():
    console = Console()
    console.print("[bold green]============================================================[/bold green]")
    console.print("[bold green]      RAG Document Q&A Bot — CLI Interactive Session        [/bold green]")
    console.print("[bold green]============================================================[/bold green]")

    # Check API key first
    api_key = get_gemini_api_key()
    if not api_key:
        console.print("[bold red]WARNING: GOOGLE_API_KEY environment variable not found.[/bold red]")
        console.print("Please create a [yellow].env[/yellow] file or set the environment variable.")
        console.print("Answers will fail to generate without an API key, but retrieval will still work.\n")

    # Initialize RAG components
    chroma_dir = get_chroma_dir()
    vector_store = VectorStore(chroma_dir)
    
    # Check if vector DB has documents
    vector_count = vector_store.count()
    if vector_count == 0:
        console.print("[bold red]Error: The vector database is empty.[/bold red]")
        console.print("Please run [yellow]python index.py[/yellow] first to index your documents.\n")
        sys.exit(1)

    console.print(f"[green]Vector database loaded successfully ([white]{vector_count} chunks[/white]).[/green]")
    
    # Initialize embedder, retriever, generator
    embedder = Embedder()
    retriever = Retriever(embedder, vector_store)
    generator = Generator()
    
    top_k = get_top_k()
    console.print(f"Configured to retrieve [cyan]top-{top_k}[/cyan] matching document chunks.\n")
    console.print("Type [bold yellow]exit[/bold yellow] or [bold yellow]quit[/bold yellow] to end the session.\n")

    while True:
        try:
            query = Prompt.ask("[bold blue]Ask a question[/bold blue]")
            if query.strip().lower() in ["exit", "quit"]:
                console.print("\n[bold green]Goodbye![/bold green]")
                break
            
            if not query.strip():
                continue

            with console.status("[bold yellow]Retrieving relevant context...[/bold yellow]"):
                results = retriever.retrieve(query, top_k=top_k)

            if not results:
                console.print("[bold red]No matching context found in the vector database.[/bold red]\n")
                continue

            # Display source chunks matching query
            console.print("\n[bold cyan]── Retrieved Chunks ──────────────────────────────────────────[/bold cyan]")
            for i, res in enumerate(results):
                source_info = f"Source: {res['source']} (Page/Section: {res['page']}) | Similarity: {res['score']:.4f}"
                console.print(f"[bold yellow]Chunk {i+1} ({source_info})[/bold yellow]")
                console.print(f"[dim]{res['text'][:200]}...[/dim]\n")
            
            # Generate answer using LLM
            with console.status("[bold green]Generating answer using Google Gemini...[/bold green]"):
                answer, _ = generator.generate_answer(query, results)

            console.print(Panel(Markdown(answer), title="[bold green]AI Answer[/bold green]", border_style="green"))
            console.print("\n" + "═"*60 + "\n")

        except KeyboardInterrupt:
            console.print("\n[bold green]Goodbye![/bold green]")
            break
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]\n")

if __name__ == "__main__":
    main()
