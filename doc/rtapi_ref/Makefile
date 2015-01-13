DOX = doxygen

all: doc_linux doc_pdf_linux doc_win doc_pdf_win

clean:
	rm -rf html-linux; rm -rf latex-linux
	rm -rf html-win; rm -rf latex-win
	rm -f *~

doc_pdf_linux: doc_linux
	python createDoxygenSty.py latex-linux
	@cd latex-linux; \
	pdflatex refman.tex; \
	pdflatex refman.tex; \
	latex_count=5 ; \
	while egrep -s 'Rerun (LaTeX|to get cross-references right)' refman.log && [ $$latex_count -gt 0 ] ;\
	    do \
	      echo "Rerunning latex...." ;\
	      pdflatex refman.tex ;\
	      latex_count=`expr $$latex_count - 1` ;\
	    done; \
	cp refman.pdf ../../rtapilinux_ref.pdf
	
doc_linux: 
	$(DOX) mambaRT_linux.cfg
	cp ../style/mamba_logo.png html-linux
	chmod a+r html-linux/mamba_logo.png

doc_pdf_win: doc_win
	python createDoxygenSty.py latex-win
	@cd latex-win; \
	pdflatex refman.tex; \
	pdflatex refman.tex; \
	latex_count=5 ; \
	while egrep -s 'Rerun (LaTeX|to get cross-references right)' refman.log && [ $$latex_count -gt 0 ] ;\
	    do \
	      echo "Rerunning latex...." ;\
	      pdflatex refman.tex ;\
	      latex_count=`expr $$latex_count - 1` ;\
	    done; \
	cp refman.pdf ../../rtapiwin_ref.pdf
	
doc_win: 
	$(DOX) mambaRT_win.cfg
	cp ../style/mamba_logo.png html-win
	chmod a+r html-win/mamba_logo.png
