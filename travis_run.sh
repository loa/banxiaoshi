#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

function set_travis_user {
    git config user.name "Travis CI"
    git config user.email "notifications@travis-ci.org"
}

# Create needed directories
rm -rf data gh-pages
git clone --single-branch -b data "https://${GH_TOKEN}@github.com/loa/banxiaoshi.git" data
mkdir gh-pages

# Collect data from Skritter API
python3 banxiaoshi/collect_data.py

# Generate static webpage
python3 banxiaoshi/generate_static.py

# Push updates to data branch
cd data/
set_travis_user
git add .
git commit -m "Automatic update to data" || true  # ignore if nothing has changed
git push \
    --force \
    --quiet \
    "https://${GH_TOKEN}@github.com/loa/banxiaoshi.git" \
    data > /dev/null 2>&1

# Push newly generated banxiaoshi pages
cd $DIR/gh-pages/
git init
set_travis_user
touch .nojekyll
git add .
git commit -m "Deploy to Github Pages"
git push \
    --force \
    --quiet \
    "https://${GH_TOKEN}@github.com/loa/banxiaoshi.git" \
     master:gh-pages > /dev/null 2>&1

