# Farm-to-Market: Claude agent entry point

Read [AGENTS.md](AGENTS.md), [README.md](README.md), [teammate handoff](docs/TEAMMATE_HANDOFF.md), and [PROGRESS.md](PROGRESS.md) before changing anything. Then use the assigned copy-paste brief in [Claude task prompts](docs/CLAUDE_TASK_PROMPTS.md).

This is an existing COSC444 lab B1 application, not a new build. Preserve Python/MySQL/Tkinter, LangChain/Gemini, BLOB images, demo-user selection, movement-based stock and the selected Loss & Surplus feature. Do not add another advanced feature or migrate the stack.

The original proposal PDF, supplied announcements/full rubric, and Lab 6 slides are saved under `docs/`. Current evidence is `docs/evidence/VALIDATION.md` and `docs/evidence/AI_VALIDATION.md`. Original guide/ZIP claims are historical. Never fabricate a test result, contribution, registration, booking, or reviewer approval.

Database setup drops `farm_market_db`; the business-rule script mutates records and executes on import. Use only an explicitly disposable database instance for those operations. `.env`, `.venv/`, `.local/`, credentials and the original machine's temporary server are not portable project assets. Never print or commit secrets.

Complete the assigned editable artifacts, exports, checks and handoff notes. You are authorized to create your assigned feature branch, commit scoped work, push that branch and open/update a pull request targeting `main`, requesting review from `abdalrahman-ismaik`. Record the PR URL and evidence in `PROGRESS.md` and deliver **Ready for review** to Abd Alrahman Ismaik. Follow the PR workflow in `docs/CLAUDE_TASK_PROMPTS.md`. Never push directly to `main`, force-push, merge a PR, self-accept, submit to eLearn, book anything, or change business policies/schema without the corresponding authorization. Draft PRs may expose blocked/incomplete work but must be labeled honestly. Investigate routine blockers and finish independent work; record external dependencies and unresolved policy questions precisely.
