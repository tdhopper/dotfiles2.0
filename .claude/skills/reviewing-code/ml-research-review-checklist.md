# ML Research Code Review Checklist

Detailed checklist for reviewing ML research and internal tooling code.

## Implementation Completeness

- [ ] All stated functionality is implemented (no TODOs left for core logic)
- [ ] Error handling covers realistic failure modes (file not found, network errors, invalid input shapes)
- [ ] Edge cases are handled (empty inputs, single-item batches, boundary conditions)
- [ ] Return types and values match documented behavior
- [ ] Any feature flags or conditionals have both paths implemented

## Test Quality

### Coverage
- [ ] New public functions have corresponding tests
- [ ] New code paths are exercised by tests
- [ ] Bug fixes include regression tests

### Test Design
- [ ] Tests verify behavior, not implementation details
- [ ] Tests have descriptive names indicating what they verify
- [ ] Tests would fail if the feature broke (not just smoke tests)
- [ ] Edge cases have dedicated tests
- [ ] Tests are independent and don't rely on execution order

### Test Clarity
- [ ] Test setup is minimal and clear
- [ ] Assertions have clear failure messages where appropriate
- [ ] Mock/fixture usage is justified and not excessive

## Complexity Assessment

### Abstraction
- [ ] New abstractions serve a clear purpose
- [ ] Existing patterns are followed rather than inventing new ones
- [ ] Class hierarchies are justified (not over-engineered)
- [ ] Generic solutions match actual use cases (not speculative)

### Code Structure
- [ ] Functions have single, clear responsibilities
- [ ] Nesting depth is reasonable (max 3-4 levels)
- [ ] Control flow is straightforward
- [ ] Dependencies between components are explicit

### Cognitive Load
- [ ] Code can be understood without extensive context
- [ ] Magic numbers/strings are named constants
- [ ] Complex logic has explanatory comments

## Performance Considerations

- [ ] No obvious performance regressions introduced
- [ ] Expensive operations are justified by the use case
- [ ] Resource usage is proportional to input size

## Duplication Detection

- [ ] Similar functionality doesn't already exist elsewhere
- [ ] Utility functions are placed in appropriate shared modules
- [ ] Copy-pasted code blocks are extracted to shared functions
- [ ] Constants aren't redefined (use existing definitions)

## ML-Specific Concerns

### Tensor Operations
- [ ] Shape assumptions are documented or validated
- [ ] Device placement is explicit (CPU/GPU)
- [ ] Dtype handling is consistent
- [ ] Gradient tracking is appropriate (with/without torch.no_grad())

### Data Pipeline
- [ ] Data loading doesn't bottleneck training
- [ ] Preprocessing is deterministic where required
- [ ] Shuffling/sampling is reproducible when seeded

### Model Code
- [ ] Weight initialization is appropriate
- [ ] Forward pass is efficient
- [ ] No detach() calls that break gradient flow unintentionally
- [ ] Model can be serialized/loaded correctly

## Side Effect Assessment

- [ ] Changes don't affect unrelated functionality
- [ ] API changes are backward compatible (or intentionally breaking)
- [ ] Default values are sensible
- [ ] Changes to shared utilities don't break other callers
- [ ] Config/environment changes are documented

## Project Guidelines Compliance

Check against project-specific guidelines (CLAUDE.md, AGENTS.md):
- [ ] Follows established patterns for similar features
- [ ] Uses project conventions for error handling
- [ ] Matches existing code organization
- [ ] Adheres to any ML-specific practices documented
