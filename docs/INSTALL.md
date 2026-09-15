# Install and verify

Installation guidance checked against official documentation on 15 September 2026. Interfaces, availability and workspace policies can change. These instructions do not imply that an account upload or global installation has already been performed.

## Get the private repository

Authenticate using an account with access, then clone:

```sh
git clone https://github.com/ShaunPrice/mechatronics-skill.git
cd mechatronics-skill
python3 scripts/build_packages.py
```

For prebuilt files, open the repository’s private Releases page while signed in and download the skill ZIP and both standalone HTML pages.

Alternatively use GitHub's authenticated **Code → Download ZIP**, extract it, and run the build command from that folder. The browser source runs immediately without building; packaging requires Python 3.9+. Never place an access token into a shared command, file or prompt.

## Claude web/Desktop: upload the skill

1. Build the packages, or use the supplied `mechatronics-engineering-0.1.0.zip`.
2. Open Claude's skill management interface (currently **Customize → Skills**) and choose the custom-skill upload/create option. Enable required skill/code-execution features if your workspace permits them.
3. Upload `dist/mechatronics-engineering-0.1.0.zip` and enable it. The ZIP has one top-level `mechatronics-engineering/` folder containing `SKILL.md`, references, assets, scripts and licence.
4. Start a conversation and ask: “Use Mechatronics Engineering to help me diagnose a motor that oscillates after stopping. Explain the terms and choose the first measurements.”
5. Confirm the response uses the skill and relevant references. Ask for a browser simulation and verify that actual code/files are produced. If script execution is unavailable, the text guidance remains useful, but do not assume calculations were run.

[Anthropic's custom-skill instructions](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) describe packaging and activation. A local filesystem copy alone does not establish availability in Claude web/Cowork.

## Claude Code: local skill folder

From the cloned repository, copy the **entire** skill folder to a personal or project skill directory. For a personal installation on macOS/Linux:

```sh
mkdir -p "$HOME/.claude/skills"
cp -R skills/mechatronics-engineering "$HOME/.claude/skills/"
```

For project-only use, create `.claude/skills/` inside that project and copy the folder there. On Windows, use the equivalent folder under your user profile or project; keep `SKILL.md` and resources together. Start a fresh Claude Code session and invoke `/mechatronics-engineering`, or ask a relevant task and check that it loads.

Inspect/back up an existing same-name installation before replacing it; copying over a newer version can leave stale files. Updating the repository does not update separately copied installations. [Claude Code documentation](https://code.claude.com/docs/en/skills) explains discovery and invocation.

## ChatGPT desktop / Codex: native local skill

For local Codex skill discovery, copy the folder to a personal or project `.agents/skills/` location. Personal macOS/Linux example:

```sh
mkdir -p "$HOME/.agents/skills"
cp -R skills/mechatronics-engineering "$HOME/.agents/skills/"
```

Restart or refresh the relevant session if it does not appear. In Codex invoke `$mechatronics-engineering`; ChatGPT surfaces with native skill selection may use `@`. Local installation does not by itself prove that the skill is available in web/mobile. Official documentation distinguishes standalone local skills from plugin-distributed skills across surfaces. This repository provides a standalone skill plus the hosted fallback below; it does not register a plugin in an account's directory. See [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills).

## Hosted ChatGPT: Project or custom GPT

This route uses explicit instructions plus reference files and does not depend on a native skill installer.

1. Open a ChatGPT Project or create a custom GPT in an account/workspace that supports it.
2. Paste `integrations/chatgpt/Instructions.txt` into its **Instructions** field/project instructions.
3. Upload these as project sources or GPT Knowledge:
   - `integrations/chatgpt/Mechatronics-knowledge.md`
   - `integrations/chatgpt/Browser-simulator-template.txt`
   - `integrations/chatgpt/Python-examples.txt`
   - `integrations/chatgpt/System-builder-template.txt`
4. Enable code execution/data analysis and browsing where available and desired. The guidance also works without them, with execution/current-source limits stated explicitly.
5. Test in Preview/a new project chat. Use the smoke tests below and ask for a downloadable browser simulator that you can open locally.

Instructions govern behaviour; Knowledge supplies reference material. A ZIP uploaded as Knowledge is not equivalent to installing/executing a native skill. If files cannot be read in your surface, attach the relevant text sections in the conversation instead. [OpenAI's GPT guide](https://help.openai.com/en/articles/8554397-creating-a-gpt) and [Projects guide](https://help.openai.com/en/articles/10169521-using-projects-in-chatgpt) explain these distinctions.

For a one-off chat, paste `Instructions.txt`, attach the relevant reference/template files, and explicitly ask the assistant to use them. Conversation context may need to be transferred when switching platforms; save the project dossier rather than assuming memory is shared.

## Native engineering tools

The browser pages run independently. For native analysis and middleware tests, follow the [Scilab/Xcos/ATOMS/ROS 2 interface guide](../skills/mechatronics-engineering/references/toolchain-interfaces.md) and [ROS 2 Docker instructions](../integrations/ros2-docker/README.md). The Docker environment builds a generated simulation package and tests its ROS topics; it does not require a physical robot.

## Smoke tests after installation

- “Explain why a 700 Hz signal sampled at 1 kHz can look like 300 Hz. What sensor settings must I check?” Expected: aliasing, units, internal sampling/decimation/output rates and a discriminating experiment.
- “Use 0.3 m and 0.2 m arm links to reach (0.6, 0) m.” Expected: unreachable target and a geometry/base/task decision.
- “Build a browser simulation of a mass–spring axis with editable gains, 2D/3D views, live charts and root locus/Bode/Nyquist explanations.” Expected: runnable files, equations and honest evidence/analysis limits.
- “Build a feedback diagram by dragging blocks, then explain how to detect an algebraic loop and test timestep convergence.” Expected: runnable builder/model, correct dependency/state explanation and real checks.
- “Export the arm animation to OpenUSD; can it size motors?” Expected: valid scene export with units/timing and a clear explanation of missing physical parameters.
- “Prepare this prototype for 100 units.” Expected: requirements, BOM/process/configuration/quality/cost and customer evidence; unknowns stay explicit.

Verify actual outputs, not only a statement that the skill loaded. Live hosted account imports and physical machine validation remain separate from the repository's code/document tests.

## Update or remove

Pull/download the new repository version, rebuild and validate, then replace the complete installed copy or uploaded skill/reference bundle. Preserve project-specific dossiers and configuration separately. To remove, disable/delete the uploaded skill or remove only its named local folder. No uninstall script changes account settings or unrelated files.
