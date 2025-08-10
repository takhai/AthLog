#!/bin/bash

REPO_NAME="athlog-frontend"
GITHUB_USERNAME="takhai"  # Change if different

echo "Creating GitHub repo: $REPO_NAME"
gh repo create $GITHUB_USERNAME/$REPO_NAME --public --confirm

echo "Initializing git and pushing index.html"
git init
git branch -M main
git add index.html
git commit -m "Add frontend HTML for AthLog"
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git
git push -u origin main

echo "Enabling GitHub Pages on main branch root folder"
gh api -X POST /repos/$GITHUB_USERNAME/$REPO_NAME/pages --raw-field source='{"branch":"main","path":"/"}'

echo "Done! Your site should be live at https://$GITHUB_USERNAME.github.io/$REPO_NAME/"
