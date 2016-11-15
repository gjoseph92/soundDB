#!/bin/bash

## Commit Sphinx-built docs in a subdirectory to the root of gh-pages

## Initial setup:
##
## You have your Sphinx documentation in some folder in the repo, call it `doc`.
## (Inside this is `_build/html`.)
## You need a .gitignore for `doc/_build` in master!
## `_build` must not be tracked in either master or gh-pages. This ensures it will not
## be removed or modified when you change branches, as git does not touch untracked files
## during checkouts.
##
## Then, create your gh-pages branch:
## $ git checkout --orphan gh-pages
## $ rm -rf *       # you want a clean start for gh-pages
## $ rm .gitignore  # if it exists
## [add this script to a scrips directory and set the name for DOCDIR in it]
## $ touch .nojekyll
## $ echo "doc" > .gitignore   # we want to ignore the docs directory so it's never touched by git
## $ git add .
## $ git commit -m "Initial gh-pages commit"
##
##
## Now, to use it:
## On master, modify your docs
## `make html`
## When you're satisfied, commit or stash any changes in master. (Remember, `doc/_build` should not be tracked.)
## cd to the root of the repo
## $ git checkout gh-pages
## $ scrips/docs-commit.sh
## $ git checkout master

# Change this to the name of your documentation directory (doc, docs, etc.)

set -e

DOCDIR="doc"


SCRIPTS=$(basename $(dirname $0))
if [[ $SCRIPTS == "." ]]; then
	echo "Please run from the root of the repository, i.e. scripts/$(basename $0)"
	exit 1
fi

if [ ! -e $DOCDIR ]; then
	echo "$DOCDIR does not exist. Go back to master and build yourself some docs!"
	exit
fi

# like rm -rf *, but skip self
echo "Cleaning working directory"
for f in *
do
	if [ "$f" != "$SCRIPTS" -a "$f" != "$DOCDIR" ]; then
		rm -rf $f
	fi
done

echo "Copying $DOCDIR/_build/html/* to working directory"
cp -r $DOCDIR/_build/html/* .
git add --all .
git reset HEAD $DOCDIR
git reset HEAD $SCRIPTS
git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`"
echo "Done!"