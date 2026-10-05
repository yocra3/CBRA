# Nextflow implementation planning

Create one complete implementation plan for the source specification. Resolve the component
design, concrete test fixtures, required companions, derived test prerequisites, reference
generation, and ordered implementation phases before implementation begins.

## Component design and reuse

During planning, derive the functional processing requirements before
designing the final Nextflow structure or its reference-generation phases.
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

Resolve implementation order from dependencies. Place reusable or imported dependencies before
new components that consume them, then order new modules before dependent subworkflows and
higher-level local wiring.

For `reuse-local`, do not plan an implementation phase when the existing
component is consumed unchanged. Represent any new consuming behavior
separately as `local-wiring`.

For nf-core imports, record the exact component type, remote name and pinned `nf-core/modules`
commit SHA and preserve the component's declared containers. Add the exact pipeline root to the
plan so `importing-nf-core` can execute without inferring it. For local reuse, record the existing
path and public interface.

For every reference command and new executable component, record an exact, architecture-compatible
container and an Apptainer-compatible URI. Prefer an immutable image from
`community.wave.seqera.io`; otherwise prefer a compatible BioContainers image. Use another source
only with a recorded justification. Never select `latest`; record the image digest or stable hash,
software version, Apptainer invocation, and required bind mounts.

Inspect the test evidence reported by `nfcore-component-reuse` when resolving concrete fixtures.
A specification fixture marked `required` must be preserved. A `candidate` may be replaced when
the selected implementation requires a different compatible fixture; record the reason.

## Increment execution

For every component in the final design, define its implementation phases in dependency order.

For `import-nf-core`, plan one direct coder phase using `importing-nf-core`. Do not plan a local
TDD cycle or cleaner phase for the imported component.

For each new local executable component or new local wiring that requires functional testing,
resolve:

- concrete input fixtures;
- companions actually required by the selected component interface;
- derived test prerequisites required only to execute the test;
- the independent method used to produce reference outputs;
- executable validation criteria for those reference outputs;
- the production test boundary and expected snapshots or assertions.

A derived test prerequisite is test infrastructure produced from another fixture, such as an
index derived from a reference FASTA. It is not a product input unless the functional contract
explicitly makes it one.

The reference method may use an existing tool or upstream component command, or an independent
Bash/Python implementation. It must not invoke, translate, or reuse the production implementation
that the later test will exercise.

For a new component requiring reference outputs, declare the phases in this order:

1. `tester: reference-validation`
2. `coder: reference-generation`
3. `tester: production-test`
4. `coder: production-implementation`
5. `cleaner: production-refactor`

The reference-validation phase defines executable expectations before reference generation.
The reference-generation phase materializes required test prerequisites and reference outputs
until those validations are GREEN. The production-test phase then freezes expectations and
establishes RED against the not-yet-implemented production behavior. Cleaner is planned only
after production GREEN.

Generated reference data belongs under
`{Project_Folder}/reference-data/<spec-slug-id>/` and remains untracked. Version any required
generation or validation helpers under `{Plans_Folder}/<spec-slug-id>.reference/`. Record
provenance, checksums, containers, commands and reproduction information required to recreate
the artifacts from an empty workspace.