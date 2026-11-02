# Project 08 — LLM Client Service (Java bridge to AI engineering)

**Status:** ⬜ Not started · **Needs:** `project-07` patterns, `09-modern-java` (`HttpClient`)

## 📌 Project Description

A small Spring Boot service that calls an LLM API reliably: typed requests and responses, timeouts, retries with backoff, and a response cache. It connects this Java repo to your AI engineering track without starting a new language track.

## 📋 Requirements
1. Endpoint that accepts a prompt and returns the model response in a typed JSON shape
2. Timeouts, bounded retries with exponential backoff, and clear errors for rate limits and failures
3. Simple in-memory cache keyed by prompt, with a size limit and eviction
4. Request logging that **never** logs API keys; the key comes from an environment variable
5. Tests that use a fake HTTP server, so the test suite never calls the real API or costs money
6. A small evaluation script: a fixed set of prompts with expected properties, and a pass-rate report

## Non-Functional Requirements
- No API key in the repository or its git history
- Configurable model name and timeout
- Document the cost of one full test run (should be zero)

## ✅ Definition of Done
- [ ] Standalone repo with README, architecture diagram, how to run
- [ ] Eval pass-rate table with real numbers, not claims
- [ ] "What broke and how I fixed it" section
