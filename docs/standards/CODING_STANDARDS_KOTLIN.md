# Kotlin Coding Standards for NFC Reader/Writer System

## Fundamental Rules
1. All code must adhere to these standards
2. Code will not be merged without passing linting and style checks
3. All code must include appropriate documentation

## Style Guide
We follow the [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html) with the following specifics:

### Formatting
- 4 spaces for indentation (no tabs)
- Maximum line length of 100 characters
- Use blank lines to separate logical sections
- Place curly braces on the same line as the code construct
- No trailing whitespace

### Naming Conventions
- `camelCase` for variables, functions, and methods
- `PascalCase` for classes, interfaces, objects, and type parameters
- `UPPER_CASE` for constants and singleton objects
- Prefix private properties with underscore (_)

### Class Structure
- Order class contents as follows:
  1. Properties and initialization blocks
  2. Secondary constructors
  3. Method declarations
  4. Companion object
- Group and sort methods by functionality rather than scope or accessibility

### Function Structure
- Single responsibility principle: functions should do one thing
- Keep functions small and focused
- Use named parameters for better readability with multiple parameters
- Prefer expression functions for simple cases

## Documentation
- All classes, methods, and functions must include KDoc comments
- Document non-obvious behavior
- Include tags for parameters, return values, and exceptions
- Use descriptive variable and function names

Example:
```kotlin
/**
 * Processes NFC tag data and extracts structured information.
 *
 * @param rawData The raw binary data from the NFC tag
 * @param validate Whether to validate the data structure
 * @return Structured data extracted from the NFC tag
 * @throws InvalidNfcDataException If the data format is invalid and validate=true
 */
fun processNfcData(rawData: ByteArray, validate: Boolean = true): NfcData {
    // Implementation
}
```

## Architecture
- Follow MVVM architecture pattern
- Use Android Architecture Components (ViewModel, LiveData, etc.)
- Use Kotlin Coroutines for asynchronous operations
- Use dependency injection (Hilt or Koin)
- Use Clean Architecture principles where appropriate

## Android-Specific Guidelines
- Avoid long operations on the main thread
- Use view binding instead of findViewById
- Use Kotlin extensions for View operations
- Follow Material Design guidelines for UI components
- Minimize XML layout nesting

## Coroutines and Asynchronous Code
- Use structured concurrency patterns
- Handle exceptions properly in coroutine scopes
- Use appropriate dispatchers for different operations
- Prefer suspending functions over callbacks
- Use Flow for reactive streams

## Testing
- Write unit tests for all business logic
- Use JUnit and Mockito for unit tests
- Use Espresso for UI tests
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies and services

## Error Handling
- Use sealed classes for representing operation results
- Properly handle and display user-facing errors
- Log errors with appropriate context
- Never catch generic exceptions without proper handling

## Project-Specific Guidelines
- All NFC operations must handle potential hardware errors
- USB and WiFi connections must implement proper connection state management
- Implement graceful degradation for missing hardware features
- Cache data locally for offline operation
- Implement proper permission handling

## Linting and Enforcement
- Use ktlint for code formatting
- Use detekt for static analysis
- Configure pre-commit hooks to enforce standards
- Use Android Studio's built-in lint checks

## Version Control
- Commit messages should follow conventional commits format
- Each commit should address a single logical change
- Branch naming: `feature/description`, `bugfix/description`, `refactor/description`
- Pull requests require code review before merging

## Security Guidelines
- Never store sensitive information in code or shared preferences
- Use Android Keystore for secure storage
- Validate all user inputs
- Implement proper NFC tag authentication where applicable
- Use encrypted communication for all network traffic
- Follow Android security best practices
