---
name: generate-expert-readme
description: Generates a complete, professional, highly structured, and dynamic README.md for both Frontend/General projects and Backend/ML API projects.
---

# Generate Expert README

When the user asks you to generate a README for their project, follow these instructions to produce a production-grade README.md file that adapts dynamically to the project type.

## Phase 1: Project Analysis
Analyze the workspace (using `list_dir`, `view_file`, etc.) to determine the nature of the project.
- **Frontend / General:** Look for standard web frameworks, UI components, HTML/CSS/JS, React/Vue/Svelte, `package.json`, etc.
- **Backend & ML:** Look for API routers (FastAPI, Flask, Express), Database connectors, LLM code, PyTorch/TensorFlow, model weights, `requirements.txt`, etc.
- **Fullstack:** If both are present, merge the requirements logically or focus on the requested component.

## Phase 2: Content Generation Rules

### Global Rules
1. **NO PLACEHOLDERS:** Do not output "[Insert description here]". Extrapolate, infer, and generate realistic and highly accurate content based on your analysis of the codebase.
2. **Professional Tone:** The README must be comprehensive, production-grade, and suitable for developers, engineers, and system architects. Ensure clarity, consistency, and strong technical depth.
3. **Diagrams:** Use Mermaid.js syntax. Ensure all node labels containing special characters are enclosed in quotes (e.g., `id["Label (Extra Info)"]`). Ensure diagrams are fully syntactically correct and renderable.
4. **Code Snippets:** Provide concrete, practical code snippets for timing execution, APIs, and logging. Use the primary programming language of the analyzed project.

### Template A: Frontend / General Project Structure
If the project is primarily a frontend or general application, ensure the README includes:

1. **Project Overview:** Description, objectives, and key features.
2. **Architecture Overview:** High-level system design with a Package Diagram (and explanation).
3. **System Design Diagrams:**
   - Activity Diagram
   - Use Case Diagram
   - Sequence Diagram
   - Class Diagram
4. **Installation & Setup:** Prerequisites, step-by-step instructions, and environment setup.
5. **Usage:** How to run the project and example workflows/commands.
6. **Performance Measurement & Execution Timing:**
   - Explain how to measure execution time.
   - Include instructions to extract execution time from logs.
   - Instructions to display execution time to the user payload/UI.
   - Code snippets to start/stop timers around specific actions.
7. **Project Structure:** Folder tree with file breakdown and detailed descriptions.
8. **Configuration & Hyperparameters:** Markdown table (Name | Description | Default Value | Type | Range/Options).
9. **Metrics & Evaluation:** Table defining all evaluation/performance metrics used (Metric | Description | Formula | Use Case).
10. **Dependencies:** List of libraries, frameworks, and tools.
11. **Contributing Guidelines.**
12. **License.**

### Template B: Backend & Machine Learning Systems
If the project includes Backend routes, AI/ML models, or LLMs, ensure the README includes:

1. **Project Overview:** Clear description, problem statement, objectives, and key features (highlighting ML + API capabilities).
2. **Architecture Overview:** End-to-end system architecture (data flow, model flow, API interaction), including a Package Diagram.
3. **System Design Diagrams:**
   - Activity Diagram (request → processing → response)
   - Use Case Diagram (users, systems, API consumers)
   - Sequence Diagram (API call → model inference → response)
   - Class Diagram (core components, services, models)
4. **Installation & Setup:** Prerequisites (Python, Frameworks, exact CUDA/GPU specs if found), Environment, and Dependency Installation.
5. **Usage:** How to run the backend server, trigger model inference (API/CLI), and example I/O.
6. **Performance, Timing & Latency Measurement:** Detailed instrumentation rules:
   - **A. Inference/Query Time:** How to capture timing from logs and return latency in API responses (e.g., `response_time_ms`).
   - **B. Code-Level Instrumentation:** Examples of start/stop timers around inferences, middleware/decorator time trackers for APIs.
   - **C. Training Time (If applicable):** How to track total training time, epoch tracking, and time logging.
   - **D. Logging Strategy:** Explain how you capture latency, model times, bottlenecks, and observability tools.
7. **Project Structure:** Directory breakdown with clear explanations.
8. **Configuration & Hyperparameters:** Markdown table covering Model parameters and API settings (Name | Description | Default Value | Type | Range/Options).
9. **Metrics & Evaluation:** Define ML evaluation metrics (e.g., accuracy, F1) and System metrics (latency, throughput). Present in a table.
10. **Dependencies:** Runtime libraries and ML frameworks.
11. **API Documentation:** Comprehensive API Endpoint list, Request/Response Schemas, and Error Handling examples.
12. **Contributing Guidelines.**
13. **License.**

## Phase 3: Output Strategy
By default, overwrite or create the `README.md` file in the root of the project using your exact generated content. Write it directly without skipping sections or leaving missing data.

Always confirm execution and provide a summary of what you discovered and populated into the README.
