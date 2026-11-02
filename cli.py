"""
System Design Interactive CLI Tool
Provides live command-line demonstrations, simulations, and benchmarks.

Usage:
    python cli.py demo-rate-limiter
    python cli.py demo-consistent-hashing
    python cli.py demo-snowflake
    python cli.py demo-url-shortener
    python cli.py demo-autocomplete
    python cli.py demo-leaderboard
    python cli.py demo-wallet
    python cli.py demo-message-queue
    python cli.py demo-object-storage
    python cli.py demo-stock-exchange
    python cli.py benchmark-all
"""

import sys
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def demo_rate_limiter():
    from implementations.rate_limiter import TokenBucketRateLimiter
    console.print(Panel.fit("[bold cyan]Rate Limiter Demo (Token Bucket)[/bold cyan]\nCapacity: 5 tokens | Refill: 1 token/sec", border_style="cyan"))
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1.0)

    table = Table(title="Simulated Rapid Requests (Client: test-client)")
    table.add_column("Req #", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Tokens Remaining", justify="center")
    table.add_column("Retry After (s)", justify="center")

    for i in range(1, 9):
        res = limiter.allow_request("test-client")
        status = "[bold green]ALLOWED[/bold green]" if res.allowed else "[bold red]THROTTLED (429)[/bold red]"
        table.add_row(str(i), status, str(res.remaining), str(res.retry_after or 0.0))
        time.sleep(0.05)

    console.print(table)


def demo_consistent_hashing():
    from implementations.consistent_hashing import ConsistentHashRing, ConsistentHashSimulator
    console.print(Panel.fit("[bold green]Consistent Hashing Ring Simulation[/bold green]", border_style="green"))

    ring = ConsistentHashRing(nodes=["node-1", "node-2", "node-3"], vnodes_per_node=150)
    keys = [f"key_{i}" for i in range(10000)]

    churn = ConsistentHashSimulator.compare_node_churn(
        initial_nodes=["node-1", "node-2", "node-3"],
        new_node="node-4",
        keys=keys,
        vnodes=150,
    )

    table = Table(title="Key Migration When Adding Node-4 to Cluster of 3 Nodes")
    table.add_column("Algorithm", justify="left")
    table.add_column("Keys Moved", justify="right")
    table.add_column("% Moved", justify="right")
    table.add_column("Theoretical Target", justify="right")

    ch_data = churn["consistent_hashing"]
    naive_data = churn["naive_modulo_hashing"]

    table.add_row(
        "[bold green]Consistent Hashing (vnodes=150)[/bold green]",
        str(ch_data["keys_moved"]),
        f"{ch_data['percentage_moved']}%",
        f"~{ch_data['theoretical_fraction']}% (1 / N)",
    )
    table.add_row(
        "[bold red]Naive Modulo Hashing (hash % N)[/bold red]",
        str(naive_data["keys_moved"]),
        f"{naive_data['percentage_moved']}%",
        f"~{naive_data['theoretical_fraction']}% ((N-1) / N)",
    )

    console.print(table)


def demo_snowflake():
    from implementations.unique_id_generator import SnowflakeIDGenerator, Base62
    console.print(Panel.fit("[bold yellow]Twitter Snowflake 64-bit ID Generator[/bold yellow]", border_style="yellow"))

    gen = SnowflakeIDGenerator(datacenter_id=2, worker_id=7)
    table = Table(title="Generated 64-bit Snowflake Identifiers")
    table.add_column("Index", justify="center")
    table.add_column("64-bit Decimal ID", justify="left")
    table.add_column("Base62", justify="center")
    table.add_column("UTC Timestamp", justify="left")
    table.add_column("DC/Worker", justify="center")
    table.add_column("Sequence", justify="center")

    for i in range(1, 6):
        uid = gen.generate()
        p = gen.parse(uid)
        table.add_row(
            str(i),
            str(uid),
            Base62.encode(uid),
            p.utc_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            f"{p.datacenter_id}/{p.worker_id}",
            str(p.sequence),
        )

    console.print(table)


def demo_url_shortener():
    from implementations.url_shortener import URLShortenerService
    console.print(Panel.fit("[bold magenta]URL Shortener Service (Snowflake + Base62 + Bloom Filter + LRU)[/bold magenta]", border_style="magenta"))

    service = URLShortenerService()
    test_urls = [
        "https://bytebytego.com",
        "https://en.wikipedia.org/wiki/Consistent_hashing",
        "https://redis.io/docs/data-types/sorted-sets/",
    ]

    table = Table(title="Shortened URLs & Resolution")
    table.add_column("Original URL", justify="left")
    table.add_column("Short Code", justify="center")
    table.add_column("Resolved URL", justify="left")
    table.add_column("Clicks", justify="center")

    for url in test_urls:
        entry = service.shorten(url)
        resolved = service.resolve(entry.short_code)
        table.add_row(url, entry.short_code, resolved, str(entry.click_count))

    console.print(table)


def demo_autocomplete():
    from implementations.search_autocomplete import SearchAutocompleteSystem
    console.print(Panel.fit("[bold blue]Search Autocomplete Trie (Top-K Pre-Cached)[/bold blue]", border_style="blue"))

    trie = SearchAutocompleteSystem(top_k_size=5)
    trie.bulk_load({
        "system design": 5000,
        "system architecture": 3000,
        "system call": 1200,
        "snowflake generator": 4500,
        "sliding window": 2000,
        "stock exchange": 1500,
    })

    prefixes = ["sys", "s", "sl", "st"]
    table = Table(title="Prefix Autocomplete Results")
    table.add_column("Prefix", justify="center")
    table.add_column("Top-5 Suggestions (Query: Frequency)", justify="left")

    for p in prefixes:
        res = trie.search(p)
        formatted = ", ".join(f"[bold green]{q}[/bold green] ({f})" for q, f in res)
        table.add_row(f"'{p}'", formatted)

    console.print(table)


def demo_leaderboard():
    from implementations.leaderboard import LeaderboardService
    console.print(Panel.fit("[bold gold1]Real-Time Gaming Leaderboard (SkipList + Hash Table)[/bold gold1]", border_style="gold1"))

    lb = LeaderboardService()
    scores = [
        ("Valkyrie", 15400),
        ("Shadow", 22900),
        ("Zeus", 31200),
        ("Nova", 19800),
        ("Apollo", 27400),
    ]
    for player, score in scores:
        lb.update_score(player, score)

    top = lb.get_top_k(5)
    table = Table(title="Top Players Podium")
    table.add_column("Rank", justify="center")
    table.add_column("Player", justify="left")
    table.add_column("Score", justify="right")

    for e in top:
        table.add_row(f"#{e.rank}", e.player_id, f"{e.score:,.0f}")

    console.print(table)


def demo_wallet():
    from implementations.digital_wallet import DigitalWalletService
    console.print(Panel.fit("[bold green]Digital Wallet Service (Deadlock-Free ACID Transfers)[/bold green]", border_style="green"))

    wallet = DigitalWalletService()
    wallet.create_wallet("Alice", 100000)  # $1,000.00
    wallet.create_wallet("Bob", 50000)     # $500.00

    table = Table(title="Wallet Ledger State Before & After")
    table.add_column("Stage", justify="center")
    table.add_column("Alice Balance", justify="right")
    table.add_column("Bob Balance", justify="right")
    table.add_column("System Total", justify="right")

    bal_a = wallet.get_balance("Alice")
    bal_b = wallet.get_balance("Bob")
    table.add_row("Initial", f"${bal_a/100:,.2f}", f"${bal_b/100:,.2f}", f"${(bal_a+bal_b)/100:,.2f}")

    wallet.transfer("Alice", "Bob", 25000)  # Transfer $250.00
    bal_a2 = wallet.get_balance("Alice")
    bal_b2 = wallet.get_balance("Bob")
    table.add_row("After Transfer ($250)", f"${bal_a2/100:,.2f}", f"${bal_b2/100:,.2f}", f"${(bal_a2+bal_b2)/100:,.2f}")

    console.print(table)


def demo_message_queue():
    from implementations.message_queue import MessageQueueBroker
    console.print(Panel.fit("[bold cyan]Distributed Partitioned Message Queue[/bold cyan]", border_style="cyan"))

    broker = MessageQueueBroker()
    broker.create_topic("orders", partition_count=3)

    for i in range(6):
        broker.publish("orders", payload=f"order_payload_{i}", key=f"cust_{i%3}")

    table = Table(title="Consumer Group Partition Lag & Offsets")
    table.add_column("Partition", justify="center")
    table.add_column("Consumed Messages", justify="left")
    table.add_column("Remaining Lag", justify="center")

    for part_id in range(3):
        msgs = broker.consume("order_processing_workers", "orders", partition_id=part_id, max_messages=10)
        lag = broker.get_lag("order_processing_workers", "orders")[part_id]
        payloads = ", ".join(m.payload for m in msgs)
        table.add_row(f"Partition {part_id}", payloads, str(lag))

    console.print(table)


def demo_object_storage():
    from implementations.object_storage import ObjectStorageService
    console.print(Panel.fit("[bold magenta]S3-like Object Storage with Block-Level Deduplication[/bold magenta]", border_style="magenta"))

    store = ObjectStorageService(chunk_size=1024)  # 1KB chunks
    # Upload File 1 and File 2 sharing identical repeated content
    common_chunk = b"A" * 1024
    file1 = common_chunk * 5 + b"UNIQUE1"
    file2 = common_chunk * 5 + b"UNIQUE2"

    store.put_object("my-bucket", "doc1.bin", file1)
    store.put_object("my-bucket", "doc2.bin", file2)

    stats = store.get_storage_stats()
    table = Table(title="Storage Deduplication Metrics")
    table.add_column("Metric", justify="left")
    table.add_column("Value", justify="right")

    table.add_row("Total Objects Uploaded", str(stats["total_objects"]))
    table.add_row("Total Logical Data", f"{stats['logical_bytes']} bytes")
    table.add_row("Total Physical Storage Used", f"{stats['physical_bytes']} bytes")
    table.add_row("Storage Space Saved", f"{stats['saved_bytes']} bytes")
    table.add_row("Deduplication Ratio", f"{stats['deduplication_ratio']}x")

    console.print(table)


def demo_stock_exchange():
    from implementations.stock_exchange import OrderBook, OrderSide
    console.print(Panel.fit("[bold red]Stock Exchange Matching Engine (LMAX / NASDAQ)[/bold red]", border_style="red"))

    book = OrderBook(symbol="AAPL")
    book.place_limit_order(OrderSide.SELL, price=150.0, quantity=100)
    book.place_limit_order(OrderSide.SELL, price=151.0, quantity=200)

    # Aggressive BUY order sweeps the book
    order, trades = book.place_limit_order(OrderSide.BUY, price=152.0, quantity=150)

    table = Table(title="AAPL Trade Executions")
    table.add_column("Trade ID", justify="center")
    table.add_column("Price", justify="right")
    table.add_column("Quantity", justify="right")
    table.add_column("Maker Order", justify="center")
    table.add_column("Taker Order", justify="center")

    for t in trades:
        table.add_row(t.trade_id, f"${t.price:.2f}", str(t.quantity), t.maker_order_id, t.taker_order_id)

    console.print(table)


def benchmark_all():
    console.print(Panel.fit("[bold green]Executing High-Throughput Benchmarks...[/bold green]", border_style="green"))

    # 1. Snowflake Benchmark
    from implementations.unique_id_generator import SnowflakeIDGenerator
    gen = SnowflakeIDGenerator()
    start = time.perf_counter()
    count = 100_000
    for _ in range(count):
        gen.generate()
    dur = time.perf_counter() - start
    rate = count / dur
    console.print(f"Snowflake ID Generator: [bold cyan]{rate:,.0f} IDs/sec[/bold cyan] ({dur:.3f}s for 100k IDs)")

    # 2. Base62 Benchmark
    from implementations.unique_id_generator import Base62
    start = time.perf_counter()
    for i in range(100_000):
        Base62.encode(1234567890 + i)
    dur = time.perf_counter() - start
    console.print(f"Base62 Encoder:         [bold cyan]{100_000/dur:,.0f} ops/sec[/bold cyan]")

    # 3. Trie Autocomplete Benchmark
    from implementations.search_autocomplete import SearchAutocompleteSystem
    trie = SearchAutocompleteSystem()
    for i in range(1000):
        trie.insert(f"keyword_{i}", i)
    start = time.perf_counter()
    for _ in range(50_000):
        trie.search("key")
    dur = time.perf_counter() - start
    console.print(f"Autocomplete Trie:      [bold cyan]{50_000/dur:,.0f} lookups/sec[/bold cyan]")

    # 4. Token Bucket Limiter Benchmark
    from implementations.rate_limiter import TokenBucketRateLimiter
    tb = TokenBucketRateLimiter(capacity=1_000_000, refill_rate=1_000_000)
    start = time.perf_counter()
    for _ in range(100_000):
        tb.allow_request("bench_key")
    dur = time.perf_counter() - start
    console.print(f"Token Bucket Limiter:   [bold cyan]{100_000/dur:,.0f} checks/sec[/bold cyan]")


def main():
    commands = {
        "demo-rate-limiter": demo_rate_limiter,
        "demo-consistent-hashing": demo_consistent_hashing,
        "demo-snowflake": demo_snowflake,
        "demo-url-shortener": demo_url_shortener,
        "demo-autocomplete": demo_autocomplete,
        "demo-leaderboard": demo_leaderboard,
        "demo-wallet": demo_wallet,
        "demo-message-queue": demo_message_queue,
        "demo-object-storage": demo_object_storage,
        "demo-stock-exchange": demo_stock_exchange,
        "benchmark-all": benchmark_all,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        console.print("[bold yellow]Available Commands:[/bold yellow]")
        for cmd in commands:
            console.print(f"  python cli.py {cmd}")
        return

    commands[sys.argv[1]]()

if __name__ == "__main__":
    main()

