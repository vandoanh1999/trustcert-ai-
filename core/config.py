"""
Genesis Core V8: Centralized Configuration

This file consolidates all network parameters, thresholds, and magic numbers
for easy tuning and maintenance.
"""

# --- API Configuration ---
API_REQUEST_WINDOW_SECONDS = 60
API_MAX_REQUESTS_PER_WINDOW = 50

# --- Node & Tier Thresholds ---
NODE_SUPER_NODE_TRUST_THRESHOLD = 0.75
NODE_STABLE_CONTRIBUTION_THRESHOLD = 10.0
NODE_SUPER_NODE_VOTE_THRESHOLD_PERCENT = 0.6
NODE_MIN_SUPER_NODES_FOR_MPC = 3

# --- User & Tier Thresholds ---
USER_STABLE_CONTRIBUTION_THRESHOLD = 10.0
USER_VIP_PRO_CONTRIBUTION_THRESHOLD = 100.0
USER_HIGH_QUALITY_FEEDBACK_BONUS = 0.05

# --- Cryptography & Security ---
VC_SIGNING_KEY = b"genesis_v8_decentralized_network_key"
REPUTATION_EMA_LEARNING_RATE = 0.1

# --- P2P Network ---
# (No configurable constants for the simulation yet)

# --- Ecosystem Rover & Training ---
# (No configurable constants for the simulation yet)

class Settings:
    def __init__(self):
        self.ENABLE_FVS = True
        self.FVS_NODE_ID = "node_main"
        self.EMBEDDING_MODEL_DIM = 384
        self.FVS_RELAY_NODES = ""
        self.FVS_P2P_PORT = 8001

def get_settings():
    return Settings()
