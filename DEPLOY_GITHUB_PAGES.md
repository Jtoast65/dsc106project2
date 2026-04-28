# GitHub Pages Deployment

This project is ready to deploy as a static site.

## Files to upload

Make sure these files stay together in the same folder in your GitHub repo:

- `index.html`
- `styles.css`
- `pro_side_charts.jpg`
- `con_side_charts.jpg`
- `.nojekyll`

Optional supporting files:

- `checkpoint_submission.pdf`
- `checkpoint_page_1_true.png`
- `checkpoint_page_2_false.png`
- `checkpoint_page_3_writeup.png`
- `make_checkpoint_submission.py`

## Fastest GitHub Pages setup

1. Create a new GitHub repository.
2. Upload the files listed above to the root of that repository.
3. Open the repository on GitHub.
4. Go to `Settings` -> `Pages`.
5. Under `Build and deployment`, set:
   - `Source` = `Deploy from a branch`
   - `Branch` = `main`
   - `Folder` = `/ (root)`
6. Save.
7. Wait about 1–3 minutes for GitHub Pages to publish.

Your public URL will usually look like:

`https://YOUR_GITHUB_USERNAME.github.io/REPO_NAME/`

## If you want to use git locally

Run these commands from this folder:

```bash
git init
git add .
git commit -m "Add DSC 106 Project 2 final submission"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/REPO_NAME.git
git push -u origin main
```

Then enable GitHub Pages in the repo settings using the steps above.

## Before submitting

- Replace the group member placeholder in `index.html`
- Open the public URL and verify:
  - images load correctly
  - text formatting looks right on desktop
  - the page also looks okay on mobile
