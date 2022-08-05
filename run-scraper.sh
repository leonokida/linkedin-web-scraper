#!/bin/bash

while getopts v:i: flag
do
    case "${flag}" in
        v) version=${OPTARG};;
        i) input=${OPTARG};;
    esac
done

executable=$(echo "$version" | tr '[:upper:]' '[:lower:]')

if [ "$executable" = "firefox" ]; then
    path="firefox-version/linkedin-scraper-firefox.py"
else
    path="chrome-version/linkedin-scraper-chrome.py"
fi

urls=$(cat $input)

for url in $urls; do
    python3 $path $url
done