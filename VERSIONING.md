# Versioning

## Version Format
Semantic versioning in format `X.Y.Z`:
- X: Major version (breaking changes)
- Y: Minor version (new features, backward compatible)
- Z: Patch version (bug fixes)

## Version Source
The canonical version is stored in `VERSION` file (format: X.Y.Z).

## Version Bump Rules
- Push to `main` branch MUST include a version bump
- Version MUST be updated in VERSION file
- Use conventional commit messages: `fix:`, `feat:`, `feat!:`, `fix!:`, etc.
- CI will fail if version is not bumped on push to main
