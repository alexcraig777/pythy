sub_dirs = src test

dists = $(wildcard dist/*)
test_dists = $(foreach d, $(dists), test-$(d))


# Build the distributions.
dist: .venv clean
	. .venv/bin/activate && python3 -m build

# Make the virtual environment from the requirements file.
.venv: requirements.txt
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

# Test all built distributions.
# TODO: This has a bug: the $(test_dists) is evaluated before `dist`
# is built, so the dists that are going to be tested are the ones
# that were previously built, which may be wrong or even not exist.
# Figure out how to make this evaluate only after `dist` is built.
test_dists: dist $(test_dists)
	@echo "[+] All distros passed all tests!"

# Test an individual distribution.
$(test_dists): test-%: % test
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
