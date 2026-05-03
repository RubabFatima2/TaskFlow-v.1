# Gemini API + OpenAI Agents SDK Compatibility Guide

## Overview

This document explains how the Gemini API can be used with the OpenAI Agents SDK using the OpenAI-compatible endpoint provided by Google.

Although the OpenAI Agents SDK is designed for OpenAI models, Gemini exposes an OpenAI-compatible interface that allows it to work with the SDK with minimal adjustments.

---

## Key Idea

Gemini provides an OpenAI-compatible REST API.

This allows us to:

- Use OpenAI client libraries
- Use OpenAI Agents SDK abstractions
- Route requests to Gemini instead of OpenAI

---

## How Compatibility Works

Instead of calling OpenAI directly, we override the base URL of the OpenAI client and point it to Gemini's endpoint.

### Architecture Flow

User Code → OpenAI Agents SDK → OpenAI Client (modified base_url) → Gemini API

---

## Installation

```bash
pip install -Uq openai-agents
```

---

## Complete Working Example

```python
import os
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
from google.colab import userdata

# Get Gemini API Key
gemini_api_key = userdata.get("GEMINI_API_KEY")

# Validate API Key
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined.")

# Create OpenAI-compatible client pointing to Gemini
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Define model using Gemini
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Configure runner
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Create agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful AI assistant"
)

# Run agent
result = Runner.run_sync(
    agent,
    "Explain Agentic AI in simple words",
    run_config=config
)

print(result.output)
```

---

## Step-by-Step Explanation

### 1. API Key Setup
We retrieve the Gemini API key securely (e.g., from Colab userdata or environment variables).

### 2. Custom OpenAI Client
We create an `AsyncOpenAI` client but override:

- `base_url` → Gemini endpoint
- `api_key` → Gemini API key

This tricks the SDK into sending requests to Gemini.

### 3. Model Configuration
We use `OpenAIChatCompletionsModel` but specify:

- model = "gemini-2.0-flash"

This works because Gemini accepts OpenAI-style chat requests.

### 4. RunConfig Setup
We pass:

- model
- model_provider (same external client)

This ensures the runner uses Gemini for execution.

### 5. Agent Execution
The agent runs normally using the SDK, but all requests are routed to Gemini.

---

## Why This Works

Gemini implements an OpenAI-compatible API layer.

This means:

- Same request format
- Same response structure
- Same chat completions interface

So the SDK cannot distinguish between OpenAI and Gemini.

---

## Limitations

This is not native compatibility. Some limitations may include:

- Tool calling inconsistencies
- Function schema differences
- Streaming behavior differences
- Partial feature support

---

## When to Use This Approach

Use this approach when:

- You want to use Gemini with minimal setup
- You are prototyping or learning
- Your agent logic is not highly complex

---

## When to Avoid

Avoid this approach when:

- You need full production reliability
- You rely heavily on advanced tool calling
- You encounter compatibility issues

In such cases, consider building a custom agent loop.

---

## Conclusion

Gemini is compatible with the OpenAI Agents SDK through an OpenAI-compatible API layer.

This allows developers to reuse the SDK while leveraging Gemini models.

However, this compatibility is indirect and may not support all advanced features.

---

## Summary

- ✅ Works using OpenAI-compatible endpoint
- ⚠️ Not natively supported
- 🚀 Great for learning and prototyping
- 🔧 May require custom solutions for advanced use cases

