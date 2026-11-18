# Farm-to-Market working instructions

This is a COSC444 Database Systems project for three students in lab B1. Read README.md and docs/PROJECT_REQUIREMENTS.md first; use docs/RUBRIC_AND_COVERAGE.md to assess completion. Team identities are in docs/TEAM.md.

For teammate/Claude sessions, also read docs/TEAMMATE_HANDOFF.md, docs/CLAUDE_TASK_PROMPTS.md, CLAUDE.md and PROGRESS.md. Claim work before editing shared artifacts and preserve the other track's files. Agents deliver Ready for review; Abd Alrahman Ismaik alone records Accepted. Do not infer completed contributions from proposed assignments.

Teammate agents are authorized to commit scoped work to their assigned feature branch, push that branch, and open/update a PR targeting `main` with reviewer `abdalrahman-ismaik`. Do not push directly to `main`, force-push, merge, or self-approve. Record branch/PR URL and evidence in PROGRESS.md. Use a draft PR when dependencies remain; the optional read-only reviewer agent has no write authority.

## Maintained application

- `app/` is the only maintained application. Entry point: `python app/app.py`.
- Preserve Python, MySQL, Tkinter, LangChain/Gemini, BLOB photos, demo-user selection, and the Loss & Surplus advanced feature unless the user changes scope.
- Do not build from `archive/lab-example/`, extract a competing app from the ZIP, or copy KU Planner architecture/theme into this project.
- Keep the small existing module structure. Read the appropriate local skill before applying it; provenance is in docs/SKILLS.md. Impeccable covers UI work and Ponytail covers implementation simplicity.
- PRODUCT.md states product truth; DESIGN.md records the incumbent desktop theme. Proposed refinements are not implemented features.

## Database and evidence

- Setup executes `DROP DATABASE IF EXISTS farm_market_db`. Never run setup or the mutating test script against valuable data as a routine check.
- Use parameterized SQL for values, transactions for related changes, and ownership checks at the data layer. Preserve movement-based stock, explicit units, and forecast separation.
- Do not print or commit `.env`, passwords, API keys, logs containing secrets, or real operational personal data. Student identities belong in team documentation, not fictional seed accounts.
- Do not claim historical test outcomes as local results. Record environment, date, expected/actual result, and limitations for every new verification claim.
- The assistant must remain read-only. Document validation limitations honestly rather than promising unrestricted SQL safety.

## Documentation and delivery

- Proposal and supplied announcements are requirement sources; preserve distinctions and conflicting announcement history. The detailed rubric totals 100 points.
- Update setup links and documentation when paths change. Preserve original teaching/submission materials and their provenance.
- Diagram sources, poster PDF, and technical PDF are separate assessed deliverables; do not mark them complete merely because a Markdown plan exists.
- No functional changes or UI restyling were part of the initial repository/documentation pass.
