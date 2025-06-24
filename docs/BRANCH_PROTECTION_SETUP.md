# Branch Protection Setup

This document describes how to set up branch protection rules for the NFC project repository.

## Setting Up Branch Protection Rules

1. Go to the repository settings on GitHub: https://github.com/0xb007ab1e/NFC/settings/branches

2. Under "Branch protection rules", click "Add rule"

3. For "Branch name pattern", enter `main`

4. Enable the following settings:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (set to 1 approval)
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging

5. In the "Status checks that are required" section, search for and select:
   - `test (3.9)` and `test (3.10)` from the Python CI workflow
   - `lint`, `test`, and `build` from the Android CI workflow

6. Additional recommended settings:
   - ✅ Do not allow bypassing the above settings
   - ✅ Restrict who can push to matching branches (add project administrators)

7. Click "Create" to save the rule

## Develop Branch Protection

Repeat the steps above for the `develop` branch, but you might want to use slightly less restrictive settings:

1. For "Branch name pattern", enter `develop`
2. Enable the following settings:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging

3. In the "Status checks that are required" section, select the same checks as for main

4. Click "Create" to save the rule

## Feature Branch Workflow

With these protection rules in place, the standard workflow will be:

1. Create feature branches from `develop`
2. Make changes and push to feature branches
3. Create pull requests to merge feature branches into `develop`
4. Once features are tested and stable in `develop`, create a pull request to merge `develop` into `main`

This workflow ensures that only well-tested code reaches the main branch.
