all: doc

clean:
	rm -f *~ *.aux *.lof *.log *.out *.pdf *.toc

doc: 
	pdflatex standards.tex
	pdflatex standards.tex
	cp standards.pdf ..
