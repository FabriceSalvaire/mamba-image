all: doc

clean:
	rm -f *~ *.aux *.lof *.log *.out *.pdf *.toc examples.tex
	rm -rf examples_icons examples.html examples_list.php

doc: 
	python examples2tex.py
	pdflatex mamba-um.tex
	pdflatex mamba-um.tex
	cp mamba-um.pdf ..
