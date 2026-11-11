# Claude Code Instructions

## Project Overview
You are working on evolving an existing trading bot from a basic system to a professional, robust, adaptive, and performant algorithmic trading system with institutional interface.

## Key Constraints and Guidelines

### 1. Preserve Existing Functionality
- Never remove or delete existing code unless explicitly instructed
- Maintain all current features and behaviors
- Ensure backward compatibility where possible
- All new implementations should integrate with existing architecture

### 2. Use Existing Audit Findings
- The audit has already been completed - do not re-audit the project
- Use the findings and recommendations from the audit as your reference
- Build upon the existing codebase, not from scratch
- Focus on improving rather than rebuilding

### 3. Follow the GOAL.md Roadmap
- Refer to /Users/garonnathan/trading bot/trading-bot/GOAL.md for project goals and task prioritization
- Implement tasks in order of priority as defined
- Update GOAL.md when tasks are completed
- Do not implement features outside the scope defined in GOAL.md

### 4. Architecture Principles
- Organize code into logical modules: core, data, market_intelligence, strategies, genetic, sentiment, risk, portfolio, execution, backtesting, learning, api, monitoring, tests, docs
- Each module should have clear responsibilities and interfaces
- Maintain modular design for scalability and maintainability
- Ensure proper dependency management between modules

### 5. Development Approach
- Work incrementally on one task at a time
- Implement functionality that directly supports the project goals
- Write comprehensive documentation for each component
- Include appropriate tests for all new features
- Follow existing code style and patterns

### 6. Quality Requirements
- Financial reliability is paramount - never compromise safety for performance
- All implementations should be testable and verifiable
- Maintain data integrity throughout all operations
- Ensure system security and proper handling of sensitive information
- Implement proper logging and monitoring

## Task Execution Workflow

1. **Review Current Task**: Check GOAL.md to identify the next task based on priority
2. **Analyze Requirements**: Understand the specific objectives and acceptance criteria
3. **Plan Implementation**: Design approach that integrates with existing codebase
4. **Implement Changes**: Code the solution following existing patterns
5. **Test Implementation**: Verify functionality works as expected
6. **Document Changes**: Update relevant documentation files
7. **Update Task Status**: Mark task as completed in GOAL.md
8. **Move to Next Task**: Proceed with next priority task

## Completed Tasks Summary

- **ARCH-001 (Architecture Refinement)**: Successfully organized codebase into modular structure with core, data, market_intelligence, strategies, genetic, sentiment, risk, portfolio, execution, backtesting, learning, api, monitoring, tests, and docs directories
- **DOC-001 (Documentation Setup)**: Created comprehensive documentation including architecture, modules, decisions, development guidelines, and roadmap
- **RISK-001 (Enhanced Risk Engine)**: Implemented centralized risk management system with dynamic position sizing and comprehensive risk firewalls
- **BT-001 (Realistic Backtesting)**: Implemented enhanced backtesting engine with transaction costs, slippage, and execution quality modeling

## Files and Directories to Focus On

### Core Files:
- main.py (main orchestration)
- engine/backtest/backtest_engine.py (backtesting framework)
- config/rules_v1.py (configuration)
- broker/base_broker.py (broker integration)

### Key Modules to Examine:
- data/ - data loading and processing
- engine/ - core trading engine components  
- risk/ - risk management
- strategies/ - trading strategies
- genetic/ - evolutionary optimization

## Special Considerations

### Data Handling:
- Respect existing data structures and formats
- Maintain data quality and traceability
- Follow existing data storage patterns (Parquet, etc.)

### Risk Management:
- All strategies must comply with central risk controls
- Never bypass or override risk management systems
- Implement proper risk firewalls

### Testing:
- Run existing tests to ensure no regressions
- Add new tests for implemented features
- Validate that all existing functionality still works

## Communication Protocol

When implementing features, provide clear explanations of:
1. What you're changing/adding
2. How it integrates with existing code
3. The benefits it provides to the system
4. Any potential impacts or considerations
5. How it addresses the requirements in GOAL.md

## Important Notes

- Do not assume you have access to external APIs or services not already present
- Use only free, open-source solutions where possible
- Focus on improving what exists rather than creating new systems from scratch
- Maintain the existing project structure and patterns as much as possible