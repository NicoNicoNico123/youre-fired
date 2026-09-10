# Speedrun: YOU'RE FIRED! 《鬥快被炒魷魚！》

A complete single-file **first-person** 3D physics-parody speedrun game, played like a
chaotic non-VR *Job Simulator*: you stand inside four ridiculous workplaces, grab things
with your own two hands, serve (or assault) walking customers, and push the
**BOSS RAGE METER** to **100%** as fast as possible. Any chaos counts — nothing is mandatory.

Built with **Three.js r160 + Rapier 3D (0.12.0, WASM)** — both pinned and loaded from jsDelivr.
All art is procedural Three.js primitives + CanvasTexture labels; all sound is synthesized
with the Web Audio API. No external images, models, fonts or audio files.

**The entire game lives in [`index.html`](index.html) (one file).**

---

## 1. Run locally

```bash
# from this folder — any ONE of these:
python3 -m http.server 8000
python  -m http.server 8000
npx serve .
```

Then open **http://localhost:8000**

> Do **not** open `file://index.html` for normal testing — ES-module/WASM security
> behaviour differs under `file://`, so use a static HTTP server.

The only network dependency is the two CDN modules, so the first load needs internet access.

## 2. Controls (first person)

**🖥️ Desktop**
- Click once to **lock the mouse**, then move the mouse to **look around**
- You play **from your station** — no walking; your hands reach anything you can see
- **Left-click** an object to grab it — it flies to your hands and floats in front of you
- **Flick the mouse and release** (left-click) to hurl it — the flick punches it forward along your aim
- **Right-click / E** = gentle place · **Mouse wheel** = reach closer / farther
- **R** (or the 🧲 RECALL button) = return props you threw too far back to their spots
- **Esc** releases the mouse (needed to click HUD / menus)

**📱 Mobile / Touch**
- **Hold and drag** empty space to look around
- **Tap an object** to grab it — it flies to your hands and floats in front of you
- **Flick and release** to throw it (swipe up while holding for extra loft)
- **Double-tap an object** to interact — ring the bell, answer the phone, stamp, smash…
- **Tap a customer** to hear their order chat
- **✋ PLACE** sets it down gently · **🧲 RECALL** brings far props back
- **⛶ Fullscreen** for edge-to-edge play · rotate to landscape for the widest view
- First launch shows a gesture card; haptic buzzes confirm grabs, throws and hits

**Never stuck:** props stranded beyond arm's reach automatically walk home after ~12
seconds, and 🧲 RECALL / `R` brings everything back instantly.

**Safety rails:** ☰ quit-to-menu and ↺ restart need a confirming second tap; every
finished run auto-saves to the device leaderboard when you leave the results screen
(💾 Submit still pins your rank). On phones the HUD re-stacks in portrait so the rage
meter is always readable, and `prefers-reduced-motion` disables shakes and flashes.

## 3. Test on a physical phone (same Wi-Fi)

1. Find your computer's LAN IP (do **not** guess it — read it):
   - Linux/macOS: `hostname -I` (first address) or `ip addr` / `ifconfig`
   - Windows: `ipconfig` → *IPv4 Address*
2. Start the server: `python3 -m http.server 8000`
3. Allow the port through your local firewall if prompted.
4. Connect the phone to the **same Wi-Fi** and open `http://<LAN-IP>:8000`
   (format only, e.g. `http://192.168.1.42:8000`).

## 4. Test with Chrome DevTools mobile emulation

1. Open the game in Chrome → **DevTools (F12)**
2. Toggle the **Device Toolbar** (`Ctrl/Cmd + Shift + M`)
3. Pick a phone preset (e.g. iPhone / Pixel) — touch emulation is on by default
4. Drag empty space to look, tap a prop to grab, flick to throw
5. Test **portrait**, then rotate to **landscape** (`Ctrl/Cmd + →`)

## 5. The Job-Sim loop

- **Customers walk up and order** things (🍔 fries, 📄 reports, 📝 contracts…) — the
  `📋 CUSTOMER ORDER` banner shows what they want; serve it on the counter/window pad
- **Serving wrong** (a boot, a bell, whatever is funnier) angers everyone and pays much more Rage
- Or just **throw the order at them** — head shots score most
- Machines are real: shredders eat, fryers sizzle, printers jam, trash swallows, the
  Level-4 exit door accepts "donations"
- **THE BOSS** — a tangerine-tanned, golden-swooped, long-red-tied caricature who wanders
  every workplace complaining in English and Cantonese ("Nobody fires people better than
  me!"). Reach 100% Rage and he storms up to your face, points, switches on the laser
  eyes, and delivers the meme: **YOU'RE FIRED! 你被炒咗啦！**

## 6. Speedrun modes

| Mode | What happens |
|---|---|
| **Full Any%** | All 4 stages back-to-back, one continuous timer, stage splits recorded — unlocks after all 4 levels are cleared |
| **Stage runs** | Pick Level 1–4 individually; its own timer and leaderboard |
| **Leaderboard** | Top-5 per mode, **stored locally on the device** (`localStorage`) — it is not online |

**Level lock:** a fresh save opens with Level 1 only. Push a workplace to 100% rage
(i.e. get fired) and the next one unlocks — progress is saved on the device.

**The crowd gets meaner as you climb:**

| Level | Customers | Behaviour |
|---|---|---|
| 1 — Office | 3 | Standing still — easy targets while you learn the throw |
| 2 — Diner | 2 extras | Strolling the dining area between bites |
| 3 — Call centre | 1 + the complainer | Pacing back and forth — **plus the HR Peacemaker** |
| 4 — Real estate | 1 + the client | Never stops weaving — the hardest target |

**Level 3 — beware the HR Peacemaker 😌:** a green-haloed HR colleague follows the boss
around and **cools him down −2.5 RAGE every 4 s** while he's in the building. Throw
something at him **3 times** and he grabs his box and sprints out (**HR KICKED OUT 🚀**,
+8 rage) — leave him alone and your meter will keep leaking.

Customers are prime rage fuel: hitting one enrages the boss about **1.3× more** than
hitting a colleague, and head shots score more than body shots.

Timer starts the instant a stage becomes interactive and stops the moment Rage hits 100%.
Times are `MM:SS.mmm` from `performance.now()`.

## 7. Four-point verification checklist

All four points are exercised by the automated harness in [`dev/e2e-test.mjs`](dev/e2e-test.mjs)
(80 checks against headless Chrome, including mobile touch emulation; final runs: **80/80 passing, 0 console errors**).

1. **WASM initialization** — ✅ Rapier `init()` completes, physics world + event queue are
   created before gameplay; failure path shows a readable error box instead of a blank screen.
2. **Pointer drag smoothness** — ✅ crosshair grab, carry, flick-throw, gentle place, walking,
   and touch-emulated grab/throw all verified; `pointercancel` and window blur release the
   object (no permanently stuck grabs).
3. **Boundary collider containment** — ✅ invisible walls + floor keep props (and you) inside
   the arena; props that fall out of the world are auto-respawned; the Level-4 exit door is
   the only intentional escape.
4. **localStorage persistence** — ✅ leaderboard entries survive a full page reload, top-5
   sorting works, separate boards per mode; storage-unavailable falls back to session-only.

## 8. Optional: run the automated test harness

```bash
cd dev
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install playwright@1.59.1
python3 -m http.server 8014 --directory ..   # in another terminal
node e2e-test.mjs                            # prints PASS/FAIL per check + screenshots
```

## 9. Deploy

Deploy the finished `index.html` directly to GitHub Pages or Cloudflare Pages with no build
step required — it is a static single file.

## Scene art and visual review

The four workplaces share rounded toy geometry, satin vinyl and ceramic finishes,
brushed-metal accents, procedural wood/tile/fabric surfaces, framed daylight windows,
wall trim, ceiling fixtures, and a reusable studio reflection map. Desktop uses 2048px
shadows and smoother geometry; mobile uses reduced geometry and existing blob shadows.
Character GLB colors and material finishes are preserved. Physics envelopes and objectives
remain defined by the existing colliders and sensors.

With the local HTTP server running, open `dev/scene-review.html` to compare workplaces.
Use `?level=0` through `?level=3`, append `&wide=1` for a room view, or `&clean=1` for
an uncluttered capture. `dev/scene-smoke.html` checks all stage loads, character visibility,
reload counts, mug grab/place/throw, and the shredder objective. Its final body attributes
are `data-complete="true"` and `data-passed="true"` when all checks pass.

The review and test pages load the actual game in an iframe; run them over HTTP.
