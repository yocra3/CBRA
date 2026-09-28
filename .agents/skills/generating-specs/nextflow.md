# Nextflow specifications

Use this profile when the requested behavior will be implemented with Nextflow or nf-core.
Product owner writes one functional specification only. When the request is for a subworkflow,
specify that subworkflow's external behavior and do not decompose it into internal modules. Module
boundaries, implementation choices and reuse decisions belong to the implementation plan.

Add a `Test data` section to the specification:

- Record every concrete input and expected output supplied by the user, including paths, formats,
  required companion files and checksums when available.
- Mark the data as `concrete` only when both sides are available for every required behavior.
- Otherwise mark it `reference-required` and describe the required filenames, formats, semantic
  properties, cardinality, metadata associations and comparison tolerances. Do not invent files or
  implementation details.

Builder uses this value to select one Nextflow round or an automatic Bash/Python reference round
followed by the Nextflow round. Product owner does not search nf-core or the local codebase for
implementation components.
