# Nextflow specifications

Use this profile when the requested behavior will be implemented with Nextflow or nf-core.
Product owner writes one functional specification only. When the request is for a subworkflow,
specify that subworkflow's external behavior and do not decompose it into internal modules. Module
boundaries, implementation choices and reuse decisions belong to the implementation plan.

Add a `Test data` section to the specification:

- Define the smallest executable scenario for each required behavior. Prefer a
  sample restricted to one chromosome or genomic region when that exercises
  the same interface and control flow as full-scale data.
- For each input role, define the format, semantic requirements and compatibility relationships
  required by the behavior. A discovered file may be recorded as:
  - `required` when that exact fixture is part of the functional requirement;
  - `candidate` when it is a suitable fixture that implementation planning may replace;
  - `unresolved` when only the required properties are known.
  Record available companion files with a candidate, but do not make them requirements unless
  the functional contract requires them.
- Preserve the smallest suitable fixtures already found even when some input roles remain
  unresolved. Describe unresolved inputs by their required format, semantic properties,
  cardinality, metadata associations and compatibility constraints.
- Define deterministic functional assertions independently from the concrete fixture whenever
  possible.
- Product owner searches reference datasets, not implementation components. Concrete fixture
  resolution, implementation-specific companions, derived test prerequisites and reference
  generation belong to implementation planning.

