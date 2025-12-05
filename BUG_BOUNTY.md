# Genesis Core V8 - Bug Bounty Program

This document outlines the scope, rules, and rewards for the Genesis Bug Bounty Program.

---

## Program Scope

We are interested in vulnerabilities in the following areas of the Genesis V8 ecosystem:

*   **Core Security:** Vulnerabilities in the Shamir's Secret Sharing, ECDSA signing, or memory management.
*   **Decentralized Network:** Flaws in the P2P gossip protocol, voting mechanism, or Sybil resistance.
*   **API Server:** Exploits in the FastAPI endpoints (e.g., rate-limit bypass, injection attacks).
*   **Reputation System:** Logical flaws that would allow an attacker to unfairly manipulate trust or contribution scores.

## Rewards

Rewards will be paid out in USD (or a future GEN token equivalent) based on severity.

*   **Critical (e.g., network takeover, private key compromise):** $500 - $1000+
*   **High (e.g., Sybil attack vector, proposal system bypass):** $250 - $500
*   **Medium (e.g., denial of service, reputation manipulation):** $100 - $250
*   **Low (e.g., information leaks, minor logical flaws):** $50 - $100

## Rules

*   Do not engage in any public disclosure of the vulnerability before we have had a chance to remediate it.
*   Do not perform any attacks that could disrupt service for other users.
*   Social engineering is out of scope.

## How to Submit

Please send a detailed report, including steps to reproduce, to `security@genesis-network.dev` (placeholder).
