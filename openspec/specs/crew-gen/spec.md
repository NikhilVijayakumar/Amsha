# Crew Gen

## Purpose

Defines the current state of the retired `crew_gen` capability so its history
remains represented in the knowledge/spec system without implying that Amsha
still ships `crew_gen` as a live runtime module.

Knowledge concept: [knowledge/features/crew-gen.md](../../../knowledge/features/crew-gen.md)

## Requirements

### Requirement: Crew Gen is retired from the runtime source tree

Amsha MUST NOT present `crew_gen` as a live runtime module when the runtime
source tree contains no `crew_gen` package under `src/nikhil/amsha/`.

#### Scenario: Runtime source tree is inspected

- **WHEN** the runtime modules under `src/nikhil/amsha/` are listed
- **THEN** `crew_gen` is absent from the live source tree
- **AND** it is not treated as a shipped runtime capability

### Requirement: Historical Crew Gen intent remains visible as retired knowledge

The retired `crew_gen` capability MUST remain represented as retired knowledge
rather than being deleted or treated as current runtime behaviour.

#### Scenario: Retired capability is reviewed

- **WHEN** the retired `crew_gen` capability is reviewed
- **THEN** its historical intent is preserved through a deprecated knowledge concept
- **AND** it is not mistaken for a live module contract
