all: doc

clean:
	rm -f *~ *.aux *.lof *.log *.out *.pdf *.toc *.tex

doc: 
	python createPython3DRef.py
	cp 3Dpyref.pdf ..
	python createPython3DQuickRef.py
	cp 3Dpyquickref.pdf ..
