# Nextflow component testing with nf-test

Use this profile with the applicable nf-core testing conventions. Resolve paths, required plugins
and execution profiles from the repository. The implementation plan declares the testing phase for the current increment.

## Reference-validation phase

When the plan declares `tester: reference-validation`, verify that the resolved reference inputs are usable, then write executable validations for the reference outputs before those outputs
are generated. Use the input, prerequisite, output and
validation contracts resolved by the plan.

Validate declared filenames, provenance where relevant, formats, cardinality, metadata
associations, semantic properties, tolerances, failure behavior and reproducibility. A successful
command or nonempty file is insufficient when content is specified.

The test harness may run on the host, but commands exercising reference behavior must use the
exact execution environment pinned by the plan. Do not fall back to undeclared host tools.

Establish RED before the reference-generation phase. Do not generate the reference outputs,
create nf-test production tests, or create snapshots in this phase. Missing source data,
runtime dependencies or required tools are environment failures, not valid RED.

## Production-test phase

Proceed only when the plan declares `tester: production-test` and the corresponding reference
validation is GREEN. Use process tests for new local modules and workflow tests for local
subworkflows or wiring. Create missing tests or extend existing coverage; preserve unrelated
coverage. Stub tests verify declared outputs and wiring but do not replace real functional tests.

Components whose plan contains only direct implementation phases do not receive a local TDD cycle.

When those concrete files are untracked, the committed test command or its repository setup must
materialize them with the versioned scripts before nf-test runs. Verify this from an empty target
workspace so a clean checkout does not depend on a previous builder session.

Build all nf-test expectations and snapshots from the verified reference outputs before production
implementation. Use exact snapshots for stable results and explicit assertions or projections for
properties, formats, cardinality, metadata association and numerical tolerances. Preserve the
concrete files even when comparisons use normalized projections. Use small Bash or Python helpers
when required; they must not reproduce the production algorithm.

When the component does not yet exist, use a test-only fixture harness that emits the verified
files and values with the exact channel shape expected from the component. Generate the snapshot
with the same snapshot name and projection used by the final test, verify it against the recorded
checksums, then point the test at the production component without regenerating the snapshot. The
harness is supporting test code and MUST NOT be imported by production code.

Run comparison with `nf-test test <test-path> --ci` and repository options. Missing snapshots,
invalid fixtures and unavailable dependencies are not valid RED. Do not use `--update-snapshot` to
accept output from the implementation under test. Tester owns every required snapshot; no snapshot
may be deferred until after GREEN.

Report the exact command, covered plan items, fixture paths and checksums, snapshot files,
phase-specific RED reason and unresolved environment failures.

## References

- [nf-test snapshots](https://www.nf-test.com/docs/assertions/snapshots/)
- [nf-test comparison mode](https://www.nf-test.com/docs/cli/test/#--ci)
