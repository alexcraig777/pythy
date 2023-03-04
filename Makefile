all_sub_dirs = $(wildcard */.)
sub_dirs = $(filter-out __pycache__/., $(all_sub_dirs))

test:
	make -C test

clean:
	echo $(sub_dirs)
	rm -rf __pycache__ .pytest_cache
	$(foreach dir, $(sub_dirs), $(MAKE) -C $(dir) $@;)

.PHONY: test clean
