# Nextflow implementation planning

Use the specification's `Test data` value to choose the plan round. Keep one plan for the source
specification and update it in place when builder invokes engineer again.

## Component design and reuse

During the first engineer invocation, derive the functional processing requirements before designing
the final Nextflow structure, even when the immediate round will implement a Bash/Python reference.
Identify the required operations, dependencies, inputs, outputs, methods and intermediate semantics
without assigning module or subworkflow boundaries yet.

Use the `nfcore-component-reuse` skill to determine which requirements, or combinations of
requirements, can reuse existing local or nf-core modules and subworkflows and which require new
implementation. Stop and report to the user if the skill cannot check nf-core when required.

Use that reuse analysis to design the final Nextflow structure. Define the subworkflows, individual
modules, channel shapes, metadata, file formats, intermediate artifacts and dependencies required by
the functional contract.

Classify every component in the final design as `reuse-local`, `import-nf-core`, `new`, or
`local-wiring`, using the `nfcore-component-reuse` analysis as evidence. Requirements reported as
`new-required` must be resolved during final design as new local modules or subworkflows when they
cannot be eliminated by the selected composition.

For nf-core imports, record the exact component type, remote name and pinned `nf-core/modules`
commit SHA and preserve the component's declared containers. Add the exact pipeline root to the
plan so `importing-nf-core` can execute without inferring it. For local reuse, record the existing
path and public interface.

For every reference command and new executable component, record an exact, architecture-compatible
container and an Apptainer-compatible URI. Prefer an immutable image from
`community.wave.seqera.io`; otherwise prefer a compatible BioContainers image. Use another source
only with a recorded justification. Never select `latest`; record the image digest or stable hash,
software version, Apptainer invocation, and required bind mounts.

## Reference round

When test data is `reference-required`, set the plan round to `reference`. Plan an independent,
deterministic Bash/Python implementation that produces concrete inputs, intermediate artifacts and
outputs at every boundary needed to test the planned Nextflow components. Prefer Bash for
orchestration and Python for structured transformations or validation. Do not invoke or translate
the Nextflow components that the later round will test.

Generated data belongs under `{Project_Folder}/reference-data/<spec-slug-id>/` and remains untracked.
Version generation and validation scripts under `{Specs_Folder}/<spec-slug-id>.reference/`. Include
provenance, checksums for every existing input, the selected container and Apptainer commands,
parameters, seeds, expected properties and reproduction commands in the plan. Mark checksums for
outputs that this round will create as `pending-reference-generation`; they are required in the
later Nextflow-round update. For web test data, pin the source revision and checksums and require
the versioned scripts to materialize it from an empty data workspace.

## Nextflow round

When test data is `concrete`, or when builder returns after the committed reference round, set the
plan round to `nextflow`. On the later invocation, update the same plan with the generated paths and
checksums, validate the original component design against the real artifacts, and change it only
when evidence requires an adjustment. Identify direct nf-core imports separately from local TDD
increments so builder can route them correctly.
