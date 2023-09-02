dists = $(wildcard dist/*)
test_dist_targets = $(foreach d, $(dists), test-$(d))


# Build the distributions.
dist: .build-venv clean
	. .build-venv/bin/activate && python3 -m build

# Make the virtual environment from the requirements file.
.build-venv: build-requirements.txt
	python3 -m venv .build-venv
	. .build-venv/bin/activate && pip install -r build-requirements.txt

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
# build the shared objects in it (accomplished by `test`).
$(test_dist_targets): test-%: % test
	@echo "[ ] Testing $< . . ."
	rm -rf .test-venv
	python3 -m venv .test-venv
	. .test-venv/bin/activate && pip install -r test-requirements.txt
	. .test-venv/bin/activate && pip install $<
	. .test-venv/bin/activate && cd test && pytest
	@echo "[+] Distribution $< passed all tests"


test:
	$(MAKE) -C $@

clean:
	rm -rf __pycache__ .pytest_cache .test-venv dist src/*.egg-info
	$(MAKE) -C test $@
	$(MAKE) -C src/pythy $@

.PHONY: test clean test_dists _test_dists $(test_dist_targets)
