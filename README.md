# Autonome

Autonome is Ric Richardson's architecture for systems that accumulate judgment, not just knowledge.

It extends the LLM-wiki pattern: a maintained source of truth captures what is known, while a governed decision queue captures what should be done next. Over time, the system learns preferences, priorities, risk boundaries, and operating judgment from human decisions.

## Why it matters

Most AI systems answer questions. An Autonome is designed to run work.

The long-term goal is progressive autonomy: the system first observes, then recommends, then drafts, then executes bounded low-risk work as it earns trust. Humans remain sovereign governors over strategy, ethics, risk, money, law, credentials, and external commitments.

## Core ideas

- **Source of truth** — structured files or records that humans and AI agents can both read and maintain.
- **Continuous reconciliation** — new inputs update the source of truth, strengthen existing claims, and flag contradictions.
- **Decision queue** — unresolved judgments are surfaced as decisions, not just tasks.
- **Authority ladder** — autonomy increases only after demonstrated reliability.
- **Governance boundary** — high-risk or irreversible actions remain human-approved.

## Planned reference implementation

- MCP server for agent access to an Autonome source of truth.
- Knowledge graph for people, projects, companies, decisions, and relationships.
- Decision queue interface for review, approval, delegation, and feedback.
- Personal, role-based, and organisational Autonomes.

## Licensing

Personal, educational, research, and non-commercial experimentation is encouraged.

Commercial implementations, hosted services, enterprise deployments, consulting offerings, resale, white-label products, software-as-a-service platforms, managed services, or commercial derivatives may require a licence where they implement patent-backed Autonome concepts.

## Public disclosure boundary

This repository is a public-facing overview and reference surface. Patent-sensitive claim detail, private operating records, credentials, commercial negotiations, and internal project data do not belong here.
