# Nextflow component testing with nf-test

Use this profile with the applicable nf-core testing conventions. Resolve paths, required plugins
and execution profiles from the repository. The implementation plan declares the round.

## Reference phase

When the plan round is `reference`, test the versioned Bash/Python reference scripts and their
observable output contract. Prefer Bash for orchestration checks and Python for
format, structured-content and numerical validation. Tests must cover declared filenames,
input provenance and checksums, formats, cardinality, metadata associations, semantic properties,
tolerances, failure behavior and reproducibility. A successful command or nonempty file is
insufficient when content is specified.

The test harness may run on the host, but every command that exercises the reference behavior must
run through `apptainer exec --cleanenv` with the exact image and bind mounts pinned by the plan.
Do not fall back to host-installed tools. Record the Apptainer version and resolved image identity
with the test evidence.

Establish RED before the reference implementation exists, then validate the generated files under
the untracked `{Project_Folder}/reference-data/<spec-slug-id>/` workspace. Do not create nf-test
tests or snapshots in this phase.
Missing source data, Apptainer, the pinned image or required tools are environment failures, not
valid RED. Report concrete data paths, checksums and validation evidence to builder for the next
round. For web sources, the committed test command must begin from an empty target and invoke the
versioned materialization path; it must not depend on data left by an earlier local run.

## Nextflow phase

Proceed only when the plan round is `nextflow` and it identifies accessible concrete inputs,
intermediate artifacts and outputs with checksums. Use process tests for new local modules and
workflow tests for local subworkflows or wiring. Create missing tests or extend existing coverage;
preserve unrelated coverage. Stub tests verify declared outputs and wiring but do not replace real
functional tests. Components classified `import-nf-core` are imported and validated directly by
builder; do not create a separate local TDD cycle for the import itself.

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

Report the exact command, covered plan items, fixture paths and checksums, snapshot files, RED reason
and unresolved environment failures.

## References

- [nf-test snapshots](https://www.nf-test.com/docs/assertions/snapshots/)
- [nf-test comparison mode](https://www.nf-test.com/docs/cli/test/#--ci)
