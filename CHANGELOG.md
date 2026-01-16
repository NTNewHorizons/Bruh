# Changelog
### Added
- Configuration file system (`config.txt`) for centralized parameter management
- Startup validation system with pre-flight checks for channels, roles, and message files
- Comprehensive error reporting with actionable diagnostic messages
- Type validation for all numeric configuration parameters
- Token validation to detect placeholder and invalid values
- Permission verification for channel access
- Console status output showing component initialization results

### Fixed
- Configuration errors now provide specific field names and expected types
- Missing channels/roles now report exact IDs and configuration locations
- File access errors now specify which file and the underlying cause
- Command execution errors now include command name, executor, and error context

### Changed
- Bot token moved from source code to configuration file
- Command prefix now configurable (default: `!`)
- All channel IDs externalized to configuration
- All role IDs externalized to configuration
- Message file paths now configurable
- Behavioral parameters (message frequency, timeouts) now configurable
- Error messages replaced with structured diagnostic output
- Hardcoded values eliminated from Python source code