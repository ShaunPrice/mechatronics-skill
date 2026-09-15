# Plugin distribution validation — v0.1.1

Checked 15 September 2026. Plugin version 0.1.1 bundles the unchanged skill version 0.1.0.

## Passed

- OpenAI bundled plugin-creator manifest/skill validator.
- Claude Code `plugin validate` on the compatibility manifest.
- Actual Codex app-server `plugin/read` against both the source repository marketplace and a freshly extracted marketplace ZIP: plugin `mechatronics-engineering@personal`, `localVersion: 0.1.1`, `availability: AVAILABLE`, one bundled skill `mechatronics-engineering:mechatronics-engineering`, and no MCP servers, hooks or apps.
- All 52 canonical skill files match the plugin copy and both archive layouts by SHA-256. The plugin contains 57 files including its manifests, README and MIT licence; the marketplace archive adds one catalog file.
- Duplicate builds produced identical release checksums. Archive CRC, duplicate-entry, relative-path and symlink checks passed.
- Package validator checked 273 local links, manifest identity, generated-copy parity and release checksums.
- 49 Python tests passed, including the available native Scilab check; 22 browser-core, 18 block-engine and 12 connector tests passed: 101 existing regression checks in total.
- Claude independently reviewed the official packaging/installation guidance and current skill structure. The review highlighted overlay precedence, complete Git contents, copy ordering, source/ZIP parity, version handling and installation-surface distinctions. These were incorporated. `codex plugin add` was verified against the installed CLI help; the saved web guide only documents the marketplace CLI and desktop installation flow.

## Evidence boundaries

The native plugin-reader result reported `installed: false` and `enabled: false`: discovery and metadata loading succeeded, but this validation did not install the plugin in the user's account. A listed bundled skill's `enabled: true` is its component setting, not proof that the containing plugin is installed.

The direct `codex plugin list --json` call without an explicit marketplace did not discover the unregistered test repository. The successful native check supplied its exact marketplace path. Users must register the GitHub/local marketplace or use the applicable desktop discovery flow before installing.

Hosted ChatGPT import, workspace publishing and universal public-directory submission have not been performed for this plugin. Existing standalone-skill installation and earlier simulation/hardware evidence remain distinct. Packaging does not install native engineering runtimes or validate physical hardware.

See [installation instructions](../docs/CHATGPT-PLUGIN.md) and the [existing engineering validation report](REPORT.md).
