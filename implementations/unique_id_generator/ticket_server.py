"""
Ticket Server Simulation
Chapter 7: Ticket Server & Multi-Master ID Generation

Simulates centralized database auto-increment ticket servers (Flickr approach),
supporting step increments (e.g., Server 1 generates 1, 3, 5, 7... and Server 2 generates 2, 4, 6, 8...).
"""

import threading
from typing import List


class TicketServer:
    def __init__(self, server_id: int, step: int = 1, start: int = 1):
        """
        Args:
            server_id: Server ordinal (e.g. 0 or 1).
            step: Increment step (e.g. 2 for 2 ticket servers).
            start: Initial ID value.
        """
        self.server_id = server_id
        self.step = step
        self.current_id = start
        self._lock = threading.Lock()

    def next_id(self) -> int:
        with self._lock:
            val = self.current_id
            self.current_id += self.step
            return val


class MultiMasterTicketCluster:
    """
    Cluster of ticket servers distributing ID generation across nodes.
    """

    def __init__(self, node_count: int = 2):
        self.node_count = node_count
        self.servers: List[TicketServer] = [
            TicketServer(server_id=i, step=node_count, start=i + 1)
            for i in range(node_count)
        ]
        self._rr_index = 0
        self._lock = threading.Lock()

    def get_id(self) -> int:
        with self._lock:
            server = self.servers[self._rr_index]
            self._rr_index = (self._rr_index + 1) % self.node_count
            return server.next_id()

