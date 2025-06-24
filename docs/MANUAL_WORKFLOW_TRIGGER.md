# Manually Triggering GitHub Workflows

This guide explains how to manually trigger GitHub Actions workflows for the NFC project.

## Using the GitHub Web Interface

1. Go to the GitHub repository: https://github.com/0xb007ab1e/NFC
2. Click on the "Actions" tab at the top of the repository
3. In the left sidebar, click on the workflow you want to run (e.g., "Python CI" or "Android CI")
4. Click the "Run workflow" button on the right side of the page
5. Select the branch you want to run the workflow on (e.g., "feature/api-endpoints")
6. Click the "Run workflow" button to start the workflow

## Using the GitHub CLI

You can also trigger workflows using the GitHub CLI if the workflow supports the `workflow_dispatch` event:

```bash
# To run the Python CI workflow
gh workflow run python-ci.yml -R 0xb007ab1e/NFC --ref feature/api-endpoints

# To run the Android CI workflow
gh workflow run android-ci.yml -R 0xb007ab1e/NFC --ref feature/api-endpoints
```

## Troubleshooting

If you encounter errors when trying to run workflows:

1. **Billing issues**: Ensure that your GitHub account has active billing or sufficient free minutes for GitHub Actions.
2. **Permission issues**: Make sure you have write access to the repository.
3. **Workflow configuration**: Check that the workflow file includes the `workflow_dispatch` trigger.
4. **Branch protection**: Ensure the workflow is allowed to run on the target branch.

## Viewing Workflow Results

1. Go to the "Actions" tab in the repository
2. Click on the workflow run you want to view
3. You'll see the status of each job and can click on individual jobs to see detailed logs
4. For failed jobs, expand the step that failed to see error messages

## CI/CD Pipeline Validation

To validate that the CI/CD pipeline is working correctly:

1. Make a small change to the code in the appropriate directory
2. Commit and push the change to a branch
3. Create a pull request targeting the main branch
4. Verify that the workflows run successfully
5. Merge the pull request and confirm that the deployment workflow runs on the main branch
