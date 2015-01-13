all: doc

clean:
	rm -f *~ *.aux *.lof *.log *.out *.pdf *.toc *.tex

doc: 
	python createPythonRef.py
	cp pyref.pdf ..
	python createPythonQuickRef.py
	cp pyquickref.pdf ..
