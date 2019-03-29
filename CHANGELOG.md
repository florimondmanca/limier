# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.0.2]

Released: 2019-03-29

### Changed

- `@deduce` is now `@converted`.
- Remove metaphors from the internal API: `.converter`, `.get`, `.chain`.

## v0.0.1

Released: 2019-02-12

Initial release.

### Added

- Main API: `limier.deduce`.
- Generic converters: `Identity`, `Transform`, `Filter`, `Equiv`, `OneOf`, `Regex`, `Range`.
- Clue system: built-in clues, `.record`, `.clue`, `.retrieve`, `.chain`.

[unreleased]: https://github.com/florimondmanca/limier/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/florimondmanca/limier/compare/v0.0.1...v0.0.1
