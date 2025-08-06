# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Bystronic OPC UA client library
- Core `BystronicClient` class for single machine connections
- `MachineMonitor` class for multi-machine monitoring
- Data type definitions for job, plan, part, and run information
- Comprehensive exception handling
- Async/await support throughout
- Basic web interface framework
- Example scripts for common use cases
- Unit test framework setup
- Documentation and API reference

### Features
- Connect to Bystronic laser cutting machines via OPC UA
- Retrieve current job information
- Access historical run data with time-based queries
- Monitor laser parameters in real-time
- Capture machine screen images
- Multi-machine monitoring with automatic reconnection
- Structured data types for consistent API
- Extensible web interface foundation

## [0.1.0] - 2025-01-XX

### Added
- Initial project structure
- Basic OPC UA client implementation
- Documentation and examples
- Test framework setup
- CI/CD pipeline configuration