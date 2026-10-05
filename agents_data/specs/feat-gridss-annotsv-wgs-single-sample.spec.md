# GRIDSS and AnnotSV WGS single-sample subworkflow Specification
- **ID**: feat-gridss-annotsv-wgs-single-sample
- **Type**: feat
- **Status**: Draft

## Problem Description

CBRA needs an independent structural-variant analysis subworkflow for rare-disease WGS samples. It must call structural variants with GRIDSS and annotate those calls with AnnotSV using a compatible, configurable GRCh38 reference and annotation set. The existing Manta-based `SV_CALLING` subworkflow is outside this work.

### User Stories

- As a rare-disease analyst, I want to submit one paired-end WGS sample with its aligned reads and GRCh38 reference so that I receive GRIDSS structural-variant calls annotated by AnnotSV.
- As a pipeline operator, I want the subworkflow to emit audit artifacts so that I can identify the software versions and calling metrics for a completed sample.

## Solution Overview

### User/App interface

- Provide an independent Nextflow DSL2 subworkflow for one WGS paired-end sample.
- Accept one sample metadata record with a coordinate-sorted BAM and matching BAI, a GRCh38 FASTA and matching FAI, and an AnnotSV annotation directory.
- Allow the GRCh38 FASTA/FAI and AnnotSV annotation directory to be supplied as configurable inputs.
- Do not invoke, modify, replace, or change the inputs or outputs of `SV_CALLING` or its Manta behavior.

### Model and logic

- Run GRIDSS on the supplied single sample and pass its structural-variant VCF to AnnotSV.
- Preserve the input sample metadata association on every per-sample result.
- Treat the BAM/BAI, FASTA/FAI, and AnnotSV annotations as mutually compatible GRCh38 resources.
- Produce the GRIDSS VCF, GRIDSS metrics/audit artifacts, AnnotSV VCF, AnnotSV TSV, and software-version audit information.

### Persistence

- Produce workflow result files only; this work introduces no persistent database or external service.

## Test data

- **Scenario:** one paired-end WGS sample restricted to a small genomic region, with at least one expected structural-variant record, exercises GRIDSS calling and AnnotSV annotation end to end.
- **BAM/BAI:** unresolved fixture; one coordinate-sorted paired-end WGS BAM and its matching BAI. The alignment contigs and sample identity must match the selected GRCh38 FASTA/FAI.
- **FASTA/FAI:** unresolved fixture; a GRCh38 FASTA limited to the scenario region and its matching FAI, compatible with the BAM/BAI.
- **AnnotSV annotations:** required source location: `agents_data/reference-data/Annotations_Human`. Planning must select or prepare the smallest GRCh38-compatible annotation directory from this location and record any required companion content.
- **Assertions:** independently of the chosen fixture, the scenario shall produce a non-empty GRIDSS VCF; each required AnnotSV result shall retain the same sample metadata; and the emitted annotation VCF and TSV shall describe the GRIDSS call set.

## Acceptance Criteria

- [ ] WHEN a single paired-end WGS sample is supplied with a coordinate-sorted BAM and its matching BAI THEN THE System SHALL accept the sample as one GRIDSS calling unit.
- [ ] WHEN compatible GRCh38 FASTA and FAI inputs are supplied THEN THE System SHALL use those configured reference inputs for the GRIDSS calling unit.
- [ ] WHEN an AnnotSV annotation directory compatible with the configured GRCh38 reference is supplied THEN THE System SHALL use it to annotate the GRIDSS structural-variant VCF.
- [ ] WHEN GRIDSS completes for the calling unit THEN THE System SHALL emit a GRIDSS structural-variant VCF associated with the input sample metadata.
- [ ] WHEN GRIDSS completes for the calling unit THEN THE System SHALL emit its metrics or other audit artifacts and software-version audit information associated with that run.
- [ ] WHEN AnnotSV completes for the GRIDSS VCF THEN THE System SHALL emit an AnnotSV VCF and an AnnotSV TSV associated with the input sample metadata.
- [ ] WHEN the minimal test scenario uses GRCh38-compatible resources selected from `agents_data/reference-data/Annotations_Human` THEN THE System SHALL produce non-empty GRIDSS and AnnotSV result files for the sample.
- [ ] WHILE this subworkflow is added THEN THE System SHALL preserve the existing `SV_CALLING` subworkflow and its Manta-based external behavior unchanged.

## Dependencies

- GRIDSS runtime and its required reference-compatible resources.
- AnnotSV runtime and GRCh38-compatible annotation content from `agents_data/reference-data/Annotations_Human`.
- A compatible paired-end WGS BAM/BAI and GRCh38 FASTA/FAI test fixture.

## User-confirmed Decisions

- The work is a new independent GRIDSS plus AnnotSV subworkflow.
- Scope is one paired-end WGS sample per invocation.
- GRCh38 reference inputs are configurable.
- Required outputs are GRIDSS VCF, GRIDSS metrics/audit artifacts, AnnotSV VCF, and AnnotSV TSV.
- `SV_CALLING` and its Manta implementation are out of scope.

## Unresolved Questions

- None for this lifecycle specification. The implementation plan shall resolve concrete minimal fixture files and implementation-specific GRIDSS configuration prerequisites.
