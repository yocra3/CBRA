## Implementation Plan for <spec-slug-id>

- **Specification**: `{Specs_Folder}/<spec-slug-id>.spec.md`
- **Plan round**: `<reference | nextflow | single-round | not-applicable>`
- **Pipeline root**: `<absolute path or not-applicable>`

## Environment and reproducibility

- **Execution environment**: `<required runtime, profiles, plugins and architecture constraints>`
- **Containers**: `<exact image URI and digest or stable hash for each reference command or new executable component; include Apptainer invocation and bind mounts, or not-applicable>`

## Test data and artifacts

| Boundary | Role | Path or materialization command | Format and semantics | Checksum |
| --- | --- | --- | --- | --- |
| `<boundary>` | `<input | intermediate | output>` | `<path or command>` | `<format, cardinality, metadata associations and tolerances>` | `<checksum, pending-reference-generation, or not-applicable>` |

## Component design

| Component | Classification | Contract and evidence | Source |
| --- | --- | --- | --- |
| `<component>` | `<reuse-local | import-nf-core | new | local-wiring>` | `<public interface, channel shape and compatibility evidence>` | `<local path, or nf-core type/name/modules SHA, or not-applicable>` |

## Acceptance criteria coverage

| Acceptance criterion | Plan increment | Verification |
| --- | --- | --- |
| `<criterion identifier>` | `<step number>` | `<test boundary and expected evidence>` |

### Step 1: {Step Title}
{short description of the step}
- [ ] {One line Task 1 description}

## Blockers

- `<blocker or none>`
