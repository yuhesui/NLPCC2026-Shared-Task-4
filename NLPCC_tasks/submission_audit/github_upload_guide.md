# GitHub Upload Guide

## Repository Visibility

Use a **private** GitHub repository until organizers explicitly authorize sharing. GitHub is a source/package delivery mechanism, not an official NLPCC submission claim. Share a release ZIP or grant organizer access only after confirming the required channel.

## Git LFS Requirement

Git LFS is required. `package/models/finbert_tone_chinese_e91b1a3/model.safetensors` exceeds GitHub's 100 MiB normal Git limit. `.gitattributes` tracks all `package/models/**`, `*.safetensors`, `*.bin`, and `*.pt` files through LFS. If organizers cannot access LFS objects, provide a SHA-256-verified ZIP/release artifact containing `package/models/` instead.

## Exact Commands

```powershell
cd D:\Projects\NLPCC2026-Shared-Task-4\NLPCC_tasks
git init
git lfs install
git lfs track "package/models/**"
git add .gitattributes
git add .
git status
git commit -m "NLPCC Task 4 submission package"
git remote add origin <PRIVATE_REPO_URL>
git push -u origin main
```

## Before Upload

Verify `git status` does not stage raw datasets, hidden 2026 data, runtime logs, `.env`, credentials, user cache paths, parent-workspace files, or report-only research folders. Verify `git lfs ls-files` lists the model weights. Run the clean-environment checks in `RUN_GUIDE.md` and inspect `submission_audit/submission_ready_decision.md`.

## Do Not Push

- hidden 2026 or organizer-private data;
- private local logs, session state, or A-list artifacts with local absolute paths;
- user caches, secrets, tokens, and `.env`;
- large raw research outputs or parent report folders;
- Prompt06/Prompt07b research/replay code or any alpha-grid artifact.
