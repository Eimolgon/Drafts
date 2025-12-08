# !/usr/bin/env

if [[$# -lt 1]]; then
    echo "Usage: $0 main.tex"
    exit 1
fi

FILE="$1"
BASE="${FILE%.tex}"

pdflatex "$FILE"

bibtex "$BASE"

pdflatex "$FILE"
pdflatex "$FILE"

rm -f "$BASE.aux" "$BASE.bbl" "$BASE.blg" "$BASE.log" "$BASE.out" "$BASE.toc" "$BASE.lof" "$BASE.lot" "$BASE.synctex.gz"

echo "Document compiled. $BASE.pdf"
