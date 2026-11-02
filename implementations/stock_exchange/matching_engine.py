"""
Stock Exchange Order Book & Matching Engine (LMAX / NASDAQ Architecture)
Chapter 28: Design A Stock Exchange

Features:
1. Limit Order Book:
   - Bids (Buy orders) sorted highest price first, then earliest timestamp first.
   - Asks (Sell orders) sorted lowest price first, then earliest timestamp first.
2. Price-Time Priority Matching:
   - Orders at better prices execute first.
   - Orders at the same price execute in strict chronological FIFO order.
3. Trade Generation:
   - Emits execution trades atomically.
   - Supports partial fills and multi-order sweep fills.
"""

from collections import deque
from dataclasses import dataclass
from enum import Enum
import threading
import time
from typing import Dict, List, Optional, Tuple
import uuid


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


@dataclass
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    price: float
    quantity: int
    remaining_quantity: int
    timestamp: float


@dataclass
class Trade:
    trade_id: str
    symbol: str
    price: float
    quantity: int
    maker_order_id: str
    taker_order_id: str
    timestamp: float


class OrderBook:
    """
    Limit Order Book maintaining Price-Time Priority for a single ticker symbol.
    """

    def __init__(self, symbol: str):
        self.symbol = symbol
        # price -> deque of Order
        self.bids: Dict[float, deque] = {}  # Buy orders
        self.asks: Dict[float, deque] = {}  # Sell orders
        self.trades: List[Trade] = []
        self._lock = threading.Lock()

    def place_limit_order(self, side: OrderSide, price: float, quantity: int) -> Tuple[Order, List[Trade]]:
        """
        Match incoming taker order against resting maker orders, or rest the remaining in book.
        """
        with self._lock:
            order = Order(
                order_id=f"ord_{uuid.uuid4().hex[:8]}",
                symbol=self.symbol,
                side=side,
                price=price,
                quantity=quantity,
                remaining_quantity=quantity,
                timestamp=time.time(),
            )

            executed_trades: List[Trade] = []

            if side == OrderSide.BUY:
                # Match against lowest asks where ask_price <= order.price
                while order.remaining_quantity > 0 and self.asks:
                    best_ask = min(self.asks.keys())
                    if best_ask > order.price:
                        break  # No acceptable price to match

                    ask_queue = self.asks[best_ask]
                    maker_order = ask_queue[0]

                    match_qty = min(order.remaining_quantity, maker_order.remaining_quantity)
                    trade = Trade(
                        trade_id=f"trd_{uuid.uuid4().hex[:8]}",
                        symbol=self.symbol,
                        price=best_ask,
                        quantity=match_qty,
                        maker_order_id=maker_order.order_id,
                        taker_order_id=order.order_id,
                        timestamp=time.time(),
                    )
                    executed_trades.append(trade)
                    self.trades.append(trade)

                    order.remaining_quantity -= match_qty
                    maker_order.remaining_quantity -= match_qty

                    if maker_order.remaining_quantity == 0:
                        ask_queue.popleft()
                        if not ask_queue:
                            del self.asks[best_ask]

                # Rest unfilled portion into bids book
                if order.remaining_quantity > 0:
                    if order.price not in self.bids:
                        self.bids[order.price] = deque()
                    self.bids[order.price].append(order)

            else:  # SELL
                # Match against highest bids where bid_price >= order.price
                while order.remaining_quantity > 0 and self.bids:
                    best_bid = max(self.bids.keys())
                    if best_bid < order.price:
                        break

                    bid_queue = self.bids[best_bid]
                    maker_order = bid_queue[0]

                    match_qty = min(order.remaining_quantity, maker_order.remaining_quantity)
                    trade = Trade(
                        trade_id=f"trd_{uuid.uuid4().hex[:8]}",
                        symbol=self.symbol,
                        price=best_bid,
                        quantity=match_qty,
                        maker_order_id=maker_order.order_id,
                        taker_order_id=order.order_id,
                        timestamp=time.time(),
                    )
                    executed_trades.append(trade)
                    self.trades.append(trade)

                    order.remaining_quantity -= match_qty
                    maker_order.remaining_quantity -= match_qty

                    if maker_order.remaining_quantity == 0:
                        bid_queue.popleft()
                        if not bid_queue:
                            del self.bids[best_bid]

                # Rest unfilled portion into asks book
                if order.remaining_quantity > 0:
                    if order.price not in self.asks:
                        self.asks[order.price] = deque()
                    self.asks[order.price].append(order)

            return order, executed_trades

    def get_market_depth(self, levels: int = 5) -> Dict[str, List[Dict]]:
        """Returns top N levels of bids and asks."""
        with self._lock:
            sorted_bids = sorted(self.bids.keys(), reverse=True)[:levels]
            sorted_asks = sorted(self.asks.keys())[:levels]

            bid_depth = [
                {"price": p, "total_quantity": sum(o.remaining_quantity for o in self.bids[p])}
                for p in sorted_bids
            ]
            ask_depth = [
                {"price": p, "total_quantity": sum(o.remaining_quantity for o in self.asks[p])}
                for p in sorted_asks
            ]

            return {"symbol": self.symbol, "bids": bid_depth, "asks": ask_depth}

