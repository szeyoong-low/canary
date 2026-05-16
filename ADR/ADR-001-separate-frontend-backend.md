# ADR-001 — Separate frontend and backend instead of Next.js

## Decision
Instead of having Next.js handle both frontend routing and backend API routes,
the frontend and backend will be kept modular.

## Context
The frontend is a SPA that only displays a dashboard. The backend does data
processing and agent orchestration.

## Reasoning
I used Next.js in my [last project](https://diner2050.vercel.app/), but I want
to learn about each part of the stack separately without being overly reliant on
a single framework. This will allow me to choose the best tools for the job. For
example, I can leverage the strong AI and data science ecosystem around Python
to build a great backend.

Down the line, this will allow me to explore other frameworks freely. If every
component is treated as separate and only interact with one another via a limited
"contract", I can make big changes the architecture of each component without
breaking CI/CD.

## Revisit if
Highly unlikely unless for learning purposes.