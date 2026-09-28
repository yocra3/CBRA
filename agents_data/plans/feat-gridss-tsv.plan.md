## Implementation Plan for feat-gridss-tsv

- **Specification**: `agents_data/specs/feat-gridss-tsv.spec.md`
- **Round**: reference
- **Data-model assessment**: Not applicable. The feature creates only per-run files and channel metadata; it introduces no persistent entity, storage schema, or retained annotation cache. `agents_data/ERM.md` is therefore intentionally unchanged.

### Component decisions

| Component | Classification | Evidence and contract |
| --- | --- | --- |
| `gridss/gridss` | import-nf-core | `nf-core modules list remote gridss --json` and `nf-core modules info gridss/gridss` confirmed the component on 2026-09-28. Import exactly `gridss/gridss` from `nf-core/modules` commit `234d5bc9907cd8b272365eabdd6de66fd4ba925c`, using repository nf-core/tools `4.1.0`. It accepts `[meta, BAM/CRAM]`, FASTA, FAI and optional BWA index; emits `[meta, *.vcf.gz]` and GRIDSS versions via topic. Its pinned Apptainer image is `https://depot.galaxyproject.org/singularity/gridss:2.13.2--h270b39a_0`. |
| `annotsv/installannotations` | reuse-local | Existing installed module at `modules/nf-core/annotsv/installannotations/`, module commit `6d46786420b4d7bc88eba026eb389c0c5535d120`. It materializes the automatic directory. |
| `annotsv/annotsv` | reuse-local | Existing installed module at `modules/nf-core/annotsv/annotsv/`, module commit `36e47ba3be943154e9bedba0397045684d77654e`. It consumes the GRIDSS VCF and annotations directory and emits `[meta, *.tsv]`; its unannotated TSV is deliberately not emitted by the new interface. Both AnnotSV modules use the stable-hash image `community.wave.seqera.io/library/annotsv:3.5.3--71a461cb86d570b7` (Apptainer blob URI `https://community-cr-prod.seqera.io/docker/registry/v2/blobs/sha256/36/363f212881f1b2f5c3395a6c7d1270694392e3a6f886e46e091e83527fed9b6b/data`). |
| `gridss-tsv` | new local subworkflow | New independent `subworkflows/local/gridss_tsv/`. It keeps `[meta, bam/cram, bai/crai]` together per sample, passes the BAM/CRAM to GRIDSS, selects a supplied annotation directory or one automatic installation, joins all results by metadata identity, exposes annotated TSV and raw VCF, and exposes an optional VCF-index channel only if the imported caller declares one. The selected GRIDSS module presently declares no index, so the reference fixture expects no index rather than a manufactured index. Software versions are exposed through the nf-core `versions` topic, including GRIDSS and AnnotSV. |

### Step 1: Materialize deterministic reference inputs

Create `agents_data/specs/feat-gridss-tsv.reference/materialize.sh` and `validate.py` and keep generated data untracked under `.reference-data/feat-gridss-tsv/`.

- [ ] Download the four specification-pinned nf-core files into an empty input directory, verify their source commit `c16e7bd8bbc7ed534a3652a608ed0b2098037bdd`, calculate and record SHA-256 checksums, and reject a nonempty target.
- [ ] Assert the selected BAM/BAI and FASTA/FAI compatibility (`testN`, `chr22`, length `40001`) before any caller runs.
- [ ] Record Apptainer version, selected images, pulled-SIF checksums, bind mounts, exact commands, parameters and tool versions in an untracked manifest.
- [ ] Add deterministic negative checks for missing input index and missing FASTA/FAI.

### Step 2: Prove the reference contract with RED, GREEN, and REFACTOR

Implement an independent Bash/Python reference path only after its focused contract test is RED; it must not invoke, copy, or translate the eventual Nextflow components.

- [ ] Tester: add tests for one output per sample, metadata `testN`, parseable GRIDSS VCF and AnnotSV TSV headers, no exposed unannotated TSV, and version records for GRIDSS and AnnotSV; demonstrate RED because the scripts do not yet exist.
- [ ] Coder: execute GRIDSS through `apptainer exec --cleanenv` with read-only inputs and writable outputs; retrieve AnnotSV annotations automatically, then run AnnotSV once using that directory and once as the copied local-annotations scenario.
- [ ] Cleaner: factor only shared validation/manifest logic and rerun Bash syntax checks, Python checks, and both reference scenarios.
- [ ] Record whether GRIDSS generated an index. If it does, validate its sample association; if it does not, record the absent optional output explicitly.

### Step 3: Commit the verified reference round and replan

- [ ] Validate that generated fixtures remain untracked and all versioned scripts are under the specification reference directory.
- [ ] Commit only the reference scripts, tests, this plan, and the `Planned` specification state after GREEN and REFACTOR are evidenced.
- [ ] Update this same plan to **Round: nextflow** with the materialized paths, checksums, successful reference output checksums, and any evidence-driven interface adjustment.

### Step 4: Directly import the approved GRIDSS module

Use the import profile directly; do not hand-copy or edit its files.

- [ ] Run `nf-core modules install gridss/gridss --sha 234d5bc9907cd8b272365eabdd6de66fd4ba925c` from the pipeline root.
- [ ] Validate its provenance in `modules.json`, installed files, and relevant nf-core lint/static checks.
- [ ] Commit the complete validated import before writing local wiring.

### Step 5: Build and test the independent Nextflow subworkflow

Create only the local subworkflow, its `meta.yml`, and nf-test coverage; do not modify `SV_CALLING`, Manta, or their configuration.

- [ ] Tester: using materialized reference artifacts, create an nf-test workflow harness and immutable snapshots/projections for one and multiple sample identities, local versus automatic annotations, raw VCF, optional index behavior, annotated TSV, absence of unannotated TSV, and versions topic; run `nf-test ... --ci` to establish RED.
- [ ] Coder: implement the minimum DSL2 wiring using keyed channel operations, no implicit parent parameters, explicit local/automatic annotation selection, and all public input/output channel documentation.
- [ ] Cleaner: preserve behavior while improving naming and channel comments; rerun the focused nf-test suite and relevant fast checks.
- [ ] Commit each passing local increment separately, without staging `.reference-data/` or `.codex-cluster/jobid`.

### Step 6: Complete validation and lifecycle states

- [ ] Run the full relevant nf-test suite and a standalone independent-subworkflow execution with the verified fixture and the repository-selected executor profile.
- [ ] Confirm every acceptance criterion, multi-sample independence, compatible-reference guard, both annotation source paths, raw VCF, conditional index result, annotated TSV, and GRIDSS/AnnotSV version metadata.
- [ ] Update the specification from `Planned` to `Coded` only after all implementation tests are green, then to `Verified` only after the complete validation is green; include each status change in its corresponding green local commit.
