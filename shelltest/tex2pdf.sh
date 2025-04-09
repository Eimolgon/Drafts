#!/bin/sh


if [ "$#" -eq "0" ]; then
    echo "Correct syntax: $0 <.tex file>"
    exit 1
fi

pdflatex $1

rm *.log
rm *.aux
rm *.out
rm *.bbl
rm *.toc
rm *.blg
