# New project or foundation

Use for a new project or a deliberately chosen new foundation. For an existing project's overview or guide, use the [project guide](project-guide.md). A bare "set up a project" first establishes whether one already exists in Studio or elsewhere.

Flow: learn the needs, research, propose one setup, build it after review. Skip the review only when the user already approved a setup or asked you to just build it.

## Learn the needs

Use what the user and the project already say. Ask the unanswered questions that change the setup, in one to three short rounds:

- **Product:** a game and its main systems, several places, a plugin, a package, a prototype.
- **Authoring:** Studio or an external editor, language, who owns code and assets, existing content, collaborators, Git and CI.
- **Constraints:** networking, saved data, UI, testing, attitude to third-party libraries, deployment.

Decide routine details yourself to match the chosen direction. For a consequential choice the evidence doesn't settle, state the options with their deciding tradeoff, recommend one, and batch the questions. Honor earlier answers.

## Choose

Choose the authoring workflow from ownership first ([source of truth](placement.md#source-of-truth)), then the tools for the roles the project needs ([tooling](tooling.md)). Compare plausible candidates for each open role, including plain modules and built-in engine features, using current sources ([keeping current](keeping-current.md#claims-about-current-tools-and-platform)). No language, framework, loader or architecture is a default; [SSA](ssa.md) is for projects that deliberately adopt it. Researching a library doesn't authorize installing it.

## Propose

Show enough to review what will exist:

- the needs served, the chosen approach and its tradeoffs;
- roots, what is authored, generated or Studio-owned, and the filesystem-to-DataModel mapping;
- entrypoint paths, classes or `RunContext`s and startup owners; client/server and authority boundaries ([placement](placement.md));
- tools and libraries with versions, and how they restore;
- **the agent foundation, sized to the project** ([agent-ready project](../SKILL.md#an-agent-ready-project)): the guide's outline and `CLAUDE.md` pointer, the check command's steps, the guards the project's permanent or security rules need, hooks, CI if wanted, and how each verification rung is reached. A solo prototype might get a guide, a check command and a Stop hook; a team game with saved data gets all of it;
- Studio steps and owner actions, and remaining evidence gaps.

A plugin or package needs its host's or consumer's contract, not invented game bootstraps. Wait for review; the review doesn't reopen choices the user already settled.

## Build and verify

Build with the native tools. Keep restore separate from updates and authored source separate from generated output. Break-test each new check or guard once against a deliberately broken input. Run the check command and report static results separately from Studio results; name required checks you couldn't run. Material deviations from the reviewed setup go back for review.

Setup is done when the approved foundation is in place, startup has clear owners, and the check passes. Then offer a [fresh-agent trial](project-guide.md#trial-it-with-a-fresh-agent).
