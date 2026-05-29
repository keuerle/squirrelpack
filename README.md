# squirrelpack

A NeoForge 1.21.1 modpack, managed with [packwiz](https://packwiz.infra.link).
Mods auto-sync on every launch — when the pack updates, you get the changes the next time you start the game.

- **Minecraft:** 1.21.1
- **Loader:** NeoForge 21.1.231
- **Manifest URL:** `https://raw.githubusercontent.com/keuerle/squirrelpack/main/pack.toml`

---

## First-time setup (do this once)

You need [Prism Launcher](https://prismlauncher.org) and Java 21.

1. **Create the instance**
   - In Prism: **Add Instance** → name it `squirrelpack`.
   - Choose **Minecraft 1.21.1**, then on the loader tab pick **NeoForge** version **21.1.231**.
   - Click OK to create it.

2. **Add the auto-sync bootstrap**
   - Download `packwiz-installer-bootstrap.jar` from
     https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest
   - Right-click the instance → **Folder** to open it, then go into the `.minecraft` folder.
   - Drop `packwiz-installer-bootstrap.jar` into that `.minecraft` folder.

3. **Wire it up as a pre-launch command**
   - Right-click the instance → **Edit** → **Settings** → check **Custom commands**.
   - In **Pre-launch command**, paste:
     ```
     "$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/keuerle/squirrelpack/main/pack.toml
     ```

4. **Launch.** The first launch downloads all the mods (takes a minute). Done.

## After that

Just launch the game normally. Every launch re-syncs your mods to match the latest
pack, so you never manually download, update, or delete a mod again.
