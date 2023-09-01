sub_dirs = src test

dists = $(wildcard dist/*)
test_dist_targets = $(foreach d, $(dists), test-$(d))


# Build the distributions.
dist: .venv clean
	. .venv/bin/activate && python3 -m build

# Make the virtual environment from the requirements file.
.venv: requirements.txt
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

# Test all built distributions.
# This recursively calls make on the `_test_dists` rule.
# This is necessary so that the `test_dist_targets` can be evaluated
# afresh after the dists have all been built. Otherwise the wildcard
# prereqs can't be guaranteed to exist.
test_dists: dist
	$(MAKE) _test_dists

# This is recursively called from the `test_dists` rule so that the
# wildcard prereqs are guaranteed to be evaluated after they have all
# been built.
_test_dists: $(test_dist_targets)
	@echo "[+] All distros passed all tests!"

# Test an individual distribution.
# Before we can run `pytest` in the `test` directory, we need to
# build the shared objects in it.
$(test_dist_targets): test-%: % test
	@echo "[ ] Testing $< . . ."
	rm -rf .test-venv
	python3 -m venv .test-venv
	. .test-venv/bin/activate && pip install -r test-requirements.txt
	. .test-venv/bin/activate && pip install $<
	. .test-venv/bin/activate && cd test && pytest
	@echo "[+] Distribution $< passed all tests"


# Making a sub-directory just calls `make` in that directory.
$(sub_dirs):
	$(MAKE) -C $@

clean:
	rm -rf __pycache__ .pytest_cache .test-venv dist
	$(foreach dir, $(sub_dirs), $(MAKE) -C $(dir) $@;)

.PHONY: $(sub_dirs) clean test-dists
