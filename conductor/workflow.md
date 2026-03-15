# Conductor Workflow

## Test Coverage
- Minimum: 80% coverage required before a task is marked complete

## Commit Strategy
- Commit after each task completion
- Commit message format: `type(scope): description`
  - e.g. `feat(scraper): add Playwright page navigation`

## Task Summaries
- Use Git Notes to store task summaries (not commit messages)

## Task Lifecycle
1. Read spec.md and plan.md for context
2. Implement the task (TDD preferred — write tests first)
3. Verify tests pass and coverage ≥ 80%
4. Manual verification step (user confirms behavior)
5. Commit with Git Note summary
6. Mark task complete in plan.md

## Definition of Done
- [ ] Code implemented
- [ ] Tests written and passing
- [ ] Coverage ≥ 80%
- [ ] User manual verification complete
- [ ] Committed to git
