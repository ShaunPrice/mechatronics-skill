# Mechatronics Engineering plugin

Plugin version **0.1.1**, containing the unchanged **0.1.0 skill**. MIT licensed. The package includes all 52 skill files: engineering references, Python calculations, browser workbench, block editor, OpenUSD export and Scilab/Xcos/ATOMS/ROS 2 interface templates.

## Install from GitHub in ChatGPT desktop / Codex

With the Codex CLI installed, run:

```sh
codex plugin marketplace add ShaunPrice/mechatronics-skill --ref v0.1.1
```

Restart the ChatGPT desktop app. In **Work** or **Codex**, open the **Plugins Directory**, select the **Personal** marketplace source, find **Mechatronics Engineering**, and select **Install**. Start a new conversation after installation.

The repository uses the plugin creator's default marketplace identifier, `personal`. If a marketplace with that identifier is already configured, inspect `codex plugin marketplace list` before adding this one; do not replace an unrelated catalog. The local-folder route below provides the same package for inspection or integration into your existing catalog.

On CLI versions offering `codex plugin add`, the installation step can also be run as:

```sh
codex plugin add mechatronics-engineering@personal
```

Check `codex plugin list --json` for the installed/enabled state. Marketplace registration, plugin installation, and successful use are separate checks. Commands do not require API keys or paid API billing.

## Download and install from a local folder

1. Download [mechatronics-marketplace-0.1.1.zip](https://github.com/ShaunPrice/mechatronics-skill/releases/download/v0.1.1/mechatronics-marketplace-0.1.1.zip) and extract it. It contains the catalog and complete plugin.
2. In a terminal, change into the extracted `mechatronics-marketplace` folder.
3. Run `codex plugin marketplace add .` and use the Plugins Directory installation step above.

For tooling that asks for just a plugin folder, download [mechatronics-engineering-plugin-0.1.1.zip](https://github.com/ShaunPrice/mechatronics-skill/releases/download/v0.1.1/mechatronics-engineering-plugin-0.1.1.zip) and extract it. Its `mechatronics-engineering` folder contains `plugin.json`, compatibility manifests, `skills/`, README and LICENSE. The plugin ZIP and the standalone `.skill` file have different layouts; choose the artifact requested by your installer.

## ChatGPT web and mobile

GitHub distribution does not automatically publish a plugin into ChatGPT's universal directory or upload it to your account. Local/repository marketplace availability varies by client. The documented GitHub installation route above is for supported desktop clients.

For workspace-wide access, a workspace admin can publish a locally added plugin using **Plugins → Personal → plugin menu → Publish**, then select eligible workspace roles, subject to workspace policy. Public-directory availability requires a separate OpenAI submission and approval. This repository has not been submitted to that directory.

If your web account exposes **Skills → Create → Upload from your computer**, you can use the [standalone .skill bundle](https://github.com/ShaunPrice/mechatronics-skill/releases/download/v0.1.0/mechatronics-engineering-0.1.0.skill). This installs the skill through that surface, rather than registering the plugin. A Project/custom GPT fallback is documented in the [installation guide](https://github.com/ShaunPrice/mechatronics-skill/blob/main/docs/INSTALL.md).

## Use and verify

In ChatGPT, type `@` and select **Mechatronics Engineering**. In Codex, use the skill picker; the plugin loader exposes the qualified skill name `$mechatronics-engineering:mechatronics-engineering`. If you have already installed the standalone skill, disable one copy if duplicate entries appear.

Try these prompts and check the actual output:

- **Teach and calculate:** “Use Mechatronics Engineering. Can a two-link arm with 0.3 m and 0.2 m links reach (0.6, 0) m?” Expected: unreachable; maximum reach is 0.5 m.
- **Build a simulation:** “Create a mass–spring–damper browser simulation with adjustable PID gains, live charts, and root-locus, Bode and Nyquist explanations.” Expected: runnable HTML/code with stated equations and model limits.
- **Build a diagram:** “Open the included block editor. Connect Constant → Gain → Scope and explain how to drag an OUT port onto an IN port.” With constant 3 and gain 2, expect scope output 6.
- **Check a boundary:** “Use the 3D arm animation to certify motor torque.” Expected: explain that kinematics alone cannot determine or certify torque; request masses, inertia, acceleration and load data.

The included workbench is at `skills/mechatronics-engineering/assets/browser-lab/index.html` inside the plugin. The block editor is `builder.html` in that same directory. Open the HTML files in a browser from an extracted package, or ask the assistant to generate downloadable standalone pages. Installing this plugin does not itself embed a persistent simulator panel in ChatGPT.

Calculations need Python; browser numerical tests need Node.js. Native Scilab, USD SDK and ROS 2 execution require their own environments. The plugin bundles instructions and source files; it does not install these runtimes or connect hardware. There are no bundled MCP servers, hooks, credentials, external service connections or telemetry.

## Updates, removal and package verification

This guide pins `v0.1.1` for repeatable installation. For a newer release, inspect its release notes and register the chosen ref explicitly; upgrading a catalog pinned to an old tag does not select a new version. Reinstall/refresh the plugin and start a new conversation. Preserve project-specific models and dossiers outside the installed plugin cache. Use the Plugins Directory to disable/remove the plugin, or `codex plugin remove mechatronics-engineering@personal` on supported CLI versions.

Compare downloaded files with the release's `SHA256SUMS`. In the source repository, run:

```sh
python3 scripts/build_packages.py
python3 scripts/validate_package.py
```

The builder regenerates the plugin's skill directory from canonical `skills/mechatronics-engineering/`; edit that canonical source. Validation checks source parity, manifest identity, archive contents, safe paths and release checksums. Packaging checks do not establish hosted account installation or hardware validation.

## Official documentation

Installation guidance checked on 15 September 2026 against [OpenAI plugin packaging and marketplaces](https://developers.openai.com/plugins/build/plugins), [plugin testing](https://developers.openai.com/plugins/deploy/connect-chatgpt), and [skill invocation](https://learn.chatgpt.com/docs/build-skills). UI labels and availability can change. [Source and licence](https://github.com/ShaunPrice/mechatronics-skill).
