all: clean prep play

clean:
	rm -rf *~ *mamba* __init__* *.html
	rm -rf addons/*~ addons/*.pyc
	rm -rf basics/*~ basics/*.pyc
	rm -rf advanced/*~ advanced/*.pyc
	rm -rf tools/*.pyc tools/*~
	rm -rf *.jpg
	rm -rf .coverage
	rm -rf covhtml

prep: 
	cp -r ../src/mambaApi/build/lib*/* .
	cp -r ../src/mambaAddons/mamba3D/build/lib*/* .
	

play:
	python runTest.py -v 2 -o test_run.html -c

