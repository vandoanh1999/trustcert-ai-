import hashlib
import secrets
import json
import time
import logging
import asyncio
import base64
from typing import Dict, List, Callable, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

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
            backend=default_backend()
        )
        return kdf.derive(password)

    @staticmethod
    def encrypt_payload(payload: dict, key: bytes) -> bytes:
        """Encrypt task payload"""
        # Fernet requires a 32-byte url-safe base64-encoded key
        f_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(f_key)
        payload_json = json.dumps(payload).encode()
        encrypted = fernet.encrypt(payload_json)
        return encrypted

    @staticmethod
    def decrypt_payload(encrypted: bytes, key: bytes) -> dict:
        """Decrypt task payload"""
        f_key = base64.urlsafe_b64encode(key)
        fernet = Fernet(f_key)
        decrypted = fernet.decrypt(encrypted)
        return json.loads(decrypted.decode())

class ThresholdSecretSharing:
    """
    Shamir's Secret Sharing (Simplified)
    - Chia key thành N shares
    - Cần M shares để reconstruct (M < N)
    - Worker nodes chỉ có 1 share, cần collaborate để decrypt
    """

    @staticmethod
    def split_secret(secret: bytes, threshold: int, num_shares: int) -> List[bytes]:
        """
        Split secret into shares
        NOTE: Đây là implementation đơn giản sử dụng XOR (không an toàn cho production)
        """
        if threshold > num_shares:
            raise ValueError("Threshold cannot be greater than num_shares")

        shares = []
        # Simplified XOR splitting for demo purposes
        # In production, use a library like 'secretsharing'

        current_xor = bytearray(secret)
        for i in range(num_shares - 1):
            share = secrets.token_bytes(len(secret))
            shares.append(share)
            for j in range(len(secret)):
                current_xor[j] ^= share[j]

        shares.append(bytes(current_xor))
        return shares

    @staticmethod
    def reconstruct_secret(shares: List[bytes], threshold: int) -> bytes:
        """Reconstruct secret from shares"""
        if not shares:
            raise ValueError("No shares provided")

        # Simplified XOR reconstruction
        result = bytearray(shares[0])
        for i in range(1, len(shares)):
            for j in range(len(result)):
                result[j] ^= shares[i][j]

        return bytes(result)

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

    def register_handler(self, task_type: str, handler: Callable):
        self.handlers[task_type] = handler

    async def _get_super_nodes(self) -> List[str]:
        """Get list of super nodes from P2P network"""
        # In a real system, this would query the DHT or peer list
        return list(self.p2p.peers)

    async def start_worker(self):
        """Start task consumer loop"""
        # Reduced sleep time for testing
        while True:
            await asyncio.sleep(2)
            logger.debug(f"DTQ worker heartbeat for {self.node_id}")

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

        # 1. Generate encryption key
        password = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)
        encryption_key = SecureTaskPayload.generate_key(password, salt)

        # 2. Encrypt payload
        encrypted_payload = SecureTaskPayload.encrypt_payload(payload, encryption_key)

        # 3. Split key into shares
        # Using N-of-N for XOR simplified
        key_shares = ThresholdSecretSharing.split_secret(
            encryption_key, num_shares, num_shares
        )

        # 4. Create task
        task = {
            "id": task_id,
            "type": task_type,
            "encrypted_payload": encrypted_payload.hex(),
            "salt": salt.hex(),
            "threshold": num_shares,
            "num_shares": num_shares,
            "key_share_holders": [],
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
        holders = []
        for i, super_node in enumerate(super_nodes[:num_shares]):
            await self.p2p.send_to_peer(super_node, {
                "type": "key_share_distribute",
                "task_id": task_id,
                "share": key_shares[i].hex(),
                "share_index": i
            })
            holders.append(super_node)

        task['key_share_holders'] = holders

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
