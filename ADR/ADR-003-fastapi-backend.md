# ADR-003 — FastAPI for backend

## Decision
Use FastAPI as the backend framework instead of Django.

## Context
The backend exists solely to serve JSON to a React frontend. It needs to
run an async LangGraph agent pipeline to fetch and process data. It also needs
to and stream LLM tokens to the insight panel in real time via SSE.

## Reasoning
Python is the right language for this project because the data science ecosystem
(pandas, polars, yfinance) lives there, and all the major AI agent frameworks
(LangChain, LangGraph) are Python-first. 

Django carries templating, a form system, and an ORM — none of which are used
in an API-only backend. More critically, FastAPI is async-native (built on
Starlette + asyncio), which is required for SSE streaming. Django added async
support later and it remains patchy — streaming responses require workarounds,
and the ORM blocks the event loop unless wrapped in `sync_to_async`.

The Python AI/ML ecosystem (LangGraph, Anthropic SDK, pandas) is written against
asyncio. FastAPI integrations are first-class; documentation examples assume it.

FastAPI also provides automatic OpenAPI docs, which I found to be immensely
helpful when testing and generating types for TypeScript.

## Consequences
None foreseeable until Phase 3.

## Revisit if
Highly unlikely unless for learning purposes.