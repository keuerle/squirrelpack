# squirrelpack

A NeoForge 1.21.1 modpack, managed with [packwiz](https://packwiz.infra.link).
Mods **auto-sync on every launch** — when the pack updates, you get the changes the next time you start the game. You never manually download, update, or delete a mod.

- **Minecraft:** 1.21.1
- **Loader:** NeoForge 21.1.231
- Works the same on **Windows, macOS, and Linux**.

---

## Setup — the easy way (recommended)

Do this once. ~2 minutes.

1. **Install [Prism Launcher](https://prismlauncher.org)** and sign in with your Microsoft/Minecraft account (Prism downloads the right Java automatically — you don't need to install Java yourself).

2. **Download the instance:**
   https://github.com/keuerle/squirrelpack/raw/main/squirrelpack-prism-instance.zip

3. **Import it:** in Prism, click **Add Instance** → **Import from zip** → pick the file you just downloaded.
   *(Or skip the download: paste this URL into the "Import from zip" URL box —
   `https://raw.githubusercontent.com/keuerle/squirrelpack/main/squirrelpack-prism-instance.zip`)*

4. **Launch it.** The first launch installs NeoForge and downloads all the mods (a minute or two). Every launch after that just syncs any changes. Done.

That's everything. The instance already has the loader and the auto-sync set up — you don't touch any config.

---

## After setup

Just launch normally. Each launch re-syncs your mods to match the latest pack automatically. When the pack owner adds or updates a mod, you get it next launch (note: GitHub's file CDN can take a few minutes to serve a fresh change, so if you launch *seconds* after an update is announced, just launch once more).

---

## Setup — manual way (if the import doesn't work)

You need Prism Launcher and Java 21.

1. **Create the instance:** Prism → **Add Instance** → name it `squirrelpack` → choose **Minecraft 1.21.1**, then on the loader tab pick **NeoForge 21.1.231**.
2. **Add the bootstrap:** download `packwiz-installer-bootstrap.jar` from
   https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest ,
   then right-click the instance → **Folder**, open `.minecraft`, and drop the jar in there.
3. **Wire up auto-sync:** right-click the instance → **Edit** → **Settings** → check **Custom commands**, and in **Pre-launch command** paste:
   ```
   "$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/keuerle/squirrelpack/main/pack.toml
   ```
4. **Launch.**
