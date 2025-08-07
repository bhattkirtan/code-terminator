# 🧠 AI DevOps Agent Platform – Architecture Summary

## 🔁 Execution Flow

```mermaid
flowchart TD
    subgraph Input
        A[User Prompt] --> M[PromptEnhancerAgent]
        A1[Screenshots Upload] --> N[EmbeddingAgent]
    end

    subgraph Generation
        M --> B[VisionAgent]
        B --> C[LayoutAgent]
        C --> D[CodeAgent]
        D --> E[StyleAgent]
        D --> F[StubAgent]
    end

    subgraph Validation
        D --> G[ValidationAgent]
        G -->|✅ Pass| H[CodeReviewAgent]
        G -->|❌ Fail| D
    end

    subgraph Improvement
        H --> I[EnhancementAgent]
        I --> D
    end

    subgraph Finalization
        D --> J[DocumentationAgent]
        D --> K[PipelineAgent]
        D --> L[CarbonAgent]
    end

    %% Embedding Agent informs core stages
    N --> B
    N --> C
    N --> D
    J --> N
    H --> N
```

---

## 🧠 Agent Role Summary

| Agent | Description |
|-------|-------------|
| **PromptEnhancerAgent** | Enriches vague prompts with context (design goals, UX intent, architecture hints) |
| **VisionAgent** | Parses screenshots into structured UI elements |
| **LayoutAgent** | Translates UI trees into Angular-compatible layout (HTML) |
| **CodeAgent** | Generates Angular TS/HTML/SCSS following best practices |
| **StyleAgent** | Applies SCSS/themes from uploaded files or inferred design |
| **StubAgent** | Creates service stubs and mock HTTP endpoints |
| **ValidationAgent** | Runs `ng build`, `ng test`, `ng lint` and parses errors |
| **CodeReviewAgent** | Flags UI/UX violations, Angular antipatterns, accessibility issues |
| **EnhancementAgent** | Recommends improvements and re-generates code if necessary |
| **DocumentationAgent** | Writes README, docstrings, and usage guides for all components |
| **PipelineAgent** | Generates GitHub Actions, Dockerfiles, and CI/CD configs |
| **CarbonAgent** | Tracks estimated CO₂ per model/token run |
| **EmbeddingAgent** | Ingests all uploaded screenshots and generated artifacts early in the flow. Enables semantic memory across agents for UI, code reuse, and layout consistency. |

---

## 🎯 System Goals

- ✅ Generate clean Angular v20 code from legacy screenshots
- 🧠 Automatically enhance vague instructions into actionable prompts
- 🧪 Validate builds + test output
- 📋 Ensure code review + UX best practices
- 📦 Create docs + pipeline
- 🔁 Embed all outputs for learning, reuse, linking
- 🌱 Track carbon emissions per model run

---

## 🧩 Use Cases Enabled

| User Action | System Behavior |
|-------------|-----------------|
| "Modernize this UI" + screenshot | Full Angular code is generated |
| Prompt is vague | PromptEnhancer expands it |
| Build fails | ValidationAgent triggers retry |
| Review fails | EnhancementAgent proposes fixes |
| Want to reuse components | EmbeddingAgent matches similar ones |
| Need GitHub CI | PipelineAgent generates config |
| Need docs | DocumentationAgent adds README, usage |
