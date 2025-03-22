# Active Context

## Current Work Focus

We are currently in the initial setup phase of the FastAPI SQLite API project. The focus is on:

1. Setting up the project structure
2. Implementing the database models
3. Creating the API endpoints
4. Testing the functionality

## Recent Changes

- Created the project documentation in the memory bank
- Defined the project structure and architecture
- Specified the technical requirements and dependencies

## Next Steps

1. Update pyproject.toml with necessary dependencies
2. Create the project directory structure
3. Implement the database models and connection
4. Implement the authentication system
5. Create the user endpoints
6. Create the transaction endpoints
7. Add testing and documentation

## Active Decisions and Considerations

- **Database Choice**: Using SQLite for simplicity and portability. This will make it easy to develop and test without requiring a separate database server.
- **API Structure**: Following RESTful design principles for a clean and intuitive API.
- **Authentication**: Implementing JWT-based authentication for secure user access.
- **Money Handling**: Storing monetary values as integers (cents) to avoid floating-point precision issues.
- **Error Handling**: Creating a consistent error handling mechanism throughout the API.
- **Documentation**: Adding OpenAPI documentation for easy API discovery and testing.