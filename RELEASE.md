# How to create a new release for Gazu

We release Gazu versions through Github Actions on Pypi. Every time a new version is ready, we
follow this process:

1. Rebase on the main branch.
2. Up the version number located the `gazu/__version__` file.
3. Push changes to `main` branch.
4. Tag the commit and push the changes to Github.
5. Github Actions will build the package from the sources and publish the package on Pypi
   once the tests pass.

Every commit pushed to `main` is also published on
[TestPyPI](https://test.pypi.org/project/gazu/) as a `.devN` version, `N`
being the short commit hash read as a number.

You can run `scripts/release.sh` to perform these commands at once. It bumps the patch version
by default (1.3.1 → 1.3.2); pass `minor` (→ 1.4.0) or `major` (→ 2.0.0) to bump another part:

```bash
scripts/release.sh minor
```

# Deployment

Please see the Zou documentation for the update instructions.
