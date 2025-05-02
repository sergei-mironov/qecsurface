R = ..
PY = $(shell find $(R)/python -name '*.py')
SH = $(shell find $(R)/sh -name '*')
TOP = $(addprefix $(R)/,Makefile env.sh)
LIB = preamble.tex template.tex
TEX = report.tex aitalks.tex
TGZ = $(subst .tex,.tar.gz,$(TEX))
PDF =  $(subst .tex,.pdf,$(TEX))

.PHONY: all
all: report.pdf

aitalks.tex: ./ai/check_matrix.tex ./ai/theory.tex

$(TGZ): %.tar.gz: %.tex Makefile $(LIB) $(PY) $(TOP) $(SH)
	cd $R && tar -czf \
		$(shell realpath --relative-to=$R $@) \
	  $(foreach prereq,$^,$(shell realpath --relative-to=$R $(prereq)))

%.sig: %.tar.gz
	gpg --armor --yes --output $@ --detach-sign $<

$(PDF): %.pdf: %.sig
	mkdir _build || true
	sed -e 's@!BODYFILE!@$*.tex@g' \
	    -e 's@!DESTFILE!@$*.pdf@g' \
	    -e 's@!GPGSIGFILE!@$*.sig@g' \
	    -e 's@!SOURCEFILE!@$*.tar.gz@g' \
		template.tex > _report.tex
	latexmk -shell-escape -pdf -interaction=nonstopmode \
	        -latex=pdflatex --halt-on-error -outdir=_build  _report.tex
	cp _build/_report.pdf $*.pdf
