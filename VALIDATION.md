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

## Published release verification

The [release CI run](https://github.com/Shadowsama20/stack2rules/actions/runs/42645436441)
passed all 12 jobs on Python 3.11–3.14 across Linux, macOS and Windows,
including the PowerShell demo on Windows. The user also reported that the
interactive PowerShell test passed on their own PC; this is user-reported evidence.

The [release workflow](https://github.com/Shadowsama20/stack2rules/actions/runs/42645603396)
successfully built, verified and published v1.0.0 from commit
`a323fe8f01d8ebcefafe3938dacbd5d052c0ca25`. The tag points to that tested commit.
The release includes a wheel, source distribution and SHA256SUMS.txt.
PyPI publication succeeded on 2026-11-10 through Trusted Publishing.
A clean virtual environment installed version 1.0.0 directly from PyPI, with
hash verification. The CLI generated the expected mixed Python/Node rules,
preserved existing output, and declared no runtime dependencies. Both PyPI
asset hashes match the tested GitHub release. Download counts and external
adoption are not claimed.

[Successful publishing run](https://github.com/Shadowsama20/stack2rules/actions/runs/42646725605)

CI action pins were verified against upstream release pages:

- [actions/checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1)
- [actions/setup-python v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0)

The license text follows the [MIT license](https://opensource.org/license/mit).
