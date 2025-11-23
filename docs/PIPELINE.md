# End-to-End Dispatch Pipeline

This document describes the flow of a query through the Genesis Core V2 system.

1.  **API Request:** A user sends a query (e.g., `"Solve the equation x^2 = 4"`) to the `/dispatch` endpoint of the API server.

2.  **Routing:** The `SemanticRouter` receives the text.
    *   It first attempts a fast **L1 Keyword Route**. If a keyword like "solve" or "equation" is found, it immediately assigns the "math" domain.
    *   If no keyword is found, it uses the `ShepherdEncoder` to generate a semantic vector from the text and performs an **L2 Semantic Route** to determine the most likely domain.

3.  **Candidate Search:** The router passes the query vector to the `WeightIndex`.
    *   The index performs a Faiss similarity search to find the top-K expert adapters that are most semantically similar to the user's query.
    *   It retrieves the metadata for these candidates from its SQLite database.

4.  **Hyper-Matrix Synthesis (HMS):** The list of candidates is sent to the `HMSSynthesizer`.
    *   The synthesizer loads the tensor data for each candidate adapter (simulated in the current version).
    *   It combines these tensors into a single, new "on-the-fly" adapter using a weighted averaging scheme based on the candidates' trust scores.

5.  **Inference (Conceptual):** The synthesized adapter is conceptually loaded onto an inference engine, which then processes the original user query to generate a result. (Note: The inference engine itself is outside the scope of Genesis Core V2).

6.  **API Response:** The API server returns information about the process, including the determined domain, the expert adapters chosen as candidates, and a preview of the synthesized adapter.
