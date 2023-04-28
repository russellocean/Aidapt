from rich.console import Console
from rich.table import Table

console = Console()


def print_search_results(query, results):
    console.print(f"[bold yellow]Search query:[/bold yellow]\n{query}\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank")
    table.add_column("Function Name")
    table.add_column("Filepath")
    table.add_column("Distance")
    table.add_column("Code Snippet")

    for i, result in enumerate(results, start=1):
        function_name = result["document"]["function_name"]
        filepath = result["document"]["filepath"]
        distance = f"{result['distance']:.6f}"
        code = result["document"]["code"]

        table.add_row(str(i), function_name, filepath, distance, code)

    console.print("[bold yellow]Search results:[/bold yellow]")
    console.print(table)
