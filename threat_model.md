# STRIDE Threat Modeling Assessment: Shopping Assistant Agent

This document performs a systematic threat modeling assessment of the **Shopping Assistant Agent** codebase, configuration, and architecture based on the STRIDE framework.

---

## 1. System Boundaries & Data Flow Map

### Trust Boundaries
1. **User ↔ Agent Interface**: The boundary between the untrusted external user and the LLM agent.
2. **Agent ↔ Tool Execution**: The boundary where the LLM decides to call the python-implemented `redeem_discount_code` function.
3. **Application ↔ External Services**: The connection to the Google Gemini API (using the mock API key).

### Data Stores
* **In-Memory Stores**:
  - `discount_codes` (dict): Tracks if `WELCOME50` or `SUMMER20` are redeemed (`True`/`False`).
  - `registered_users` (set): Mock list of allowed user IDs (`user_1`, `user_2`, `user_3`, `Huzai134`).
  - `Runner` session history and state.

---

## 2. STRIDE Pillar Evaluation

### 👤 Spoofing (Identity Spoofing)
* **Threat**: A user can spoof their identity by claiming to be another registered user (e.g., passing `Huzai134` as the `user_id` argument to the tool).
* **Current Boundary Check**: The system relies on the user self-reporting their user ID. There is no secure authentication (e.g., JWT, OAuth, session tokens) verifying the user's identity before calling the tool.
* **Mitigation**: Implement cryptographic token verification (like a verified session token) and retrieve the user ID directly from the authenticated session context rather than letting the LLM or user pass it as a raw string parameter.

### ✍️ Tampering (Data Manipulation)
* **Threat**: An attacker could tamper with the global in-memory state or try to manipulate the `code` parameter.
* **Current Boundary Check**: 
  - The in-memory variables `discount_codes` and `registered_users` are simple global mutable structures in `app/tools.py`.
  - Concurrent requests could cause race conditions (e.g., two threads modifying `discount_codes["WELCOME50"]` at the exact same time, leading to double-redemption).
* **Mitigation**: Use atomic operations or database transactions (e.g., using Cloud SQL with transactions) rather than global in-memory Python dictionaries to persist discount codes and user data.

### 🛡️ Repudiation
* **Threat**: A user redeems a discount code but denies doing so, and the system lacks a non-repudiable audit trail.
* **Current Boundary Check**: No permanent transaction ledger or audit log is maintained. A simple Python print or dictionary update occurs, but no structured, tamper-proof logs are written to external storage.
* **Mitigation**: Log every successful and failed redemption to a secure, write-only audit trail (e.g., Cloud Logging with strict IAM controls) recording the timestamp, verified user ID, and action taken.

### ℹ️ Information Disclosure
* **Threats**: 
  1. API key exposure.
  2. Leakage of valid discount codes or registration IDs to unauthenticated users.
* **Current Boundary Check**: 
  - **API Key**: The mock API key `api_key="AIzaSyD-mock-key-value-12345"` is hardcoded in `app/agent.py`. While used for security gating tests, real credentials should never be committed.
  - **Logic Leakage**: An unauthenticated user could prompt the LLM to output the entire list of valid discount codes or registered user IDs since they reside in the same runtime memory space.
* **Mitigation**: 
  - Use Secret Manager for the Gemini API key.
  - Do not expose the list of registered users or valid codes directly to the LLM agent's prompt or tools (the tool should only check matching, not list them).

### 💥 Denial of Service (DoS)
* **Threat**: A user floods the agent with complex reasoning requests or repeatedly calls the tool to exhaust system memory and Gemini API quotas.
* **Current Boundary Check**: The FastAPI app serving the agent does not implement rate-limiting or request size limits.
* **Mitigation**: Implement rate-limiting middleware (e.g., `slowapi` or Cloud Armor) at the network layer and configure maximum token usage limits in Gemini configurations.

### 🔑 Elevation of Privilege
* **Threat**: An unauthenticated user accesses the discount redemption tool or executes commands on the system.
* **Current Boundary Check**: The system relies on the LLM to gate access to the tool based on system instructions, which can be bypassed using prompt injection.
* **Mitigation**: Enforcement of access control should happen programmatically (in Python code) prior to tool execution by checking the caller's actual role/permissions, rather than relying solely on the LLM's adherence to instructions.
