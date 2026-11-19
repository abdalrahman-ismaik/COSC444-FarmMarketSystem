# GitHub delivery

The repository presents the maintained `app/` beside the final application ZIP, technical PDF, approved poster and editable report bundle. The root README is the setup/download entry point; supporting sources, requirements, diagrams and evidence remain under `docs/`.

## Release checks

1. Rebuild the application archive with `scripts/build_candidate.py` using a fresh extraction directory.
2. Confirm extracted application files match the working tree, package CRC/member hashes pass, and no real `.env`, credentials, environments or caches are included.
3. Verify the final PDF and editable bundle using [BUILD_DOCUMENTS.md](BUILD_DOCUMENTS.md). Inspect changed report pages after compilation.
4. Review `git diff --cached --check` and the staged file list before committing.
5. Push a scoped feature branch and open a PR targeting `main`, requesting reviewer `abdalrahman-ismaik` when GitHub permits it. Do not push directly to `main`, merge or self-approve.

Publication status and the branch/PR URL are recorded in [PROGRESS.md](../PROGRESS.md). GitHub publication is separate from the course submission upload. No fresh-device or application regression result is implied by archive/document checks.
