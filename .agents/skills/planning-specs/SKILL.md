---
name: planning-specs
description: Create or update the single implementation plan for an approved specification. Do not use for unscoped ideas or direct code edits.
---

# Generate Plan Skill

Resolve `{Specs_Folder}` and `{Plans_Folder}` from global instructions.
Stop if a required placeholder or input artifact cannot be resolved.

The plan will be a set of ordered steps, each with specific tasks to complete.

## Context

- [The Specification file]({Specs_Folder}/<spec-slug-id>.spec.md)

Each source specification owns one plan. Resolve an existing plan by its specification identifier
or path before choosing an output path.

For Nextflow work, also load [Nextflow planning](./nextflow.md).

## Steps to follow:

### Step 1: Think about the overall implementation.
 - [ ] Understand the specification requirements.
 - [ ] Consider relevant repository conventions and existing interfaces.
 - [ ] Choose the simplest viable approach to implement the spec.
### Step 2: Decompose the implementation in steps.
 - [ ] Break down the implementation into 3 to 9 steps 
 - [ ] Ensure each step is an ordered logical unit of work.
### Step 3: Define tasks for each step.
 - [ ] For each step, list specific tasks (<= 5) needed to complete it.
 - [ ] Ensure tasks are clear and actionable.
### Step 4: Resolve and write the implementation plan.
 - [ ] Follow the format in the [Implementation Plan template](plan.template.md).
 - [ ] If exactly one plan already maps to the specification, update it in place and preserve its path.
 - [ ] If no plan maps to the specification, create `{Plans_Folder}/<spec-slug-id>.plan.md`.
 - [ ] If multiple candidates exist, stop and ask the user; do not create another plan.
### Step 5: Review and finalize the plan.
 - [ ] Ensure the plan is comprehensive and feasible.
 - [ ] After the initial plan is finalized, change the source specification from `Approved` to
   `Planned`. Preserve `Planned` when a later round updates the same plan.
 - [ ] Do not skip or regress an existing later status.

## Output Checklist

- [ ] A detailed implementation plan at `{Plans_Folder}/<spec-slug-id>.plan.md`.
- [ ] Exactly one plan file associated with the source specification.
- [ ] The source specification marked `Planned` when its previous status was `Approved`.
- [ ] The source specification identifier, plan path, whether it was created or updated, and
  resulting specification status reported to the caller.
