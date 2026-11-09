# Validation record

Checked on 2026-11-09 using Python 3.12.14 on Linux.

| Check | Observed result |
| --- | --- |
| Standard-library unittest suite | 29 tests passed |
| Same suite with site packages disabled (`python -S`) | 29 tests passed |
| Editable install | Passed using installed setuptools 84.2.1, without index access |
| Installed `stack2rules --help` entry point | Passed |
| Next.js, Django and mixed-stack examples | All three matched committed output |
| Wheel build | Passed |
| Wheel metadata | No runtime dependencies; MIT license expression present |
| Bundled license | Matches the source LICENSE byte for byte |
| Clean virtual-environment wheel installation | Passed without dependency downloads |
| CLI from the installed wheel | Generated expected FastAPI and Pandas sections |

The GitHub Actions workflow targets Python 3.11–3.14 on Linux, macOS and
Windows. These hosted runs have not been executed during release preparation;
their results must be checked on the repository's Actions page. No tagged release,
PyPI publication, download count or external adoption is claimed.

CI action pins were verified against upstream release pages:

- [actions/checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)
- [actions/setup-python v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0)

The license text follows the [MIT license](https://opensource.org/license/mit).
