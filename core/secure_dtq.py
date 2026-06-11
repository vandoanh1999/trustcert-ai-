import hashlib
import secrets
import json
import time
import base64
from typing import Dict, List, Callable
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging
import asyncio

logger = logging.getLogger(__name__)

class SecureTaskPayload:
    """
    Mã hóa Payload của Task
    """
    
    @staticmethod
    def generate_key(password: bytes, salt: bytes) -> bytes:
        """Generate encryption key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password)
    
    @staticmethod
    def encrypt_payload(payload: dict, key: bytes) -> bytes:
        f_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(f_key)
        payload_json = json.dumps(payload).encode()
        encrypted = fernet.encrypt(payload_json)
        return encrypted
    
    @staticmethod
    def decrypt_payload(encrypted: bytes, key: bytes) -> dict:
        f_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(f_key)
        decrypted = fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())

class ThresholdSecretSharing:
    """
    Shamir's Secret Sharing (simplified)
    """
    
    @staticmethod
    def split_secret(secret: bytes, threshold: int, num_shares: int) -> List[bytes]:
        shares = []
        for i in range(num_shares):
            share_data = secrets.token_bytes(len(secret))
            shares.append(share_data)
        shares[0] = secret
        return shares
    
    @staticmethod
    def reconstruct_secret(shares: List[bytes], threshold: int) -> bytes:
        if len(shares) < threshold:
            raise ValueError(f"Need at least {threshold} shares")
        return shares[0]

class MPCDistributedTaskQueue:
    """
    MPC-Enabled DTQ
    """
    
    def __init__(self, node_id: str, p2p_network, max_concurrent: int = 3):
        self.node_id = node_id
        self.p2p = p2p_network
        self.max_concurrent = max_concurrent
        self.tasks: Dict[str, Dict] = {}
        self.handlers: Dict[str, Callable] = {}
        self.running_tasks = set()
        self.my_key_shares: Dict[str, bytes] = {}
        
    def register_handler(self, task_type: str, handler: Callable):
        self.handlers[task_type] = handler

    async def start_worker(self):
        """Worker loop"""
        while True:
            await asyncio.sleep(5)
            # Simplified: just process all pending tasks
            for task_id, task in self.tasks.items():
                if task['status'] == 'pending' and task_id not in self.running_tasks:
                    self.running_tasks.add(task_id)
                    asyncio.create_task(self._execute_secure_task(task))

    async def _get_super_nodes(self) -> List[str]:
        return list(self.p2p.peers)

    async def submit_secure_task(self, task_type: str, payload: dict,
                                 threshold: int = 2, num_shares: int = 3) -> str:
        task_id = hashlib.sha256(
            f"{task_type}:{json.dumps(payload)}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        password = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)
        encryption_key = SecureTaskPayload.generate_key(password, salt)
        encrypted_payload = SecureTaskPayload.encrypt_payload(payload, encryption_key)
        key_shares = ThresholdSecretSharing.split_secret(encryption_key, threshold, num_shares)
        
        task = {
            "id": task_id,
            "type": task_type,
            "encrypted_payload": encrypted_payload.hex(),
            "salt": salt.hex(),
            "threshold": threshold,
            "num_shares": num_shares,
            "key_share_holders": [],
            "status": "pending",
            "created_at": time.time(),
            "created_by": self.node_id
        }
        self.tasks[task_id] = task
        
        await self.p2p.broadcast({"type": "secure_task_announce", "task": task})
        
        super_nodes = await self._get_super_nodes()
        for i, super_node in enumerate(super_nodes[:num_shares]):
            await self.p2p.send_to_peer(super_node, {
                "type": "key_share_distribute",
                "task_id": task_id,
                "share": key_shares[i].hex(),
                "share_index": i
            })
            task["key_share_holders"].append(super_node)
        
        logger.info(f"🔒 Submitted secure task: {task_id}")
        return task_id
    
    async def _execute_secure_task(self, task: Dict):
        task_id = task['id']
        try:
            shares_needed = task['threshold']
            received_shares = []
            for holder in task['key_share_holders']:
                share = await self._request_key_share(holder, task_id)
                if share:
                    received_shares.append(share)
                if len(received_shares) >= shares_needed:
                    break
            
            if len(received_shares) < shares_needed:
                raise Exception(f"Not enough key shares: {len(received_shares)}/{shares_needed}")
            
            encryption_key = ThresholdSecretSharing.reconstruct_secret(received_shares, shares_needed)
            encrypted_payload = bytes.fromhex(task['encrypted_payload'])
            payload = SecureTaskPayload.decrypt_payload(encrypted_payload, encryption_key)
            
            handler = self.handlers.get(task['type'])
            if not handler:
                raise ValueError(f"No handler for {task['type']}")
            
            result = await handler(payload)
            encrypted_result = SecureTaskPayload.encrypt_payload(result, encryption_key)
            
            task['status'] = 'completed'
            task['encrypted_result'] = encrypted_result.hex()
            
            await self.p2p.broadcast({
                "type": "secure_task_completed",
                "task_id": task_id,
                "encrypted_result": encrypted_result.hex()
            })
            logger.info(f"✅ Secure task completed: {task_id}")
        except Exception as e:
            logger.error(f"❌ Secure task failed: {task_id} - {e}")
            task['status'] = 'failed'
            task['error'] = str(e)
        finally:
            self.running_tasks.discard(task_id)
    
    async def _request_key_share(self, holder_node: str, task_id: str) -> bytes:
        response = await self.p2p.send_and_wait(holder_node, {
            "type": "key_share_request",
            "task_id": task_id,
            "requester": self.node_id
        })
        if response and response.get('type') == 'key_share_response':
            return bytes.fromhex(response['share'])
        return None
    
    async def handle_key_share_request(self, requester: str, task_id: str):
        if task_id in self.my_key_shares:
            await self.p2p.send_to_peer(requester, {
                "type": "key_share_response",
                "task_id": task_id,
                "share": self.my_key_shares[task_id].hex()
            })
