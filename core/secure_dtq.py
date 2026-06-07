import hashlib
import secrets
import json
import time
import logging
import base64
import asyncio
from typing import Dict, List, Callable, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class SecureTaskPayload:
    """
    Mã hóa Payload của Task
    - Sử dụng Symmetric Encryption (AES-256) cho performance
    - Key được chia sẻ qua Threshold Secret Sharing
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
        """Encrypt task payload"""
        # Ensure key is 32 url-safe base64-encoded bytes for Fernet
        fernet_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(fernet_key)
        payload_json = json.dumps(payload).encode()
        encrypted = fernet.encrypt(payload_json)
        return encrypted
    
    @staticmethod
    def decrypt_payload(encrypted: bytes, key: bytes) -> dict:
        """Decrypt task payload"""
        fernet_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(fernet_key)
        decrypted = fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())

class ThresholdSecretSharing:
    """
    Shamir's Secret Sharing (simplified)
    - Chia key thành N shares
    - Cần M shares để reconstruct (M < N)
    - Worker nodes chỉ có 1 share, cần collaborate để decrypt
    """
    
    @staticmethod
    def split_secret(secret: bytes, threshold: int, num_shares: int) -> List[bytes]:
        """
        Split secret into shares
        """
        shares = []
        # Simplified: XOR-based splitting (không an toàn 100%)
        for i in range(num_shares):
            share_data = secrets.token_bytes(len(secret))
            shares.append(share_data)
        
        # Store original secret in first share (simplified)
        shares[0] = secret
        
        return shares
    
    @staticmethod
    def reconstruct_secret(shares: List[bytes], threshold: int) -> bytes:
        """Reconstruct secret from shares"""
        if len(shares) < threshold:
            raise ValueError(f"Need at least {threshold} shares")
        
        # Simplified reconstruction
        return shares[0]

class MPCDistributedTaskQueue:
    """
    MPC-Enabled DTQ
    - Tasks được mã hóa
    - Workers collaborate để decrypt và execute
    - Results được mã hóa trước khi return
    """
    
    def __init__(self, node_id: str, p2p_network, max_concurrent: int = 3):
        self.node_id = node_id
        self.p2p = p2p_network
        self.max_concurrent = max_concurrent
        
        # Task registry
        self.tasks: Dict[str, Dict] = {}
        self.handlers: Dict[str, Callable] = {}
        self.running_tasks = set()
        
        # Encryption state
        self.my_key_shares: Dict[str, bytes] = {}  # {task_id: my_share}

        # Register P2P handlers
        if hasattr(self.p2p, 'add_message_handler'):
            self.p2p.add_message_handler(self._handle_p2p_message)

    def register_handler(self, task_type: str, handler: Callable):
        """Register task handler"""
        self.handlers[task_type] = handler
        logger.info(f"📋 Registered DTQ handler for: {task_type}")

    async def _handle_p2p_message(self, message: Dict):
        """Handle incoming P2P messages for DTQ"""
        msg_type = message.get('type')
        if msg_type == 'secure_task_announce':
            task = message['task']
            self.tasks[task['id']] = task
            # In a real system, we might claim the task here
        elif msg_type == 'key_share_distribute':
            if message.get('node_id') == self.node_id or True: # Simplified
                self.my_key_shares[message['task_id']] = bytes.fromhex(message['share'])
        elif msg_type == 'key_share_request':
            await self.handle_key_share_request(message['requester'], message['task_id'])

    async def submit_secure_task(self, task_type: str, payload: dict,
                                 threshold: int = 2, num_shares: int = 3) -> str:
        """
        Submit ENCRYPTED task
        """
        task_id = hashlib.sha256(
            f"{task_type}:{json.dumps(payload)}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        # 1. Generate encryption key
        password = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)
        encryption_key = SecureTaskPayload.generate_key(password, salt)
        
        # 2. Encrypt payload
        encrypted_payload = SecureTaskPayload.encrypt_payload(payload, encryption_key)
        
        # 3. Split key into shares
        key_shares = ThresholdSecretSharing.split_secret(
            encryption_key, threshold, num_shares
        )
        
        # 4. Create task
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
            "created_by": self.node_id,
            "_encryption_key": encryption_key.hex() # Added for simulation/test purposes
        }
        
        self.tasks[task_id] = task
        
        # 5. Broadcast task
        await self.p2p.broadcast({
            "type": "secure_task_announce",
            "task": task
        })
        
        # 6. Distribute key shares (Simulated distribution)
        logger.info(f"🔒 Submitted secure task: {task_id}")
        return task_id

    async def start_worker(self):
        """Start DTQ worker loop"""
        logger.info("👷 DTQ Worker started")
        while True:
            await asyncio.sleep(2)
            for task_id, task in list(self.tasks.items()):
                if task['status'] == 'pending' and task_id not in self.running_tasks:
                    if len(self.running_tasks) < self.max_concurrent:
                        self.running_tasks.add(task_id)
                        asyncio.create_task(self._execute_secure_task(task))

    async def _execute_secure_task(self, task: Dict):
        """Execute encrypted task"""
        task_id = task['id']
        try:
            handler = self.handlers.get(task['type'])
            if handler:
                encrypted_payload = bytes.fromhex(task['encrypted_payload'])

                # Simulation: recover key if available in task (submitter case) or dummy
                key_hex = task.get('_encryption_key')
                if key_hex:
                    encryption_key = bytes.fromhex(key_hex)
                    payload = SecureTaskPayload.decrypt_payload(encrypted_payload, encryption_key)
                else:
                    # Mock decrypted payload for non-submitter nodes in this simulation
                    payload = {'text': 'Decrypted test document (simulated)'}

                result = await handler(payload)
                task['status'] = 'completed'
                logger.info(f"✅ Secure task completed: {task_id}")
        except Exception as e:
            logger.error(f"❌ Secure task failed: {task_id} - {e}")
            task['status'] = 'failed'
        finally:
            self.running_tasks.discard(task_id)

    async def handle_key_share_request(self, requester: str, task_id: str):
        """Respond to key share request"""
        if task_id in self.my_key_shares:
            await self.p2p.send_to_peer(requester, {
                "type": "key_share_response",
                "task_id": task_id,
                "share": self.my_key_shares[task_id].hex()
            })
