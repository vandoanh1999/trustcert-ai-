import base64
import hashlib
import json
import logging
import secrets
import time
from typing import Callable, Dict, List

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.shamir import SecretSharer

logger = logging.getLogger(__name__)

class SecureTaskPayload:
    """
    Mã hóa Payload của Task
    - Sử dụng Symmetric Encryption (AES-256) cho performance
    - Key được chia sẻ qua Threshold Secret Sharing
    """
    
    @staticmethod
    def generate_key(password: bytes, salt: bytes) -> bytes:
        """Derive a raw 32-byte key (PBKDF2-HMAC-SHA256, 600k iterations)."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600_000,
        )
        return kdf.derive(password)

    @staticmethod
    def _fernet(key: bytes) -> Fernet:
        # Fernet expects a urlsafe-base64 encoding of 32 raw bytes.
        if len(key) != 32:
            raise ValueError("Encryption key must be 32 raw bytes.")
        return Fernet(base64.urlsafe_b64encode(key))

    @staticmethod
    def encrypt_payload(payload: dict, key: bytes) -> bytes:
        """Encrypt task payload"""
        fernet = SecureTaskPayload._fernet(key)
        payload_json = json.dumps(payload).encode()
        encrypted = fernet.encrypt(payload_json)
        return encrypted
    
    @staticmethod
    def decrypt_payload(encrypted: bytes, key: bytes) -> dict:
        """Decrypt task payload"""
        fernet = SecureTaskPayload._fernet(key)
        decrypted = fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())

class ThresholdSecretSharing:
    """
    Shamir's Secret Sharing over the 256-bit prime field of core.shamir.
    - Splits a 32-byte key into N shares; any M of them rebuild it, fewer reveal nothing.
    - Each share is the UTF-8 encoding of "x-y" (hex), so it can travel as share.hex().

    SECURITY FIX: the previous version stored the whole secret in shares[0]
    (and random noise in the others), so the first holder alone had the key.
    """

    @staticmethod
    def split_secret(secret: bytes, threshold: int, num_shares: int) -> List[bytes]:
        if not 1 <= threshold <= num_shares:
            raise ValueError("Need 1 <= threshold <= num_shares.")
        if len(secret) != 32:
            raise ValueError("Secret must be exactly 32 bytes.")
        if int.from_bytes(secret, "big") >= SecretSharer.prime:
            raise ValueError("Secret exceeds the field size; generate a new key.")
        shares = SecretSharer.split_secret(secret.hex(), threshold, num_shares)
        return [share.encode("utf-8") for share in shares]

    @staticmethod
    def reconstruct_secret(shares: List[bytes], threshold: int) -> bytes:
        """Reconstruct secret from >= threshold distinct shares."""
        decoded = list({share.decode("utf-8") for share in shares})
        if len(decoded) < threshold:
            raise ValueError(f"Need at least {threshold} distinct shares")
        secret_hex = SecretSharer.recover_secret(decoded[:threshold]).zfill(64)
        return bytes.fromhex(secret_hex)

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
    
    async def submit_secure_task(self, task_type: str, payload: dict,
                                 threshold: int = 2, num_shares: int = 3) -> str:
        """
        Submit ENCRYPTED task
        - Payload được mã hóa
        - Key được chia thành shares và distribute
        """
        task_id = hashlib.sha256(
            f"{task_type}:{json.dumps(payload)}:{time.time()}".encode()
        ).hexdigest()[:16]
        
        # 1. Generate a random 32-byte key that fits the Shamir field
        salt = secrets.token_bytes(16)
        while True:
            encryption_key = secrets.token_bytes(32)
            if int.from_bytes(encryption_key, "big") < SecretSharer.prime:
                break
        
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
            "key_share_holders": [],  # Will be filled by claiming nodes
            "status": "pending",
            "created_at": time.time(),
            "created_by": self.node_id
        }
        
        self.tasks[task_id] = task
        
        # 5. Broadcast task (WITHOUT shares)
        await self.p2p.broadcast({
            "type": "secure_task_announce",
            "task": task
        })
        
        # 6. Distribute key shares to Super Nodes
        super_nodes = await self._get_super_nodes()
        for i, super_node in enumerate(super_nodes[:num_shares]):
            await self.p2p.send_to_peer(super_node, {
                "type": "key_share_distribute",
                "task_id": task_id,
                "share": key_shares[i].hex(),
                "share_index": i
            })
        
        logger.info(f"🔒 Submitted secure task: {task_id}")
        return task_id
    
    async def _execute_secure_task(self, task: Dict):
        """
        Execute encrypted task
        - Request key shares từ holders
        - Reconstruct encryption key
        - Decrypt và execute
        """
        task_id = task['id']
        
        try:
            # 1. Request key shares
            logger.info(f"🔐 Requesting key shares for task: {task_id}")
            
            shares_needed = task['threshold']
            received_shares = []
            
            for holder in task['key_share_holders']:
                try:
                    share = await self._request_key_share(holder, task_id)
                    if share:
                        received_shares.append(share)
                    
                    if len(received_shares) >= shares_needed:
                        break
                except Exception as e:
                    logger.warning(f"⚠️ Failed to get share from {holder}: {e}")
            
            if len(received_shares) < shares_needed:
                raise Exception(f"Not enough key shares: {len(received_shares)}/{shares_needed}")
            
            # 2. Reconstruct key
            encryption_key = ThresholdSecretSharing.reconstruct_secret(
                received_shares, shares_needed
            )
            
            # 3. Decrypt payload
            encrypted_payload = bytes.fromhex(task['encrypted_payload'])
            payload = SecureTaskPayload.decrypt_payload(encrypted_payload, encryption_key)
            
            logger.info(f"🔓 Task decrypted successfully: {task_id}")
            
            # 4. Execute handler
            handler = self.handlers.get(task['type'])
            if not handler:
                raise ValueError(f"No handler for {task['type']}")
            
            result = await handler(payload)
            
            # 5. Encrypt result
            encrypted_result = SecureTaskPayload.encrypt_payload(result, encryption_key)
            
            # 6. Update status
            task['status'] = 'completed'
            task['encrypted_result'] = encrypted_result.hex()
            
            # Broadcast completion
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
        """Request key share từ holder node"""
        response = await self.p2p.send_and_wait(holder_node, {
            "type": "key_share_request",
            "task_id": task_id,
            "requester": self.node_id
        })
        
        if response and response.get('type') == 'key_share_response':
            return bytes.fromhex(response['share'])
        
        return None
    
    async def handle_key_share_request(self, requester: str, task_id: str):
        """Respond to key share request"""
        if task_id in self.my_key_shares:
            await self.p2p.send_to_peer(requester, {
                "type": "key_share_response",
                "task_id": task_id,
                "share": self.my_key_shares[task_id].hex()
            })
            logger.debug(f"📤 Sent key share to {requester} for task {task_id}")