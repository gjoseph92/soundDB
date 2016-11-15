#!/bin/bash

## Build a simple Python package repository to gh-pages from wheels built into /dist in master
## Because GitHub pages doesn't auto-index directories, the script
## generates HTML files indexing the repository as required by PEP 503,
## and puts wheels in appropriately-named subfolders.

## Useage:
##
## Prereqs:
## Create the clean gh-pages branch according to the directions in docs-commit.sh
## dist/ should *not* be tracked in master
## 
## Every time you have a new release:
## Update setup.py with version info and commit in master
## git checkout gh-pages
## $ scripts/wheels-commit.sh (will build wheels and create indexing pages)
## $ git push origin gh-pages

set -e

PARENT=$(basename $(dirname $0))
if [[ $PARENT == "." ]]; then
	echo "Please run from the root of the repository, i.e. scripts/$(basename $0)"
	exit 1
fi

DISTDIR="dist"

# args: package name
normalize() {
	echo "$1" | sed 's/[-_.]+/-/g' | tr '[:upper:]' '[:lower:]'
}
# args: outfile
start_html() {
	echo '<!DOCTYPE html><html><body>' >> $1
}
# args: link text/url, outfile
append_link() {
	echo "<a href='$1'>$1</a>" >> $2
}
# args: link text/url, outfile
finish_html() {
	echo '</body></html>' >> $1
}

git checkout master
python setup.py bdist_wheel --universal
git add $DISTDIR
git stash
git checkout gh-pages
git stash pop


rm -rf $DISTDIR || { echo "Couldn't remove $DISTDIR. Make sure it's not open anywhere else."; exit 1; }
git checkout --theirs master -- $DISTDIR  || { echo "Couldn't checkout $DISTDIR. Make sure it's not open anywhere else."; exit 1; }

cd $DISTDIR
start_html index.html

# make a subdirectory for each package
for wheel in *.whl; do
	package_name=$(normalize `echo $wheel | cut -d - -f 1`)
	if [ ! -e $package_name ]; then
		mkdir $package_name
		append_link $package_name index.html
		start_html "$package_name/index.html"
	fi
	mv $wheel $package_name
	append_link $wheel "$package_name/index.html"
	echo "Put $wheel in $package_name"
done

for dir in *; do
	if [ -d $dir ]; then
		finish_html "$dir/index.html"
		echo "Built $DISTDIR/$dir/index.html"
	fi
done

finish_html index.html
echo "Built $DISTDIR/index.html"
cd ..

git add --all $DISTDIR
git commit -m "Updated wheels from `git log master -1 --pretty=short --abbrev-commit`"
