import oracledb
import os
import time
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

# Database configuration
DB_USER = os.getenv("DB_USER", "select_ai")
DB_PASS = os.getenv("DB_PASS", "oracle123")
DB_DSN  = os.getenv("DB_DSN", "localhost:1521/freepdb1")

def get_stats():
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute("SELECT count(*) FROM PRODUCTS")
        prods = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM CUSTOMER_REVIEWS")
        revs = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM CUSTOMER_REVIEWS WHERE VECTOR_CONTENT IS NOT NULL")
        vectors = cursor.fetchone()[0]
        
        # Get Index Status (New)
        index_pct = 0
        index_stage = "Waiting..."
        try:
            # Oracle 26ai internal status check
            cursor.execute("SET SERVEROUTPUT ON")
            # We capture DBMS_OUTPUT
            cursor.callproc("dbms_output.enable", (None,))
            cursor.execute("BEGIN DBMS_VECTOR.GET_INDEX_STATUS('SELECT_AI', 'IDX_REVIEW_VECTORS'); END;")
            
            lines = []
            line_var = cursor.var(str)
            status_var = cursor.var(int)
            while True:
                cursor.callproc("dbms_output.get_line", (line_var, status_var))
                if status_var.getvalue() != 0:
                    break
                lines.append(line_var.getvalue())
            
            status_text = " ".join(lines)
            if "IVF Index Initialization" in status_text:
                index_pct = 15
                index_stage = "Initializing"
            elif "Centroids Creation" in status_text:
                index_pct = 45
                index_stage = "Centroids"
            elif "Centroid Partitions Creation" in status_text:
                index_pct = 85
                index_stage = "Partitioning"
            elif "Creation Completed" in status_text:
                index_pct = 100
                index_stage = "Completed"
        except:
            pass

        # Get space
        cursor.execute("SELECT SUM(bytes)/1024/1024 FROM user_segments")
        space = cursor.fetchone()[0] or 0
        
        conn.close()
        return prods, revs, vectors, space, index_pct, index_stage
    except Exception as e:
        return 0, 0, 0, 0, 0, "Error"

def create_dashboard(prods, revs, vectors, space, stage):
    table = Table.grid(expand=True)
    table.add_column(justify="left")
    table.add_column(justify="right")
    
    table.add_row("[bold cyan]Products Ingested:[/]", f"[bold white]{prods:,} / 800,000[/]")
    table.add_row("[bold magenta]Reviews Ingested: [/]", f"[bold white]{revs:,} / 800,000[/]")
    table.add_row("[bold green]Vectors Created:  [/]", f"[bold yellow]{vectors:,} / 800,000[/]")
    table.add_row("[bold blue]Indexing Stage:   [/]", f"[bold cyan]{stage}[/]")
    table.add_row("[bold red]Oracle Space:     [/]", f"[bold white]{space:.2f} MB / 11,800 MB[/]")
    
    return table

console = Console()

def main():
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        ingest_task = progress.add_task("[cyan]Ingestion Status", total=800000)
        vector_task = progress.add_task("[green]Vectorization  ", total=800000)
        index_task  = progress.add_task("[bold blue]Final Indexing ", total=100)
        
        with Live(Panel(create_dashboard(0,0,0,0, "Init"), title="💎 [bold white]Enterprise AI Mission Control[/]"), refresh_per_second=1) as live:
            while not progress.finished:
                p, r, v, s, idx_p, idx_s = get_stats()
                
                progress.update(ingest_task, completed=r)
                progress.update(vector_task, completed=v)
                progress.update(index_task, completed=idx_p)
                
                live.update(Panel(create_dashboard(p, r, v, s, idx_s), title="💎 [bold white]Enterprise AI Mission Control[/]"))
                
                if idx_p >= 100:
                    break
                time.sleep(5)

if __name__ == "__main__":
    main()
