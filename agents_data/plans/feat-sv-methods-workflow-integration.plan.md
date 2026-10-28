## Implementation Plan for feat-sv-methods-workflow-integration

- **Specification**: `agents_data/specs/feat-sv-methods-workflow-integration.spec.md` (ID `feat-sv-methods-workflow-integration`)
- **Pipeline root**: `/beegfs/home/cruizarenas/CBRA`
- **Ownership**: This is the sole plan for this specification. Tester owns test files, fixtures, and snapshot review. Coder owns renames, module stub patches, parameter and selection wiring, configuration, and documentation. Cleaner owns refactoring after GREEN only. No new modules or subworkflows are added. Do not touch the untracked `modules/nf-core/bcftools/stats/`. Do not run Git operations; the builder commits each step.

## Environment and reproducibility

- **Execution environment**: Run every development command on a Slurm compute node, never on `login01`. Check with `hostname -s`. Planning baseline: `nodo05`, Slurm job `583151`. Use this shell prefix for every command in this plan:

  ```bash
  cd /beegfs/home/cruizarenas/CBRA
  source /beegfs/home/cruizarenas/CBRA/.codex-cluster/load-conda-environment.sh
  export NXF_SYNTAX_PARSER=v1
  export NXF_SINGULARITY_CACHEDIR=/beegfs/home/cruizarenas/.nxf-singularity-cache   # persistent, outside the repo; create once
  ```

  - `NXF_SYNTAX_PARSER=v1` is required. `nf-dev` ships Nextflow `26.04.6`. Its strict parser rejects `def check_max(...)` in `nextflow.config` with `Config parsing failed`. Every nf-test run loads `nextflow.config`, so without this variable all tests fail. This was observed during planning.
  - Run every nf-test with `--profile singularity`. `tests/config/nf-test.config` and `nf-test.config` enable no container engine. Stub runs still need containers because `eval` version outputs (Delly, BCFtools, GRIDSS) and `CUSTOM_DUMPSOFTWAREVERSIONS` (no stub block) run real tools. Earlier recorded runs used `-profile singularity`.
  - Use `--ci` for verification runs. `--ci` refuses to create missing snapshots. Create a new or renamed snapshot entry with one run without `--ci` during the GREEN phase, then confirm with `--ci`.
  - Stub tests set `options "-stub"` inside the test file. The GRIDSS subworkflow test is a real functional test. It needs the untracked local AnnotSV directory `agents_data/reference-data` and network access to nf-core test-datasets.
  - nf-test prints warnings about missing `untar` dependencies in unrelated `gatk4` module tests. They are noise.
- **Containers**: No new executable components and no reference commands. All processes use the declared containers of installed modules, unchanged:
  - Manta: `https://community-cr-prod.seqera.io/docker/registry/v2/blobs/sha256/f6/f696c93e6209e33ac0d15f1ecfa799bc67329eec07b0569e065ea8b220b53953/data`
  - Delly: `https://depot.galaxyproject.org/singularity/delly:1.7.3--hd6466ae_0`
  - BCFtools index: `https://community-cr-prod.seqera.io/docker/registry/v2/blobs/sha256/0b/0b4d52ca9a56d07be3f78a12af654e5116f5112908dba277e6796fd9dfb83fe5/data`
  - AnnotSV and AnnotSV install: `https://community-cr-prod.seqera.io/docker/registry/v2/blobs/sha256/36/363f212881f1b2f5c3395a6c7d1270694392e3a6f886e46e091e83527fed9b6b/data`. Runs with `--writable-tmpfs` from the module's `containerOptions`.
  - GRIDSS: `https://depot.galaxyproject.org/singularity/gridss:2.13.2--h270b39a_0`. Observed SIF SHA-256 `c1d9336c481d0a460a8a320b30e8ed217c8315d53f5e553e9fd1f4ad8676c244`.
  - Tabix: `https://depot.galaxyproject.org/singularity/htslib:1.20--h5efdd21_2`
  - BWA index: `https://depot.galaxyproject.org/singularity/bwa:0.7.18--he4a0461_0`
  - Version dumper and MultiQC: `https://depot.galaxyproject.org/singularity/multiqc:1.19--pyhdfd78af_0`
  - Bind mounts come from `singularity.autoMounts = true` in the `singularity` profile.

## Baseline evidence (planning, 2026-10-28, nodo05)

- `nf-test test subworkflows/local/gridss_annotsv/tests/main.nf.test --profile singularity --ci` with `NXF_SYNTAX_PARSER=v1`: **PASSED** (1/1, 74.7 s).
- `nf-test test subworkflows/local/sv_calling_delly/tests/main.nf.test --profile singularity --ci` with `NXF_SYNTAX_PARSER=v1`: **FAILED**, a pre-existing defect: `MissingFileException: Missing output file(s) versions.yml expected by process SV_CALLING_DELLY:ANNOTSV_ANNOTSV`.
  - The local patch `modules/nf-core/annotsv/annotsv/annotsv-annotsv.diff` replaced the topic output with `path "versions.yml"` but did not update the `stub:` block.
  - `modules/nf-core/manta/germline/manta-germline.diff` has the same defect. Its stub emits no `versions.yml`, so every `-stub` run that includes Manta also fails.
  - `modules/nf-core/annotsv/installannotations` has the same gap, but the tests below avoid it by passing `--annotsv_annotations`.
- `--sv_tools` schema check (planning replan, 2026-10-28, nodo05): a throwaway pipeline in the session scratchpad with nf-schema `2.4.2`, `validateParameters()`, and the `sv_tools` schema entry from the parse and validate contract below. Observed:
  - Accepted: `manta`, `' delly , delly '`, `' , '`, and the empty string from a params file (`{"sv_tools": ""}`), `--sv_tools=` or `--sv_tools ' '`.
  - Rejected before the workflow block: `manta,foo`, `foo,bar`, `Manta`, `manta;delly`. Exit status 1, `completed=0`. stdout has `ERROR ~ Validation of pipeline parameters failed!`. stderr and `.nextflow.log` carry the detail line, with the `errorMessage` appended in parentheses.
  - `--sv_tools ''` on the command line becomes boolean `true`. It is rejected with `* --sv_tools (true): Value is [boolean] but should be [string] (<errorMessage>)`. nf-test passes `params {}` through a params file, so `sv_tools = ''` stays a string in tests.

## Reuse analysis

```yaml
functional_requirements:
  - id: select-sv-methods
    operation: Parse --sv_tools (comma-separated, trimmed, de-duplicated) into the set of SV methods to run for a WGS SV run.
    method: null
    inputs: ["params.sv_tools string", "params.svs", "params.ngs_type"]
    outputs: ["selected method set subset of {manta, delly, gridss}"]
  - id: validate-sv-selection
    operation: Before any process starts and in every invocation, fail on unknown names through nextflow_schema.json validation (naming the invalid value and listing accepted values); under --svs true --ngs_type wgs, warn and continue with no SV results on an empty selection.
    method: nf-schema validateParameters
    inputs: ["params.sv_tools", "params.svs", "params.ngs_type"]
    outputs: ["schema validation error exit or warning log line"]
  - id: call-annotate-manta
    operation: Manta germline calling plus AnnotSV per sample (or joint with --manta_joint).
    method: Manta, AnnotSV
    inputs: ["[meta,bam,bai]", "[meta,fasta]", "[meta,fai]", "manta config", "[meta,annotations]", "candidate genes / false-positive SNV / gene transcripts tuples"]
    outputs: ["diploid and candidate SV VCF.gz (+tbi)", "AnnotSV tsv / unannotated tsv / optional vcf", "versions"]
  - id: call-annotate-delly
    operation: Delly calling, TBI indexing, AnnotSV per sample.
    method: Delly, BCFtools index, AnnotSV
    inputs: ["[meta,bam,bai]", "[meta,fasta]", "[meta,fai]", "[meta,annotations]", "optional AnnotSV tuples"]
    outputs: ["VCF.gz + TBI", "AnnotSV outputs", "versions"]
  - id: call-annotate-gridss
    operation: GRIDSS calling with a BWA index, Tabix, AnnotSV per sample.
    method: GRIDSS, Tabix, AnnotSV
    inputs: ["[meta,bam,bai]", "[meta,fasta]", "[meta,fai]", "[meta,bwa_index_dir]", "[meta,annotations]"]
    outputs: ["VCF.gz + TBI", "AnnotSV vcf/tsv/unannotated tsv", "consolidated versions + mqc"]
  - id: provide-bwa-index
    operation: Use --index when supplied, otherwise derive a BWA index from --fasta once per run.
    method: BWA index
    inputs: ["params.index directory or [meta,fasta]"]
    outputs: ["[meta,bwa_index_dir]", "versions"]
  - id: publish-sv-results
    operation: Publish each method's raw calls and AnnotSV results under ${outdir}/SVs/{method}/.
    method: publishDir configuration
    inputs: ["process outputs"]
    outputs: ["SVs/manta/, SVs/delly/, SVs/gridss/"]
  - id: report-versions
    operation: Include versions of selected methods only in collated software versions and MultiQC.
    method: CUSTOM_DUMPSOFTWAREVERSIONS, MULTIQC
    inputs: ["versions files"]
    outputs: ["pipeline_info/software_versions.yml", "MultiQC versions section"]
resolutions:
  - covers: [call-annotate-manta]
    resolution: reuse-local
    path: subworkflows/local/sv_calling (renamed to subworkflows/local/manta_annotsv, contract unchanged)
    evidence:
      - "SV_CALLING composes MANTA_GERMLINE (manta/germline @3485512d, local patch) and ANNOTSV_ANNOTSV (annotsv/annotsv @36e47ba3, local patch); take/emit match the requirement. Stubs of both patched modules lack versions.yml (Step 1)."
  - covers: [call-annotate-delly]
    resolution: reuse-local
    path: subworkflows/local/sv_calling_delly (renamed to subworkflows/local/delly_annotsv, contract unchanged)
    evidence:
      - "Composes DELLY_CALL (delly/call @6d467864), BCFTOOLS_INDEX (bcftools/index @feef3743, ext.args --tbi), ANNOTSV_ANNOTSV; existing stub nf-test covers one sample."
  - covers: [call-annotate-gridss]
    resolution: reuse-local
    path: subworkflows/local/gridss_annotsv
    evidence:
      - "Verified spec feat-gridss-annotsv-wgs-single-sample; take includes ch_bwa_index [meta, dir]; functional nf-test passes at planning baseline. GRIDSS_GRIDSS (gridss/gridss) is tracked but absent from modules.json."
  - covers: [provide-bwa-index]
    resolution: reuse-local
    path: modules/nf-core/bwa/index (BWA_INDEX already included in workflows/snvs.nf)
    evidence:
      - "Emits [meta, bwa/] directory; nf-core gridss/gridss test feeds BWA_INDEX.out.index directly to GRIDSS_GRIDSS. SNVS already builds ch_index from --index or BWA_INDEX for mapping."
  - covers: [publish-sv-results]
    resolution: reuse-local
    path: conf/modules.config
    evidence:
      - "Scoped withName publishDir/ext.* selectors; no component change needed."
  - covers: [report-versions]
    resolution: reuse-local
    path: modules/nf-core/custom/dumpsoftwareversions, modules/nf-core/multiqc
    evidence:
      - "Pipeline-level dump aggregates by module name (process.split(':')[-1]) and asserts identical versions per module name; all three SV paths use the same AnnotSV container, so this holds."
  - covers: [validate-sv-selection]
    resolution: reuse-local
    path: nextflow_schema.json + nf-schema 2.4.2 validateParameters() (main.nf, guarded by params.validate_params, default true)
    evidence:
      - "validateParameters() runs at main.nf top level before the workflow block. A string pattern plus errorMessage rejects unknown names in every run; verified at planning with nf-schema 2.4.2 (see Baseline evidence)."
  - covers: [select-sv-methods, validate-sv-selection]
    resolution: new-required
    evidence:
      - "Splitting, trimming, de-duplication and the empty-selection warning are pipeline-level Groovy logic (local-wiring in lib/ or workflows/snvs.nf), not an executable component; no module or subworkflow is added."
nfcore:
  checked: false
  modules_sha: null
  note: "Every executable requirement is covered by components already installed locally, and the specification forbids adding modules, so no remote nf-core search was needed. Installed SHAs come from modules.json."
```

## Test data and artifacts

| Boundary | Role | Path or materialization command | Format and semantics | Checksum |
| --- | --- | --- | --- | --- |
| Pipeline stub tests (Scenario A) | input samplesheet | `${projectDir}/assets/samplesheet_test.csv` (tracked, existing) | One sample `Sample1`. BAM `test.rna.paired_end.sorted.bam` + `.bai` from nf-core test-datasets `modules`. The FASTQ/VCF columns are present but unused because `--mapping false --variant_calling false --annotation false`. If the tester needs a different BAM-only one-row sheet, it is materialized at test runtime, not committed as data | not applicable (remote, branch-tracked) |
| Pipeline stub tests | FASTA + FAI | `params.modules_testdata_base_path + 'genomics/homo_sapiens/genome/genome.fasta'` and `.fai` | chr22 subset, compatible with the BAM above (same group as the verified GRIDSS fixture) | not applicable |
| Pipeline stub tests | AnnotSV annotations | an existing tracked repository directory passed with `--annotsv_annotations` (stub stand-in; tester picks it) | Stubs never read it. It must exist, so the install module (no stub versions) is not triggered and the tests do not depend on untracked `agents_data/` | not applicable |
| Pipeline stub tests | BWA index (`--index` case) | an existing tracked local directory used as stub stand-in | Proves GRIDSS takes the supplied index and that `BWA_INDEX` does not run. Content is irrelevant under `-stub` | not applicable |
| Pipeline stub tests | derived prerequisite | `BWA_INDEX` stub output (no `--index` case) | `[meta, bwa/]` directory derived from `--fasta` | not applicable |
| `MANTA_ANNOTSV` subworkflow (Scenario B) | BAM + BAI, FASTA + FAI | Same as the Delly test: `genomics/homo_sapiens/illumina/bam/test2.paired_end.recalibrated.sorted.bam(.bai)`, `genomics/homo_sapiens/genome/chr21/sequence/genome.fasta(.fai)` under `params.modules_testdata_base_path` | One sample `[id:'test']`, stub. The Manta config input is the tracked `assets/configManta.ini` or an empty optional value. Annotations `[[id:'annotations'], []]` and empty optional AnnotSV tuples, as in the Delly test | not applicable |
| `DELLY_ANNOTSV` subworkflow | existing fixture | unchanged inputs of `sv_calling_delly/tests/main.nf.test` | Reused under the new name | not applicable |
| `GRIDSS_ANNOTSV` subworkflow | existing fixture | unchanged; pinned test-datasets commit `c16e7bd8bbc7ed534a3652a608ed0b2098037bdd` plus local `agents_data/reference-data` | Real functional test, unchanged | snapshots unchanged |
| Outputs | output | `${outdir}/SVs/manta/`, `${outdir}/SVs/delly/`, `${outdir}/SVs/gridss/` | Raw calls (VCF.gz plus index) and AnnotSV results per sample, one directory per method; no cross-method overwrite | not applicable |

No reference data generation is needed. There are no new executable components, and the stub and contract assertions are deterministic.

## Component design

| Component | Classification | Contract and evidence | Source |
| --- | --- | --- | --- |
| `ANNOTSV_ANNOTSV` | reuse-local | Unchanged interface. Its local patch's `stub:` must also emit `versions.yml` so stub runs succeed (Step 1). The production `script:` stays the same | `modules/nf-core/annotsv/annotsv` (nf-core `annotsv/annotsv` @`36e47ba3be943154e9bedba0397045684d77654e` + `annotsv-annotsv.diff`) |
| `MANTA_GERMLINE` | reuse-local | Unchanged interface. Its local patch's `stub:` must emit `versions.yml` (Step 1) | `modules/nf-core/manta/germline` (@`3485512d3930df1fcb66b5f92af639179bdfe4be` + `manta-germline.diff`) |
| `DELLY_CALL`, `BCFTOOLS_INDEX`, `GRIDSS_GRIDSS`, `TABIX_TABIX`, `BWA_INDEX`, `CUSTOM_DUMPSOFTWAREVERSIONS`, `MULTIQC`, `ANNOTSV_INSTALLANNOTATIONS` | reuse-local | Consumed unchanged | `modules/nf-core/...` |
| `MANTA_ANNOTSV` | local-wiring (rename) | `subworkflows/local/manta_annotsv/`. Same take/emit as current `SV_CALLING`: take `ch_bam, ch_fasta, ch_fai, ch_manta_config, ch_annotsv_annotations, ch_candidate_genes, ch_false_positive_snv, ch_gene_transcripts`; emit `annotated_tsv, annotated_vcf, unannotated_tsv, diploid_sv_vcf, candidate_sv_vcf, versions`. New stub nf-test | from `subworkflows/local/sv_calling` |
| `DELLY_ANNOTSV` | local-wiring (rename) | `subworkflows/local/delly_annotsv/`. Same take/emit as current `SV_CALLING_DELLY`. Tests, snapshot, and manual helper move with it | from `subworkflows/local/sv_calling_delly` |
| `GRIDSS_ANNOTSV` | reuse-local | Unchanged take `ch_bam, ch_fasta, ch_fai, ch_bwa_index, ch_annotsv_annotations`; emit `gridss_vcf, gridss_tbi, annotsv_vcf, annotsv_tsv, annotsv_unannotated_tsv, versions (software_versions.yml), versions_mqc` | `subworkflows/local/gridss_annotsv` |
| `--sv_tools` parse and validate | local-wiring | Declared in `nextflow.config` (default `'manta,delly,gridss'`) and in `nextflow_schema.json` under `svs_options`: type string, default, description listing `manta`, `delly`, `gridss` and the default, plus the exact `pattern` and `errorMessage` from the contract below. Unknown names are rejected by schema validation. Groovy only parses the value and warns on an empty selection | `nextflow.config`, `nextflow_schema.json`, `lib/WorkflowSnvs.groovy` and/or `workflows/snvs.nf` |
| SNVS SV selection wiring | local-wiring | In the existing `params.svs && ngs_type == 'wgs'` branch, invoke exactly the selected subworkflows with the shared `ch_bam_svs`, `ch_fasta`, `ch_fai`, `annotations` and optional AnnotSV channels. GRIDSS keeps its own input set (no optional AnnotSV channels, plus a BWA index). WES branch unchanged | `workflows/snvs.nf` |
| BWA index provisioning | local-wiring | One `ch_index` per run: from `--index` (`[ [id:baseName], dir ]`) or from a single `BWA_INDEX(ch_fasta)` call. Built when `--mapping` is true or GRIDSS is selected in a WGS SV run. `BWA_INDEX` must not be invoked twice. Its versions are collected once | `workflows/snvs.nf` |
| Publishing and SV configuration | local-wiring | `conf/modules.config` selectors renamed to `MANTA_ANNOTSV`/`DELLY_ANNOTSV` and GRIDSS selectors added. See the publishing and versions contract below | `conf/modules.config` |

### Cross-phase contracts

- **`--sv_tools` parse and validate**:
  - **Schema validation (every invocation).** The existing `validateParameters()` call in `main.nf` (nf-schema `2.4.2`) runs before any process starts, whatever `--svs` and `--ngs_type` are. The `sv_tools` property in `nextflow_schema.json` must contain exactly these two keys and values as JSON text:

    ```json
    "pattern": "^\\s*(manta|delly|gridss)?\\s*(,\\s*(manta|delly|gridss)?\\s*)*$",
    "errorMessage": "Invalid SV tool name. Accepted values: manta, delly, gridss (comma-separated)."
    ```

    - The decoded regex is `^\s*(manta|delly|gridss)?\s*(,\s*(manta|delly|gridss)?\s*)*$`. It accepts only `manta`, `delly`, and `gridss` (case-sensitive), separated by commas, with optional whitespace around each name. It also accepts the empty value and empty items such as `' , '`.
    - The schema keeps `"type": "string"` and `"default": "manta,delly,gridss"`.
  - **Expected unknown-name error text.** This is nf-schema's fixed format with the `errorMessage` appended. For `sv_tools = 'manta,foo'`, stderr and `.nextflow.log` contain this line:

    ```text
    * --sv_tools (manta,foo): "manta,foo" does not match regular expression [^\s*(manta|delly|gridss)?\s*(,\s*(manta|delly|gridss)?\s*)*$] (Invalid SV tool name. Accepted values: manta, delly, gridss (comma-separated).)
    ```

    - It comes after `The following invalid input values have been detected:`. stdout carries `ERROR ~ Validation of pipeline parameters failed!`.
    - Tests assert two substrings so they do not depend on the regex text: `* --sv_tools (manta,foo): "manta,foo" does not match regular expression` and `(Invalid SV tool name. Accepted values: manta, delly, gridss (comma-separated).)`.
    - nf-schema prints the whole offending value, so the invalid name `foo` appears inside it.
  - **Groovy parsing (WGS SV runs only).** Split on `,`, trim each name, drop empty items, de-duplicate. No Groovy unknown-name error is required: with schema validation on, unknown names never reach the workflow. With `--validate_params false`, the user has disabled validation, and an unknown name matches no method, so it runs nothing. No defensive check is planned.
  - An empty selection while `--svs true --ngs_type wgs` logs one `log.warn` and the run continues with no SV process. This single text satisfies both spec wordings:
    `No SV tools have been selected (--sv_tools is empty): at least one SV tool is required (accepted values: manta, delly, gridss), so no SV results will be returned.`
  - `--svs false` and `--ngs_type wes` run no `{METHOD}_ANNOTSV` process for any valid `--sv_tools` value, and no warning is logged.
- **Publishing**:
  - Manta raw calls (`*.vcf.gz`, `*.vcf.gz.tbi`) and Manta AnnotSV outputs go to `${params.outdir}/SVs/manta/`.
  - Delly `*.delly.vcf.gz`, its TBI, and Delly AnnotSV outputs go to `${params.outdir}/SVs/delly/`.
  - GRIDSS VCF.gz, TBI, and GRIDSS AnnotSV outputs go to `${params.outdir}/SVs/gridss/`.
  - Existing per-method `ext.args`/`ext.prefix` are kept. GRIDSS in the pipeline needs `-p vcf` for its Tabix and AnnotSV arguments in line with the other methods.
  - `.*CNVS_CALLING:*` selectors stay unchanged.
  - The old locations `manta/`, `delly/`, `svs/annotsv_annotation`, and `svs/delly_annotsv_annotation` are replaced.
- **Versions**:
  - Every selected method's versions reach the pipeline's single `CUSTOM_DUMPSOFTWAREVERSIONS` input: caller, indexing (BCFtools/Tabix, and BWA when derived), and AnnotSV. Unselected methods contribute none.
  - `GRIDSS_ANNOTSV.out.versions` is a consolidated `software_versions.yml`. It is valid YAML keyed by process name and may be mixed into `ch_versions`.
  - `GRIDSS_ANNOTSV.out.versions_mqc` must not be fed to MultiQC, because its section id would duplicate `software_versions`.
  - The bare `withName: CUSTOM_DUMPSOFTWAREVERSIONS` selector also matches `GRIDSS_ANNOTSV:CUSTOM_DUMPSOFTWAREVERSIONS`. The GRIDSS-internal dump must therefore not publish into `pipeline_info/`, where it would overwrite the pipeline-level `software_versions.yml`/`software_versions_mqc.yml`.

## Acceptance criteria coverage

| Acceptance criterion | Plan increment | Verification |
| --- | --- | --- |
| AC1 `--sv_tools` in `nextflow.config` and `nextflow_schema.json`, accepted values and default `manta,delly,gridss` | 3, 4 | Schema/config entries reviewed. Pipeline stub test without `--sv_tools` runs Manta, Delly and GRIDSS tasks (Step 4). `validateParameters()` accepts the parameter in every pipeline test |
| AC2 Run each SV subworkflow only when listed; no process of an unlisted method | 3, 4 | Pipeline stub tests for single selections (`manta`, `delly`, `gridss`, and whitespace/duplicate form): the trace contains only processes of the selected subworkflow(s), and only that method's `SVs/{method}/` directory exists |
| AC3 Several methods run once per sample and publish to distinct method locations | 4 | Multiple-selection and default stub tests: one caller task per method for the single sample; `SVs/manta/`, `SVs/delly/`, `SVs/gridss/` each hold that method's raw and AnnotSV files only |
| AC4 Unknown name stops before any process, whatever `--svs`/`--ngs_type`, with a `nextflow_schema.json` validation error naming the value and listing accepted values | 3 | Three pipeline stub tests with an unknown name: `--svs true --ngs_type wgs`, `--svs false`, and `--ngs_type wes`. Each run fails, stderr contains both expected-error substrings from the contract, and the trace has zero tasks. Schema review: the `pattern`/`errorMessage` match the contract |
| AC5 Empty selection: warning that at least one SV tool is required; run continues with no SV results | 3 | Pipeline stub tests with `--sv_tools ''` (and separators only, e.g. `' , '`): success, the warning text appears in the output, no SV process runs, no `SVs/` directory exists |
| AC6 GRIDSS uses `--index` or a BWA index derived from `--fasta` | 4 | GRIDSS stub tests with and without `--index`: `BWA_INDEX` runs exactly once without `--index` and never with it, and the GRIDSS task runs in both cases |
| AC7 WES runs the CNV path unchanged and ignores the selection of a valid `--sv_tools` | 3, 4, 5 | Diff review: the `ngs_type == 'wes'` branch and `.*CNVS_CALLING:*` selectors are unchanged, and Groovy selection and the empty-selection warning apply only to WGS SV runs. Under WES, only schema validation of unknown names applies (Step 3 `--ngs_type wes` unknown-name test) |
| AC8 Names `{method}_annotsv`/`{METHOD}_ANNOTSV`; no `sv_calling`/`SV_CALLING`/`sv_calling_delly`/`SV_CALLING_DELLY` reference | 2, 5 | `rg -n -i 'sv_calling' --glob '!agents_data/**' --glob '!.nf-test*' --glob '!.git/**' /beegfs/home/cruizarenas/CBRA` returns nothing. Renamed tests pass |
| AC9 Passing nf-test coverage: three subworkflow tests plus pipeline stub tests (single, multiple, default, unknown) | 1, 2, 3, 4, 5 | All four nf-test commands in Step 5 pass with `--ci` |

### Step 1: Make patched AnnotSV and Manta stubs emit version evidence
Restore stub runnability so that existing and planned stub tests can pass. Production `script:` blocks and the module interfaces stay unchanged.

- **Depends on:** none
- **Execution:** `coder: direct module-patch`. No preceding tester phase: the RED evidence is the existing Delly stub test, which fails with `Missing output file(s) versions.yml ... ANNOTSV_ANNOTSV` (planning baseline).
- **Approval (recorded 2026-10-28):** the user approved this step as planned, relayed by the coordinator. The approved scope is to add `versions.yml` creation to the `stub:` blocks of `annotsv/annotsv` and `manta/germline` only, and to regenerate both patches with `nf-core modules patch`. Real `script:` blocks stay unchanged. No other module changes.
- **RED (already recorded):** `nf-test test subworkflows/local/sv_calling_delly/tests/main.nf.test --profile singularity --ci` fails on `versions.yml`.
- **GREEN:** the same command passes, or fails only on a snapshot mismatch limited to version-file md5 values. In that case, run once without `--ci` and rerun with `--ci`. The test is renamed in Step 2, so snapshot refresh may also be deferred to Step 2.

- [x] Update the `stub:` blocks of `modules/nf-core/annotsv/annotsv/main.nf` and `modules/nf-core/manta/germline/main.nf` so each writes a `versions.yml` with the same `"${task.process}": tool: version` shape as its script.
- [x] Regenerate both local patch files with `nf-core modules patch annotsv/annotsv` and `nf-core modules patch manta/germline` from the pipeline root. Confirm `modules.json` still points at the patch files.
- [x] Run the Delly stub test to the GREEN state above and record the result. (2026-10-28, nodo05: AnnotSV versions md5 refreshed once; `--ci` rerun `SUCCESS: Executed 1 tests`; GRIDSS test also PASSED.)

### Step 2: Rename SV subworkflows to `{method}_annotsv` and add the Manta subworkflow test
Mechanical rename with preserved contracts, plus the missing `MANTA_ANNOTSV` stub test. The Delly and GRIDSS tests must stay green.

- **Depends on:** 1
- **Execution:** `tester: production-test` -> `coder: production-implementation` -> `cleaner: production-refactor`
- **tester (RED):**
  - Create `subworkflows/local/manta_annotsv/tests/main.nf.test` (stub, one sample, see Test data) and `tests/nextflow.config` with scoped `MANTA_ANNOTSV:*` `ext.args`, mirroring the Delly test. Workflow `MANTA_ANNOTSV`, tags `subworkflows`, `subworkflows/manta_annotsv`, `manta`, `manta/germline`, `annotsv`, `annotsv/annotsv`.
  - Assert success, every emitted channel's metadata/file shape, and a stub snapshot.
  - Move the Delly tests directory, including `manual/`, to `subworkflows/local/delly_annotsv/tests/`. Change every name, tag, and selector in it to `DELLY_ANNOTSV`/`delly_annotsv`.
  - Expected RED: both tests fail because `../main.nf` / workflow `MANTA_ANNOTSV` / `DELLY_ANNOTSV` do not exist. Command: `nf-test test subworkflows/local/manta_annotsv/tests/main.nf.test subworkflows/local/delly_annotsv/tests/main.nf.test --profile singularity --ci`.
- **coder (GREEN):**
  - Move `sv_calling/{main.nf,meta.yml}` to `manta_annotsv/` and `sv_calling_delly/{main.nf,meta.yml}` to `delly_annotsv/`, renaming the workflows to `MANTA_ANNOTSV`/`DELLY_ANNOTSV`. Leave no old directory.
  - Update `meta.yml` names, the `include`s and calls in `workflows/snvs.nf`, and the `conf/modules.config` selectors (`.*SV_CALLING:...` -> `.*MANTA_ANNOTSV:...`, `.*SV_CALLING_DELLY:...` -> `.*DELLY_ANNOTSV:...`).
  - Keep behavior and output paths unchanged in this step.
  - Create the new snapshot entries with one run without `--ci`. Remove the obsolete `sv_calling_delly ...` snapshot key. Delly snapshot changes must be limited to the test name and version-file md5 values that come from process names. Then verify:
    - `nf-test test subworkflows/local/manta_annotsv/tests/main.nf.test --profile singularity --ci` passes
    - `nf-test test subworkflows/local/delly_annotsv/tests/main.nf.test --profile singularity --ci` passes
    - `nf-test test subworkflows/local/gridss_annotsv/tests/main.nf.test --profile singularity --ci` passes with unchanged snapshots
- **cleaner:** Remove only rename leftovers, such as stale comments or descriptions. Rerun the three commands above with `--ci`; all must pass.

- [x] Tester: add the `MANTA_ANNOTSV` stub test and config, move and rename the Delly tests and manual helper, and record RED.
- [x] Coder: rename both subworkflow directories, workflow names, `meta.yml`, the `workflows/snvs.nf` includes and calls, and the `conf/modules.config` selectors, with contracts unchanged.
- [x] Coder: create and review the snapshots, then bring the Manta, Delly, and GRIDSS subworkflow tests to GREEN with `--ci`.
- [x] Confirm the AC8 `rg` scan finds no matches outside `agents_data/`.
- [x] Cleaner: refactor after GREEN and rerun the three subworkflow tests. (2026-10-28, nodo05: no cleanup needed; `--ci` run of Manta, Delly and GRIDSS tests `SUCCESS: Executed 3 tests`; AC8 scan empty.)

### Step 3: Add `--sv_tools` with validation and selection of Manta and Delly
Declare the parameter, validate it before any process starts, and gate the existing Manta and Delly calls on the selection. GRIDSS is integrated in Step 4. Until then `gridss` is an accepted name that runs nothing.

- **Depends on:** 2
- **Execution:** `tester: production-test` -> `coder: production-implementation` -> `cleaner: production-refactor`
- **tester (RED):**
  - Create the pipeline-level stub test file `tests/sv_tools.nf.test` (`nextflow_pipeline`, `script "../main.nf"`, `options "-stub"`, tag `pipeline`, tag `sv_tools`).
  - Common params: `outdir = "$outputDir"`, the samplesheet/FASTA/FAI/annotations from Test data, `ngs_type = 'wgs'`, `svs = true`, `mapping = false`, `variant_calling = false`, `annotation = false`.
  - Cases:
    - `sv_tools = 'manta'`: only `MANTA_ANNOTSV` processes run, and `SVs/manta/` exists.
    - `sv_tools = ' delly , delly '`: whitespace and duplicate handling; `DELLY_ANNOTSV` processes run once for the sample, and none from Manta or GRIDSS.
    - Unknown name, `sv_tools = 'manta,foo'` (common params): the run fails, stderr contains both expected-error substrings from the parse and validate contract, and the trace has zero tasks (empty or absent trace).
    - Unknown name with `svs = false, sv_tools = 'manta,foo'`: the same failure, error substrings, and zero tasks.
    - Unknown name with `ngs_type = 'wes', sv_tools = 'manta,foo'`: the same failure, error substrings, and zero tasks. Keep the other params schema-valid so the asserted error is the `sv_tools` one.
    - `sv_tools = ''` and `sv_tools = ' , '`: success, the warning text from the contract appears, no SV process runs.
    - `svs = false, sv_tools = 'manta'`: no SV process runs.
  - Process-name and trace assertions only; no md5 snapshots of stub files are required.
  - Expected RED, all from the stub run:
    - The selection cases fail because Manta and Delly always run.
    - The empty cases fail because the warning is missing.
    - The three unknown-name cases fail because `sv_tools` is not in the schema: `validationFailUnrecognisedParams = false` only warns, so the expected-error substrings are absent. In the WGS case, tasks also start.
    - Record the failing assertion for each unknown-name case. A run failing for an unrelated reason is not valid RED evidence.
  - Command: `nf-test test tests/sv_tools.nf.test --profile singularity --ci`.
- **coder (GREEN):**
  - Add `sv_tools = 'manta,delly,gridss'` to `nextflow.config`.
  - Add the `nextflow_schema.json` property under `svs_options`: type string, the default, a description listing `manta`, `delly`, `gridss` and the default, and the exact `pattern` and `errorMessage` from the contract.
  - Implement the Groovy parsing and the empty-selection warning, and gate `MANTA_ANNOTSV`/`DELLY_ANNOTSV` on the selection. Version collection applies only to invoked subworkflows. Leave the WES branch unchanged.
  - Verify:
    - `nf-test test tests/sv_tools.nf.test --profile singularity --ci` passes. This stub run is the GREEN evidence for all three unknown-name cases.
    - `python3 -m json.tool nextflow_schema.json` succeeds
    - `nf-test test subworkflows/local/manta_annotsv/tests/main.nf.test subworkflows/local/delly_annotsv/tests/main.nf.test --profile singularity --ci` passes
- **cleaner:** Simplify the parsing and selection code while keeping the contract. Rerun both commands above.

- [x] Tester: write the pipeline-level stub tests for single selection, whitespace and duplicates, unknown name (WGS SV, `--svs false`, `--ngs_type wes`), empty selection, and `--svs false`, and record RED from the stub run.
- [x] Coder: declare `--sv_tools` in `nextflow.config`, and in `nextflow_schema.json` with the exact `pattern` and `errorMessage`.
- [x] Coder: implement parsing and the empty-selection warning contract, and gate Manta and Delly on the selection. Leave WES unchanged.
- [x] Coder: bring the pipeline and the Manta and Delly subworkflow tests to GREEN with `--ci`.
- [x] Cleaner: refactor after GREEN and rerun the tests. (2026-10-28, nodo05: RED 7/8 failed for missing behavior; GREEN `--ci` `SUCCESS: Executed 10 tests` across sv_tools, Manta and Delly tests. `SVs/manta/` assertion deferred to Step 4 with publishing.)

### Step 4: Integrate GRIDSS with the BWA index, method-specific publishing, and version reporting
Wire `GRIDSS_ANNOTSV` into the WGS SV branch. Provide the BWA index from `--index` or `--fasta`. Publish all three methods under `SVs/{method}/`, and report versions for the selected methods only.

- **Depends on:** 3
- **Execution:** `tester: production-test` -> `coder: production-implementation` -> `cleaner: production-refactor`
- **tester (RED):** Extend `tests/sv_tools.nf.test` with these cases:
  - `sv_tools = 'gridss'` without `--index`: `BWA_INDEX` runs once, `GRIDSS_ANNOTSV` processes run, no Manta or Delly process runs, and `SVs/gridss/` holds the GRIDSS VCF.gz, TBI and AnnotSV TSV.
  - `sv_tools = 'gridss'` with `index` = the stand-in directory: no `BWA_INDEX` task, GRIDSS runs.
  - `sv_tools = 'manta,gridss'` (multiple selection): exactly the processes of those two methods run.
  - The default, with no `sv_tools` param: all three run once for the sample.
  - For the multiple and default cases, assert that each `SVs/{method}/` contains only its own method's raw and AnnotSV files, and that no SV file is published outside `SVs/`. Assert that `pipeline_info/software_versions.yml` lists the selected methods' callers (e.g. `gridss`, `delly`, `manta`) plus `annotsv`, and omits the unselected ones. Assert that the GRIDSS-internal dump does not overwrite it.
  - Update the Step 3 `manta`/`delly` cases to expect `SVs/{method}/` paths.
  - Expected RED: GRIDSS never runs, and the outputs are still in the old locations.
  - Command: `nf-test test tests/sv_tools.nf.test --profile singularity --ci`.
- **coder (GREEN):**
  - Implement the BWA index provisioning contract, so `BWA_INDEX` is called at most once.
  - Invoke `GRIDSS_ANNOTSV` when selected, with `ch_bam_svs`, `ch_fasta`, `ch_fai`, `ch_index`, `annotations`.
  - Mix the selected methods' versions into `ch_versions` according to the versions contract.
  - Update `conf/modules.config` for SV publishing and the GRIDSS selectors, following the publishing contract.
  - Verify every command below:
    - `nf-test test tests/sv_tools.nf.test --profile singularity --ci`
    - `nf-test test subworkflows/local/manta_annotsv/tests/main.nf.test --profile singularity --ci`
    - `nf-test test subworkflows/local/delly_annotsv/tests/main.nf.test --profile singularity --ci`
    - `nf-test test subworkflows/local/gridss_annotsv/tests/main.nf.test --profile singularity --ci`. The subworkflow tests also load `conf/modules.config`, so GRIDSS snapshots must stay unchanged. Explain any snapshot change before accepting it.
- **cleaner:** Remove duplication in the SV branch, such as shared channel preparation, while keeping the contracts. Rerun all four commands.

- [x] Tester: add the GRIDSS, `--index`, multiple, default, publishing, and versions cases, and record RED.
- [x] Coder: provide the BWA index once from `--index` or `--fasta`, and invoke `GRIDSS_ANNOTSV` when selected.
- [x] Coder: publish Manta, Delly and GRIDSS raw and AnnotSV outputs under `SVs/{method}/`, and keep the GRIDSS-internal version dump out of `pipeline_info/`.
- [x] Coder: bring the pipeline and all three subworkflow tests to GREEN with `--ci`.
- [x] Cleaner: refactor after GREEN and rerun all four tests. (2026-10-28, nodo05: RED 6/12 failed for missing behavior; GREEN `--ci` `SUCCESS: Executed 15 tests` across sv_tools and the three subworkflow tests; no snapshot changes. GRIDSS-internal dump publishing disabled by a fully qualified selector, verified by review from run output. No BWA_INDEX `ext.prefix` added; see Step 5 docs.)

### Step 5: Documentation and final verification
Describe `--sv_tools`, the three methods, and their output locations, then run the full verification set.

- **Depends on:** 4
- **Execution:** `coder: direct documentation`. This is a docs-only phase; no RED is required.
- **Verification:** all commands below:
  - `nf-test test subworkflows/local/manta_annotsv/tests/main.nf.test subworkflows/local/delly_annotsv/tests/main.nf.test subworkflows/local/gridss_annotsv/tests/main.nf.test tests/sv_tools.nf.test --profile singularity --ci` passes
  - The AC8 `rg` scan finds no matches
  - `python3 -m json.tool nextflow_schema.json` succeeds

- [x] Update `docs/usage.md` (the SV paragraph under "Pipeline steps"): `--sv_tools` syntax, accepted values, the default, schema rejection of unknown names in every run, empty-selection and `--svs false` behavior (an empty value is passed as `--sv_tools=`, `--sv_tools ' '`, or `sv_tools: ''` in a params file, not as `--sv_tools ''`), the fact that WES ignores a valid selection, and GRIDSS with `--index` or a derived index.
- [x] Update `README.md` (SV analysis bullets): replace "all available SV callers are run together" with selectable Manta, Delly and GRIDSS, and note that AnnotSV annotates every selected method.
- [x] Add an SVs section to `docs/output.md` with `SVs/manta/`, `SVs/delly/`, `SVs/gridss/` and their raw and AnnotSV files.
- [x] Add a `CHANGELOG.md` entry under `v1.0dev` `Added` (the `--sv_tools` selection and GRIDSS integration) and a rename note (`sv_calling` -> `manta_annotsv`, `sv_calling_delly` -> `delly_annotsv`, new output paths).
- [x] Run the final verification set above and record the results. (2026-10-28, nodo05: `--ci` run of the four nf-test files `SUCCESS: Executed 15 tests`; AC8 scan empty; schema JSON valid. Docs record that GRIDSS uses a BWA index only when named after the FASTA file name, otherwise builds its own.)

## Risks and spec notes (not resolved by changing the spec)

- **Warning wording:** the single warning text in the contract contains both "No SV tools have been selected ... no SV results will be returned" (Model section) and "at least one SV tool is required" (AC5).
- **Output relocation:** the existing `manta/`, `delly/`, `svs/annotsv_annotation/`, and `svs/delly_annotsv_annotation/` move to `SVs/{method}/`. Note the capital `SVs`, as the spec requires. Users of the old paths are affected, so the CHANGELOG must say so.
- **GRIDSS index naming:** `BWA_INDEX` writes `bwa/<fasta.baseName>.*`. GRIDSS looks for an index next to the reference (`<fasta name>.*`) and rebuilds it itself when that is missing. The spec contract (the index is passed to GRIDSS) is met, but a derived index may not actually be used. A scoped `BWA_INDEX` `ext.prefix` set to the FASTA file name stays compatible with `BWA_MEM`, which finds the index by `*.amb`. This is optional and outside the stub-testable contract. Record whatever is chosen.
- **Version dumper:** the pipeline-level dump aggregates by module name and fails if two same-named modules report different versions. All AnnotSV and Tabix uses share one container, so this holds today. Do not feed the GRIDSS `versions_mqc` to MultiQC.
- **Pre-existing, out of scope:** `ch_manta_config` is `Channel.empty()` when `--manta_config` is unset, which silently skips Manta; the default is a URL. `gridss/gridss` is tracked but missing from `modules.json`. `annotsv/installannotations` has no `versions.yml` in its stub. Report these; do not fix them here.
- `--sv_tools` passed without a value, or as `--sv_tools ''` on the command line, becomes boolean `true` in Nextflow. The string schema rejects it with `Value is [boolean] but should be [string]` plus the `errorMessage` (observed at planning). This is why the docs must give working empty forms. No test is required.
- `--validate_params false` skips schema validation, so unknown names are then not rejected. They match no method and run nothing. This is accepted user opt-out, not a defect.

## Blockers

- None. The Step 1 stub-only patch of `annotsv/annotsv` and `manta/germline` (add `versions.yml` to the stubs, regenerate the patches with `nf-core modules patch`, real scripts unchanged) was approved by the user on 2026-10-28, relayed by the coordinator. It is no longer a blocker.
- Not a blocker: the GRIDSS subworkflow test depends on the untracked local `agents_data/reference-data`, which exists on this cluster.
