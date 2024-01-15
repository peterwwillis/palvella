# palvella

## Design

See [DESIGN.md](./DESIGN.md)

## Development Environment

### Setup

 1. Load the `.rc` file in your shell. This will install system dependencies (if needed), pyenv, and then the pinned version of Python.
 2. Run `make dev.environ poetry`. This will install development environment dependencies, which includes poetry.

## Containerization

### Building

 1. Run:
        $ cd dev/pyenv/
        $ make docker

## Testing

 1. Run `make test-e2e` to run a basic end-to-end test.
