# DOCS Folder Guide: Creating Stories and Building Applications

## Overview

The `DOCS/` folder serves as the central documentation hub for transforming business requirements into working code through a structured story-driven development process. This guide explains how to use the DOCS folder structure to create user stories that AI assistants and developers can use to build complete applications.

## Purpose

The DOCS folder provides:
- **Business Requirements** (`BusinessSpec.txt`) - Raw business needs and objectives
- **Structured Specifications** (`SPEC.md`, `DESIGN.md`) - Formalized requirements and technical design
- **User Stories** (`TASKS/`) - Bite-sized, implementable development tasks
- **Design Rationale** (`DECISIONS.md`) - Why certain technical choices were made
- **Project Status** (`BACKLOG.md`) - Current state and progress tracking
- **Coding Guidelines** (`AI_GUIDE.md`) - Standards for code generation

## Folder Structure

```
DOCS/
├── BusinessSpec.txt          # Original business requirements
├── SPEC.md                   # Functional requirements specification
├── DESIGN.md                 # Technical design document
├── DECISIONS.md              # Design decisions and rationale
├── BACKLOG.md                # Sprint status and backlog
├── AI_GUIDE.md               # Coding standards and guidelines
├── runbook.md                # Operational procedures
├── ExampleFileDownload.txt   # Sample data files (if applicable)
└── TASKS/                    # User stories directory
    ├── README.md             # Story organization guide
    ├── US-001-*.md           # Individual user stories
    ├── US-002-*.md
    └── ...
```

## Workflow: From Requirements to Code

### Step 1: Start with Business Requirements

Begin with `BusinessSpec.txt` or similar document containing:
- Business objectives
- Functional requirements
- Data formats and structures
- Integration points
- Security and performance needs

**Example:**
- Objective: Process data files from external system and update database
- File format: Delimited text files (CSV, pipe-delimited, etc.)
- Database: Your target database system
- Integration: External APIs, file systems, or services

### Step 2: Create Structured Specifications

Transform business requirements into formal specifications:

**`SPEC.md`** - Functional Requirements:
- Detailed feature descriptions
- Data mappings (source columns → target columns)
- Validation rules
- Error handling requirements
- Acceptance criteria

**`DESIGN.md`** - Technical Design:
- Architecture overview
- Technology stack
- Component structure
- Database schema
- File formats
- Error handling strategy

### Step 3: Break Down into User Stories

Create individual story files in `TASKS/` folder. Each story should be:
- **Small and focused** - One feature or component
- **Testable** - Clear acceptance criteria
- **Independent** - Can be developed separately (with dependencies noted)
- **Prioritized** - Assigned to sprints and given priority levels

## User Story Format

Each story file in `TASKS/` follows this structure:

```markdown
# US-XXX: Story Title

**Story Type:** Database Schema | Infrastructure | Feature | Testing | Documentation
**Priority:** Critical | High | Medium | Low
**Sprint:** Sprint number
**Story Points:** Estimated effort (1-13)

## User Story

**As a** [user role],  
**I want** [functionality],  
**So that** [business value].

## Description

Detailed description of what needs to be built, including context and scope.

## Acceptance Criteria

- [ ] Specific, testable requirement 1
- [ ] Specific, testable requirement 2
- [ ] Specific, testable requirement 3

## Technical Notes

- Implementation guidance
- Technology choices
- Code patterns to use or avoid
- Integration points

## Dependencies

- US-XXX (Other story that must be completed first)
- US-YYY (Another dependency)

## Definition of Done

- Code implemented and tested
- Documentation updated
- Code review completed
- Integration tests passing
- All tests passing
- Code quality assessment completed
- No Grade C+ complexity introduced without justification
- Story reviewed and amended by Story QA Agent before implementation
```

### Story Types

- **Database Schema** - Creating tables, indexes, constraints
- **Infrastructure** - Configuration, connection modules, utilities
- **Feature** - Business functionality (parsing, validation, operations)
- **Testing** - Unit tests, integration tests
- **Documentation** - User guides, API docs, runbooks

### Priority Levels

- **Critical** - Blocks other work, must be done first
- **High** - Important for core functionality
- **Medium** - Important but not blocking
- **Low** - Nice to have, can be deferred

## How AI/Developers Use Stories

### 1. Reading Context

AI assistants and developers should read documentation in this order:

1. **`TASKS/US-XXX.md`** - Current story being implemented
2. **`SPEC.md`** - Overall functional requirements
3. **`DESIGN.md`** - Technical implementation details
4. **`DECISIONS.md`** - Design rationale and constraints
5. **`AI_GUIDE.md`** - Coding standards and style guide
6. **`BACKLOG.md`** - Project status and dependencies

### 2. Understanding Dependencies

Before implementing a story:
- Check **Dependencies** section in the story file
- Verify dependent stories are completed (marked "DONE")
- Review related code from completed stories
- Understand integration points

### 3. Implementation Process

When implementing a story:

1. **Read the story completely** - Understand all acceptance criteria
2. **Check dependencies** - Ensure prerequisites are met
3. **Review existing code** - Look for patterns and utilities to reuse
4. **Follow coding guidelines** - Adhere to `AI_GUIDE.md` standards
5. **Implement incrementally** - Build and test each acceptance criterion
6. **Update documentation** - Mark story as "DONE" when complete

### Post-Story Quality Gate

Before marking a story complete:

1. **Run all tests** and verify they pass.
2. **Perform a code quality assessment** (e.g., complexity and maintainability; see `DOCS/CodeQualityChecks/TEMPLATE.md`).
3. **Document any complexity issues introduced** (functions with high cyclomatic complexity or low maintainability).
4. **Update the quality report** if significant changes were made (new modules, refactors, or risky areas).

### 4. Code Generation Guidelines

AI assistants should:
- Use existing helper functions and utilities
- Follow naming conventions specified in `AI_GUIDE.md`
- Keep code simple and readable (avoid over-engineering)
- Create focused, single-purpose functions
- Handle errors gracefully
- Add appropriate comments and docstrings

## Example: Story to Code Workflow

### Story: US-003 - Data Parser Module

**Story says:**
- Parse delimited text files
- Validate required fields
- Map columns to database fields
- Return valid rows and errors

**Implementation:**
1. Create `data_parser.py` module
2. Use appropriate parsing library (e.g., Python `csv` module)
3. Validate each row against requirements
4. Return dictionary with `valid_rows` and `errors`
5. Follow simple function pattern (no classes, no complex patterns)

**Result:** `data_parser.py` with `parse_file()` function

## Story Organization Best Practices

### Naming Convention

- Format: `US-XXX-descriptive-name.md`
- Use kebab-case for descriptive name
- Number sequentially (US-001, US-002, etc.)
- Mark completed stories: `US-XXX-name - DONE.md`

### Sprint Organization

Group stories by sprint in `TASKS/README.md`:
- **Sprint 1:** Foundation (database, infrastructure)
- **Sprint 2:** Core features (parsing, database operations)
- **Sprint 3:** Integration (main script, automation)
- **Sprint 4:** Testing and documentation

### Dependency Management

- List dependencies explicitly in each story
- Ensure foundational stories come first
- Build incrementally - each story builds on previous ones
- Update `BACKLOG.md` to track completion status

## Creating New Stories

### When to Create a Story

Create a new story when:
- A feature is too large to implement in one go
- A component can be developed independently
- You need to track progress on a specific task
- A requirement needs clarification before implementation

### How to Create a Story

1. **Identify the feature** - What needs to be built?
2. **Define the user** - Who will use this feature?
3. **Write user story** - As a... I want... So that...
4. **List acceptance criteria** - What must be true for this to be done?
5. **Add technical notes** - Implementation guidance
6. **Identify dependencies** - What must be done first?
7. **Assign priority and sprint** - When should this be done?

### Story Sizing

- **Small (1-3 points):** Simple functions, single-purpose modules
- **Medium (5 points):** Features with multiple components
- **Large (8-13 points):** Complex features, integration work

Keep stories small enough to complete in 1-3 days of focused work.

## Tracking Progress

### Story Status

- **Pending** - Not started (no "DONE" suffix)
- **In Progress** - Currently being worked on
- **Done** - Completed (rename file to include " - DONE")

### Backlog Management

Update `BACKLOG.md` to reflect:
- Completed items ✅
- In progress items 🚧
- Pending items 📋

## Tips for Effective Story Creation

1. **Be Specific** - Vague stories lead to unclear implementations
2. **Include Examples** - Show expected input/output formats
3. **Define Boundaries** - What's in scope? What's out?
4. **Consider Edge Cases** - What happens when things go wrong?
5. **Reference Existing Code** - Point to similar implementations
6. **Keep It Simple** - Avoid over-engineering in story descriptions

## Common Patterns

### Simple Function Pattern

Instead of classes and complex patterns, use simple functions:

```python
def function_name(param1, param2):
    """
    Brief description of what function does.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description of return value
    """
    # Simple, clear implementation
    pass
```

### Error Handling Pattern

- Continue processing on individual errors
- Log all errors appropriately (database, file, or logging system)
- Return summary of successes and failures
- Don't fail entire process on single error

### File Processing Pattern

1. Download/read file
2. Parse file
3. Validate data
4. Process each record
5. Log errors
6. Generate summary
7. Send notifications (if applicable)

## Using Stories with AI Assistants

### For Users

When asking AI to implement a story:
1. Reference the story file: "Implement US-003 as specified in `DOCS/TASKS/US-003-module-name.md`"
2. Provide context: "This is part of the [project name] project"
3. Reference dependencies: "US-001 and US-002 are already complete"
4. Ask for clarification: "If anything is unclear, ask questions"
5. Stories may not introduce new functional behavior. Any ambiguity or conflict must be documented as a Proposed Spec Change, not silently resolved.

### For AI Assistants

When implementing a story:
1. Read the story file completely
2. Check dependencies are met
3. Review `AI_GUIDE.md` for coding standards
4. Look at existing code for patterns
5. Implement incrementally
6. Test each acceptance criterion
7. Ask questions if requirements are unclear

## Conclusion

The DOCS folder structure provides a clear path from business requirements to working code:

1. **Business Requirements** → `BusinessSpec.txt`
2. **Structured Specs** → `SPEC.md`, `DESIGN.md`
3. **User Stories** → `TASKS/US-XXX.md`
4. **Implementation** → Code files
5. **Documentation** → `runbook.md`, code comments

By following this structure, you create a maintainable, traceable development process where:
- Requirements are clear and testable
- Progress is trackable
- Code follows consistent patterns
- Dependencies are explicit
- Documentation stays current

Use this guide to create effective stories that lead to successful implementations.

