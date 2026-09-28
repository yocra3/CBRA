# Nextflow specifications

Use this profile when the requested behavior will be implemented with Nextflow or nf-core.
Product owner writes one functional specification only. When the request is for a subworkflow,
specify that subworkflow's external behavior and do not decompose it into internal modules. Module
boundaries, implementation choices and reuse decisions belong to the implementation plan.

Add a `Test data` section to the specification:

- Define the smallest executable scenario for each required behavior. Prefer a
  sample restricted to one chromosome or genomic region when that exercises
  the same interface and control flow as full-scale data.
- Follow [reference test data](test_data.md) to search nf-core/test-datasets
  before considering the allowed local-module Zenodo record.
- Record each concrete input, its role, path, format, required companion files,
  checksums when available, and only the compatibility relationships that the
  software relies on. Do not require independent inputs to belong to the same
  sample or experiment.
- Define deterministic output assertions appropriate to a functional test.
  Do not require a complete biological truth set or source-supplied expected
  output unless an acceptance criterion explicitly requires exact biological
  correctness.
- Mark the data as `concrete` when every required minimal scenario has the
  inputs and assertions needed to execute and observe it. This does not require
  whole-genome data, multiple samples, a production annotation bundle, or one
  source containing every input and output.
- Mark it `reference-required` only when a required minimal scenario still
  lacks an essential input, companion file, compatibility relationship, or
  deterministic assertion. Preserve and document all concrete inputs already
  found, then describe only the missing artifacts and their required formats,
  semantic properties, cardinality, metadata associations, and comparison
  tolerances. Do not invent files or implementation details.

Builder uses this value to select one Nextflow round or an automatic Bash/Python reference round
followed by the Nextflow round. Product owner searches reference datasets, not implementation
components.
