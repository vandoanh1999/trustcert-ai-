# core/p2p_gossip.py - Gossip Protocol for P2P Communication
import asyncio
import json
import time
import logging
from typing import Set, Dict, List, Callable, Optional
import numpy as np

logger = logging.getLogger(__name__)

class GossipP2P:
    """
    Gossip Protocol for P2P Network
    - No central server needed
    - Eventually consistent
    - Lightweight communication
    """
    
    def __init__(self, node_id: str, port: int, fvs_store=None):
        self.node_id = node_id
        self.port = port
        self.fvs_store = fvs_store
        
        # Peer management
        self.peers: Set[str] = set()
        self.peer_vectors: Dict[str, Set[str]] = {}
        self.peer_last_seen: Dict[str, float] = {}
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Gossip settings
        self.gossip_interval = 30
        self.peer_timeout = 300
        
        # External handlers
        self.external_handlers: List[Callable] = []
    
    async def start(self):
        """Start P2P server"""
        server = await asyncio.start_server(
            self._handle_connection, '0.0.0.0', self.port
        )
        
        asyncio.create_task(self._gossip_loop())
        asyncio.create_task(self._cleanup_loop())
        
        logger.info(f"P2P server running on port {self.port}")
        
        async with server:
            await server.serve_forever()
    
    async def _handle_connection(self, reader, writer):
        """Handle incoming connection"""
        try:
            data = await asyncio.wait_for(reader.read(8192), timeout=10)
            if not data:
                return
            
            message = json.loads(data.decode())
            msg_type = message.get('type')
            
            # Get peer address
            peer_addr = writer.get_extra_info('peername')
            peer_port = message.get('port', self.port)
            peer_id = f"{peer_addr[0]}:{peer_port}"
            
            # Update peer tracking
            self.peers.add(peer_id)
            self.peer_last_seen[peer_id] = time.time()
            
            # Handle message
            response = await self._process_message(peer_id, message)
            
            if response:
                writer.write(json.dumps(response).encode())
                await writer.drain()
            
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def _process_message(self, peer_id: str, message: Dict) -> Optional[Dict]:
        """Process incoming message"""
        msg_type = message.get('type')
        
        if msg_type == 'ping':
            return {"type": "pong", "node_id": self.node_id}
        
        elif msg_type == 'announce':
            vec_ids = message.get('vector_ids', [])
            if peer_id not in self.peer_vectors:
                self.peer_vectors[peer_id] = set()
            self.peer_vectors[peer_id].update(vec_ids)
            logger.debug(f"Peer {peer_id} announced {len(vec_ids)} vectors")
        
        elif msg_type == 'query':
            if self.fvs_store:
                embedding = np.array(message['embedding'])
                top_k = message.get('top_k', 5)
                results = self.fvs_store.search(embedding, top_k)
                return {
                    "type": "query_response",
                    "results": results,
                    "node_id": self.node_id
                }
        
        elif msg_type == 'peer_list':
            return {
                "type": "peer_list_response",
                "peers": list(self.peers),
                "node_id": self.node_id
            }
        
        # Call external handlers
        for handler in self.external_handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Handler error: {e}")
        
        return None
    
    async def _gossip_loop(self):
        """Periodic gossip to peers"""
        while True:
            await asyncio.sleep(self.gossip_interval)
            
            if not self.peers or not self.fvs_store:
                continue
            
            # Broadcast our vectors
            message = {
                "type": "announce",
                "node_id": self.node_id,
                "port": self.port,
                "vector_ids": self.fvs_store.vector_ids[-100:],
                "timestamp": time.time()
            }
            
            await self.broadcast(message)
    
    async def _cleanup_loop(self):
        """Clean up stale peers"""
        while True:
            await asyncio.sleep(60)
            
            now = time.time()
            stale_peers = [
                p for p, t in self.peer_last_seen.items()
                if now - t > self.peer_timeout
            ]
            
            for peer in stale_peers:
                self.peers.discard(peer)
                self.peer_vectors.pop(peer, None)
                self.peer_last_seen.pop(peer, None)
                logger.debug(f"Removed stale peer: {peer}")
    
    async def _safe_send(self, peer: str, message: Dict):
        """Helper for safe parallel broadcast"""
        try:
            await self.send_to_peer(peer, message)
        except Exception as e:
            logger.warning(f"Broadcast to {peer} failed: {e}")

    async def broadcast(self, message: Dict):
        """Broadcast message to all peers in parallel"""
        peers = list(self.peers)
        if not peers:
            return

        # Bolt: Parallelize broadcast to reduce latency from O(N) to O(1)
        tasks = [self._safe_send(peer, message) for peer in peers]
        await asyncio.gather(*tasks)
    
    async def send_to_peer(self, peer: str, message: Dict):
        """Send message to specific peer"""
        try:
            ip, port = peer.split(':')
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, int(port)),
                timeout=5
            )
            
            writer.write(json.dumps(message).encode())
            await writer.drain()
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.debug(f"Send to {peer} failed: {e}")
            raise
    
    async def send_and_wait(self, peer: str, message: Dict, timeout: float = 10) -> Optional[Dict]:
        """Send message and wait for response"""
        try:
            ip, port = peer.split(':')
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, int(port)),
                timeout=5
            )
            
            writer.write(json.dumps(message).encode())
            await writer.drain()
            
            data = await asyncio.wait_for(reader.read(16384), timeout=timeout)
            response = json.loads(data.decode()) if data else None
            
            writer.close()
            await writer.wait_closed()
            
            return response
            
        except Exception as e:
            logger.debug(f"Send/wait to {peer} failed: {e}")
            return None
    
    async def query_peers(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Query all peers for similar vectors in parallel"""
        peers = list(self.peers)
        if not peers:
            return []

        message = {
            "type": "query",
            "embedding": query_embedding.tolist(),
            "top_k": top_k
        }
        
        # Bolt: Parallelize queries to reduce latency from O(N) to O(1)
        tasks = [self.send_and_wait(peer, message) for peer in peers]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        for response in responses:
            if isinstance(response, dict) and response.get('type') == 'query_response':
                all_results.extend(response.get('results', []))
        
        # Deduplicate and sort
        seen = set()
        unique = []
        for r in sorted(all_results, key=lambda x: x['score'], reverse=True):
            if r['id'] not in seen:
                seen.add(r['id'])
                unique.append(r)
        
        return unique[:top_k]
    
    async def announce_vector(self, vec_id: str):
        """Announce new vector to network"""
        message = {
            "type": "announce",
            "node_id": self.node_id,
            "port": self.port,
            "vector_ids": [vec_id],
            "timestamp": time.time()
        }
        await self.broadcast(message)
    
    def add_bootstrap_peer(self, peer_address: str):
        """Add initial peer"""
        self.peers.add(peer_address)
        self.peer_last_seen[peer_address] = time.time()
        logger.info(f"Added bootstrap peer: {peer_address}")
    
    def add_message_handler(self, handler: Callable):
        """Add external message handler"""
        self.external_handlers.append(handler)