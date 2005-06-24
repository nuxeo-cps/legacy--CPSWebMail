#! /bin/sh
# clean the directory and subdirectories

clean:
	find . -name '*~' | xargs rm -f
	find . -name '*.pyc' | xargs rm -f

