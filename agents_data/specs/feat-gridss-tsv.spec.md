# GRIDSS TSV subworkflow Specification

- **ID**: feat-gridss-tsv
- **Type**: feat
- **Status**: Draft

Allowed status flow: Draft -> Approved -> Planned -> Coded -> Verified -> Released. A requested
revision of the same work reopens this file at Draft.

## Problem Description

CBRA needs an independent `gridss-tsv` subworkflow that calls structural variants with GRIDSS
and annotates each sample with AnnotSV, without changing the existing Manta-based `SV_CALLING`
workflow.

### User Stories

- As a rare-disease analyst, I want per-sample GRIDSS calls annotated by AnnotSV so that I can
  review structural variants for each sample.
- As a pipeline user, I want AnnotSV to use the local annotations in
  `./agents_data/reference_data/Annotations_Human/` when supplied so that annotation can run with
  controlled local reference data.
- As a pipeline maintainer, I want GRIDSS and AnnotSV versions in the results so that outputs are
  traceable.

## Solution Overview

### User/App interface

- Provide an independent `gridss-tsv` Nextflow subworkflow.
- Accept sample-associated BAM or CRAM files and indexes, plus a compatible reference FASTA and
  FAI index.
- Accept `./agents_data/reference_data/Annotations_Human/` as the optional local AnnotSV
  annotations-directory input. If it is absent, obtain AnnotSV annotations automatically.
- Return, per processed sample, the AnnotSV-annotated TSV, the raw GRIDSS VCF, and its index when
  generated. Return GRIDSS and AnnotSV version metadata.

### Model and logic

- Process samples independently and retain their input sample identity on all sample outputs.
- Annotate each sample's GRIDSS VCF with the selected AnnotSV annotations source.
- Do not expose an unannotated AnnotSV TSV.

### Persistence

- Return result files and version metadata through subworkflow outputs.
- No persistent database or downloaded-annotation cache is required.

## Boundaries

- `SV_CALLING`, its Manta behavior, configuration, and outputs are out of scope.
- Joint or cohort-level calling, GRIDSS-specific reference bundles, and unannotated AnnotSV TSV
  outputs are out of scope.

## Inputs and Outputs

| Direction | Item | Required | Functional contract |
| --- | --- | --- | --- |
| Input | Sample-aligned reads | Yes | BAM or CRAM associated with a sample identifier. |
| Input | Reference genome | Yes | FASTA and FAI index compatible with the aligned reads. |
| Input | Local AnnotSV annotations | No | Directory `./agents_data/reference_data/Annotations_Human/`; when supplied, it is the AnnotSV annotation source. |
| Output | Annotated structural variants | Yes | One AnnotSV-annotated TSV per processed sample. |
| Output | Raw structural-variant calls | Yes | One GRIDSS VCF per processed sample. |
| Output | GRIDSS VCF index | Conditional | The index for a returned VCF when GRIDSS generates it. |
| Output | Software versions | Yes | Metadata identifying the GRIDSS and AnnotSV versions. |

## Test Data

- **Status**: concrete
- Use one indexed BAM or CRAM, a compatible FASTA/FAI, and the local annotations directory
  `./agents_data/reference_data/Annotations_Human/`.
- Assert successful consumption of all inputs; a sample-associated raw VCF; its index when
  generated; a sample-associated annotated TSV; and version metadata naming GRIDSS and AnnotSV.
- A second scenario without the local annotations input asserts automatic annotation retrieval and
  the same output contract.
- A multi-sample scenario asserts one independent VCF and annotated TSV for each input sample.

## Acceptance Criteria

- [ ] WHEN `gridss-tsv` receives a sample BAM or CRAM with its index, THE System SHALL require a compatible reference FASTA and FAI index before processing that sample.
- [ ] WHEN `gridss-tsv` receives `./agents_data/reference_data/Annotations_Human/` as its local AnnotSV annotations input, THE System SHALL use that directory to annotate every processed sample.
- [ ] WHEN the local AnnotSV annotations input is absent, THE System SHALL obtain AnnotSV annotations automatically before annotation.
- [ ] WHEN `gridss-tsv` receives multiple samples, THE System SHALL process each sample independently without combining calls or annotations.
- [ ] WHEN GRIDSS completes for a sample, THE System SHALL return that sample's raw structural-variant VCF and its index if GRIDSS generated one.
- [ ] WHEN AnnotSV completes for a sample, THE System SHALL return one annotated TSV associated with that sample.
- [ ] WHEN `gridss-tsv` completes, THE System SHALL return version metadata that identifies the GRIDSS and AnnotSV versions used.

## Dependencies

- GRIDSS and AnnotSV are available to the execution environment.
- Input alignments, reference FASTA/FAI, and the local annotations directory use compatible genome
  assemblies.
- Automatic annotation retrieval requires access to the AnnotSV annotation source.
