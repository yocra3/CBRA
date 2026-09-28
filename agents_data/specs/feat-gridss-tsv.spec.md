# GRIDSS TSV subworkflow Specification
- **ID**: feat-gridss-tsv
- **Type**: feat
- **Status**: Draft

Allowed status flow: Draft -> Approved -> Planned -> Coded -> Verified -> Released. A requested
revision of the same work reopens this file at Draft.

## Problem Description

CBRA has no independent subworkflow to call structural variants with GRIDSS and annotate each
sample's calls with AnnotSV. Users need this result without changing the existing Manta-based
`SV_CALLING` workflow.

### User Stories

- As a rare-disease analyst, I want to run GRIDSS and AnnotSV for each aligned sample independently so that I receive sample-specific structural-variant annotations.
- As a pipeline user, I want to provide local AnnotSV annotations or have them obtained automatically so that annotation can run in connected and controlled local environments.
- As a pipeline maintainer, I want the subworkflow to report the GRIDSS and AnnotSV versions so that results are traceable.

## Solution Overview

### User/App interface

- Provide an independent Nextflow subworkflow named `gridss-tsv`.
- Accept one or more sample-associated aligned BAM or CRAM files with their indexes, plus a
  reference FASTA and its FAI index. The reference is required and must be compatible with the
  aligned sample.
- Accept an optional local AnnotSV annotations directory. When it is not supplied, obtain the
  AnnotSV annotations automatically.
- Return, for every processed sample, an AnnotSV-annotated TSV and the raw GRIDSS structural
  variant VCF. Return the VCF index when GRIDSS generates one.
- Return software-version metadata covering GRIDSS and AnnotSV.

### Model and logic

- Process each sample independently; samples in the same invocation do not share structural
  variant calling or annotation results.
- Use the sample identity carried by the aligned-input metadata to associate every required output
  with its originating sample.
- Use the GRIDSS structural-variant VCF as the input to AnnotSV.
- Treat the local AnnotSV annotations directory as the selected annotation source when supplied;
  otherwise use the automatically obtained annotations.
- Do not expose AnnotSV's unannotated intermediate TSV as a `gridss-tsv` output.

### Persistence

- Produce per-sample result files and version metadata through the subworkflow outputs.
- No persistent database or retained downloaded-annotation cache is required by this work item.

## Boundaries

- This work creates the independent `gridss-tsv` interface only.
- `SV_CALLING`, its Manta behavior, Manta configuration, and existing Manta outputs are out of
  scope and must not be modified.
- Joint or cohort-level GRIDSS calling, additional GRIDSS reference bundles, and exposure of the
  AnnotSV unannotated TSV are out of scope.

## Inputs and Outputs

| Direction | Item | Required | Functional contract |
| --- | --- | --- | --- |
| Input | Sample-aligned reads | Yes | BAM or CRAM and its corresponding index, associated with a sample identifier. |
| Input | Reference genome | Yes | FASTA and FAI index compatible with each sample's aligned reads. |
| Input | AnnotSV annotations | No | A local annotations directory. If absent, annotations are obtained automatically. |
| Output | Annotated structural variants | Yes | One AnnotSV-annotated TSV per processed sample, associated with that sample identifier. |
| Output | Raw structural-variant calls | Yes | One GRIDSS VCF per processed sample, associated with that sample identifier. |
| Output | GRIDSS VCF index | Conditional | The index associated with the raw GRIDSS VCF when GRIDSS generates one. |
| Output | Software versions | Yes | Version metadata containing GRIDSS and AnnotSV versions. |

## User-Confirmed Decisions

- Required outputs are the AnnotSV-annotated TSV, the raw GRIDSS structural-variant VCF, and its
  index when generated.
- The unannotated AnnotSV TSV is not exposed.
- The required reference is the pipeline or sample FASTA with its FAI index; no GRIDSS-specific
  reference bundle is required.

## Test Data

- **Status**: reference-required
- **Search result**: The full `nf-core/test-datasets` `modules` tree was searched at commit
  `c16e7bd8bbc7ed534a3652a608ed0b2098037bdd`, followed by every file in Zenodo record
  [19064653](https://doi.org/10.5281/zenodo.19064653). One nf-core BAM/FASTA compatibility group
  is reusable for the smallest execution. AnnotSV resources and an optional biological oracle
  remain unavailable, so the overall status remains `reference-required`.

### Existing reusable fixture

The following concrete nf-core files form one verified compatibility group. They are pinned to the
commit above; the repository does not publish SHA-256 checksums for them.

| Role | Concrete file |
| --- | --- |
| Aligned reads | [test.paired_end.sorted.bam](https://raw.githubusercontent.com/nf-core/test-datasets/c16e7bd8bbc7ed534a3652a608ed0b2098037bdd/data/genomics/homo_sapiens/illumina/bam/test.paired_end.sorted.bam) |
| Alignment index | [test.paired_end.sorted.bam.bai](https://raw.githubusercontent.com/nf-core/test-datasets/c16e7bd8bbc7ed534a3652a608ed0b2098037bdd/data/genomics/homo_sapiens/illumina/bam/test.paired_end.sorted.bam.bai) |
| Reference FASTA | [genome.fasta](https://raw.githubusercontent.com/nf-core/test-datasets/c16e7bd8bbc7ed534a3652a608ed0b2098037bdd/data/genomics/homo_sapiens/genome/genome.fasta) |
| Reference index | [genome.fasta.fai](https://raw.githubusercontent.com/nf-core/test-datasets/c16e7bd8bbc7ed534a3652a608ed0b2098037bdd/data/genomics/homo_sapiens/genome/genome.fasta.fai) |

- The BAM is coordinate sorted, its read group identifies sample `testN`, and both its header and
  the FAI declare `chr22` with length `40001`. This proves the compatibility relationship needed
  by the minimal BAM/BAI and FASTA/FAI input scenario.
- This is a single-sample, chr22-restricted fixture, not WGS. It does not by itself exercise
  multi-sample independence, establish biological sensitivity, or provide a known structural
  variant. Those are not prerequisites for the smallest interface and output-contract execution.
- Deterministic assertions for this fixture are successful consumption of the BAM/BAI and
  FASTA/FAI; propagation of metadata `testN`; one raw VCF; and a VCF index when emitted. When
  paired with either required AnnotSV resource below, the same run also asserts one annotated TSV,
  parseable VCF/TSV headers, and version metadata naming GRIDSS and AnnotSV. Exact calls, record
  order, and annotation values are not asserted.

### External resources still required

| Missing role | Required artifact and verification use |
| --- | --- |
| Local annotation scenario | A complete AnnotSV annotations directory compatible with the `chr22` GRCh38 fixture, supplied with its release identifier and archive checksum. It enables the local-annotations acceptance scenario. |
| Automatic annotation scenario | An immutable AnnotSV annotation archive or release URL, its resolved version, and its directory checksum. It enables an automatic-download run without a local annotations input; its extracted content must match the declared local resource version and checksum. |
| Extended WGS semantic oracle | A separately sourced WGS BAM/BAI or CRAM/CRAI pair with a compatible FASTA/FAI, plus an event manifest containing sample ID, contig(s), breakpoints, event class or orientation, and comparison tolerance. It is required only to assert known biological calls beyond the minimal fixture. |
| Extended AnnotSV oracle | Expected annotation fields and values for the declared WGS events, matched by sample and event identity. It is required only for semantic annotation-value comparison. |

### Other searched data

- The nf-core `NA12878.chr21_22.1X` and `NA19401.chr21_22.1X` BAM/BAI pairs are not selected:
  their headers declare full GRCh38-plus-decoy/HLA while the available related FASTA/FAI contains
  only `chr21` and `chr22`.
- The nf-core GRIDSS VCF and GRIDSS properties file are not linked to the selected BAM and are not
  an expected-output oracle.
- Zenodo record 19064653 contains one targeted chr17 BAM/BAI with FASTA/FAI, but no second sample,
  AnnotSV resources, or relevant GRIDSS oracle; it is not selected.

## Acceptance Criteria

- [ ] WHEN `gridss-tsv` receives aligned reads and their indexes for multiple samples, THE System SHALL process each sample independently.
- [ ] WHEN `gridss-tsv` receives a sample's BAM or CRAM and matching index, THE System SHALL require a compatible reference FASTA and FAI index before processing that sample.
- [ ] WHEN a local AnnotSV annotations directory is supplied, THE System SHALL use that directory to annotate every processed sample.
- [ ] WHEN a local AnnotSV annotations directory is not supplied, THE System SHALL obtain AnnotSV annotations automatically before annotation.
- [ ] WHEN GRIDSS completes for a sample, THE System SHALL return that sample's raw structural-variant VCF.
- [ ] WHEN GRIDSS generates an index for a sample's raw structural-variant VCF, THE System SHALL return that index associated with the same sample.
- [ ] WHEN AnnotSV completes for a sample, THE System SHALL return one annotated TSV associated with that sample.
- [ ] WHERE multiple samples are processed, THE System SHALL NOT combine structural-variant calls or annotation results between samples.
- [ ] WHEN `gridss-tsv` completes, THE System SHALL return version metadata that identifies the GRIDSS and AnnotSV versions used.

## Dependencies

- GRIDSS and AnnotSV must be available to the executing environment.
- Automatic annotation retrieval requires access to the AnnotSV annotation source.
- Input alignments, reference FASTA/FAI, and local annotations when supplied must use compatible
  genome assemblies.
