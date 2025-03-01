

## General Development Best Practices
- Search for existing files before creating new files
- Do not remove any existing code unless necessary
- Do not remove my comments or commented-out code unless necessary
- Use curly braces for all conditionals
- Always use best practices
- Use clean architecture principles
- Don't put placeholders, implement everything required
- Always make sure that a file doesn't exist before attempting to create it
- Always follow best practices
- Always follow coding standards
- Split large files into components
- Don't give incomplete code like "// Add any <something> code here"
- Don't remove code unnecessarily
- Don't ever give "// ... rest of the code ..." as a response
- Don't you ever give "// ... existing " as a response
- Don't add placeholder methods like "ShouldDoSomething"
- Always update the CHANGELOG.md file with summarized changes after making changes. Create it if it doesn't exist. Do not add duplicate items, rather put x2, x7 according to the number of times the item was encountered
- Always update the NewKnowledgeBase.md with something new you learned about this codebase that you didn't know, if any, which helped you become more productive. Do not add duplicate items, rather put x2, x7 according to the number of times the item was encountered
- Streamlit uses a testid of stColumn not column, for columns
- In React web applications which are mobile responsive, make sure that you're modifying the right component and CSS styles, for mobile or desktop
- Always when generating test add along an additional string in Gherkin format
- You should start the reasoning paragraph with lots of uncertainty, and slowly gain confidence as you think about the item more
- The fewer line of code the better
- Proceed like a Senior Developer // 10x engineer
- Always you come up with an approach think about another 2 possible approaches then decide which is the best and continue with it
- Always create tests first then follow with methods
- Always after updating changelog and newknowledgebase run all tests to see if they pass

## Project Creation and Architecture Rules
- Create a comprehensive project README.md with setup instructions and project overview before writing any code
- Establish a clear folder structure following domain-driven design principles at the beginning of the project
- Implement a dependency injection container early to facilitate loose coupling and testability
- Create interface definitions before implementations to ensure proper abstraction
- Document API endpoints in a separate markdown file or using OpenAPI/Swagger annotations
- Maintain a .env.example file that lists all required environment variables without sensitive values
- Create clear separation between domain logic, application services, and infrastructure components
- Establish coding conventions and linting rules in configuration files before writing code
- Implement a robust error handling strategy at the application's foundation
- Create database migration scripts alongside each model/schema definition
- Document all public interfaces and methods with JSDoc or similar documentation standard
- Include version compatibility information for all external dependencies
- Create typed interfaces for all data structures before implementation

## Test-Driven Development (TDD) Rules
- Write failing tests before implementing corresponding functionality
- Organize tests to mirror the structure of the source code they're testing
- Create separate test files for unit, integration, and e2e tests
- Establish test fixtures and factories before implementing core functionality
- Implement mocks for external dependencies to ensure unit tests are isolated
- Write tests for edge cases and error conditions, not just happy paths
- Include performance assertions in tests for time-critical operations
- Test all public APIs and interfaces thoroughly
- Implement test coverage reporting and maintain minimum coverage thresholds
- Create integration tests for all database operations
- Test asynchronous operations with appropriate timeout handling
- Implement property-based testing for complex algorithms like trading strategies
- Create test utilities for common testing operations early in development
- Document test scenarios in BDD (Behavior-Driven Development) style with Given/When/Then format
- Implement continuous integration testing before feature completion
- Test both successful and failing conditions for all API endpoints
- Create regression tests for any bugs discovered during development
- Ensure mocked database operations match actual database behavior
- Test user interface components with snapshot testing where appropriate
- Create parameterized tests for strategies with different input configurations
- Verify memory usage for long-running processes through appropriate tests

## Crypto Trading Bot Specific Rules
- Implement proper decimal precision handling for all currency calculations
- Create comprehensive tests for exchange rate conversions and fee calculations
- Document all trading strategies with mathematical formulas and references
- Create data validation rules for all external API responses
- Implement proper logging for all trading decisions with reasoning
- Test trading algorithms against historical market data
- Create separate environments for development, testing, and production
- Implement circuit breakers for trading strategies to prevent catastrophic losses
- Document risk management strategies and implement corresponding tests
- Create visualization components for strategy performance metrics
- Test concurrency handling for simultaneous trading operations
- Implement proper serialization/deserialization for all trading data
- Document the expected behavior of machine learning components
- Create comprehensive tests for strategy selection logic
- Test notification systems with various alert conditions