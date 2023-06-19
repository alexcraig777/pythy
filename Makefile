sub_dirs := src test

# This ensures that `src` is made before `test`, and that `test`
# is the default rule.
test: src

# Making a sub-directory just calls `make` in that directory.
$(sub_dirs):
	$(MAKE) -C $@

clean:
	echo $(sub_dirs)
	rm -rf __pycache__ .pytest_cache
	$(foreach dir, $(sub_dirs), $(MAKE) -C $(dir) $@;)

.PHONY: $(sub_dirs) clean
