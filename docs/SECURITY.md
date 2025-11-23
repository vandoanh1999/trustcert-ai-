# Security Guidelines for Genesis Core V2

This document outlines security considerations, primarily related to the handling and merging of model adapters.

## 1. Adapter Provenance

- **Rule:** Only adapters from trusted, verified sources should be ingested into the `WeightIndex`.
- **Reasoning:** Model weights (adapters) are executable code. A malicious adapter could contain layers that perform arbitrary, harmful operations when executed during inference. There is no practical way to statically analyze a tensor file for safety, so trust must be established at the source.

## 2. Safe Merging Practices

- **Constraint:** Merging algorithms should operate purely on numerical tensor data. They must not have access to execute arbitrary code or access the file system outside of their designated model weight paths.
- **Reasoning:** The `merging` library itself should be a secure sandbox. Its responsibility is to perform mathematical operations, not to interpret or execute potentially unsafe model graphs.

## 3. API Endpoint Security

- **Practice:** Standard API security measures should be applied to the FastAPI server in a production environment.
    - **Authentication:** Protect endpoints with API keys or OAuth2 to prevent unauthorized access.
    - **Rate Limiting:** Prevent denial-of-service attacks by limiting the number of requests a single client can make.
    - **Input Validation:** Pydantic models provide a first layer of defense by validating the structure and type of incoming data. Ensure that no unvalidated or overly large inputs can crash the server.

## 4. Environment Security

- **Rule:** The environment where the API server and inference engine run should be isolated, with minimal necessary permissions.
- **Reasoning:** In the event of a security breach (e.g., through a malicious model), an isolated environment (like a Docker container) limits the potential damage to the host system.
