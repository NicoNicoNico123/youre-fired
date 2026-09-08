# ROLE

You are a senior browser-game engineer and autonomous coding agent specializing in:

* Three.js
* Rapier 3D physics
* browser-based 3D games
* mobile touch interaction
* physics sandbox gameplay
* game-state architecture
* procedural graphics
* Web Audio API
* performance optimization
* debugging and iterative testing

Your task is to autonomously design, implement, run, debug, test, and finish a complete browser game titled:

# Speedrun: YOU'RE FIRED!

## 《鬥快被炒魷魚！》

Do not stop after creating a prototype or vertical slice.

Continue fixing:

* runtime errors
* input problems
* physics instability
* incomplete levels
* broken interactions
* scoring exploits
* mobile usability issues
* reset bugs
* performance problems

until the acceptance criteria at the end of this specification are satisfied.

Do not leave:

* TODOs
* pseudocode
* placeholder functions
* unfinished levels
* omitted code
* unimplemented systems

If you are operating in a coding environment with filesystem/browser access, write and modify the actual files directly, run the game, inspect errors, and iteratively repair the implementation.

---

# 1. GAME CONCEPT

Build a complete responsive, non-VR, 3D physics-parody web game optimized for:

* Desktop Chrome
* Android Chrome
* modern mobile Chromium browsers
* mouse input
* single-touch input

The gameplay concept is:

> The player intentionally becomes the worst employee possible and tries to get fired as quickly as possible.

The player works through four ridiculous career stages.

Inside each stage, the player can freely:

* grab objects
* carry objects
* throw objects
* smash props
* knock things over
* misuse workplace equipment
* throw items at colleagues/customers
* create chain reactions
* discover ridiculous object combinations
* complete major sabotage actions

Every chaotic action can increase the:

# BOSS RAGE METER

The goal is to reach:

# 100% RAGE

as quickly as possible.

At 100%, trigger an exaggerated meme climax:

# YOU'RE FIRED!

## 你被炒咗啦！

The game should feel like a combination of:

* physics sandbox
* comedy workplace simulator
* speedrun challenge
* environmental interaction game
* slapstick chaos game

The experience should encourage the player to think:

> “What happens if I grab THIS and throw it THERE?”

rather than:

> “Which three fixed objectives do I need to complete?”

---

# 2. CORE DESIGN PHILOSOPHY

The game must NOT behave like a simple checklist puzzle.

Do not require players to complete exactly three predefined objectives in every level.

Instead:

* predefined sabotage objectives are high-value shortcuts
* ordinary sandbox interactions also generate Rage
* throwing props at NPCs generates Rage
* smashing and misusing objects generates Rage
* environmental chaos generates Rage
* chain reactions generate Rage
* secret combinations generate Rage
* the player may discover different routes to 100%

This allows players to develop their own speedrun strategies.

The same stage should support multiple valid ways of getting fired.

---

# 3. PRIMARY GAMEPLAY LOOP

The fundamental gameplay loop is:

**GRAB → MOVE → THROW / MISUSE / COLLIDE → NPC REACTS → GAIN RAGE → BUILD COMBO → CREATE MORE CHAOS**

The player wins the stage whenever:

`rage >= 100`

The player is NOT required to complete all major sabotage objectives.

---

# 4. TECH STACK

Create one primary artifact:

`index.html`

The final game must run directly from a simple static web server.

Use:

* HTML
* CSS
* JavaScript
* ES Modules
* Three.js
* `@dimforge/rapier3d-compat`
* Web Audio API

Use pinned mutually compatible versions.

Do NOT use unpinned imports such as:

`three@latest`

or:

`@dimforge/rapier3d-compat@latest`

The selected versions must be explicitly specified in the import URLs.

Preferred CDN sources:

* jsDelivr
* esm.sh

Do not use:

* build tools
* React
* Vue
* external game engines
* OrbitControls
* external image assets
* external models
* external sound files
* external fonts
* external textures

All game content must be generated procedurally.

---

# 5. SINGLE-FILE REQUIREMENT

The entire runnable game must exist inside:

`index.html`

Include in the same file:

* HTML structure
* CSS
* JavaScript
* shaders if used
* canvas-generated textures
* procedural audio logic

External dependencies are limited to CDN-loaded Three.js and Rapier modules.

Do not split required gameplay code into additional local JS/CSS files.

---

# 6. RAPIER INITIALIZATION

Rapier WASM must initialize before physics world creation.

Use behavior equivalent to:

`await RAPIER.init()`

Display a visible loading screen while dependencies initialize.

If initialization fails:

* log the actual technical error
* show a readable error message
* do not leave a blank screen

Only start the game after:

* Three.js is loaded
* Rapier initializes
* renderer is available
* physics world is created

---

# 7. RESPONSIVE VIEWPORT

The game should occupy the full browser viewport.

Use equivalent CSS behavior to:

* `margin: 0`
* `overflow: hidden`
* `touch-action: none`

Use viewport metadata including:

`user-scalable=no`

Prevent:

* page scrolling during gameplay
* text selection during dragging
* browser gesture conflicts where practical

Handle:

* resize
* portrait orientation
* landscape orientation
* browser toolbar resizing

Update:

* camera
* renderer
* HUD

correctly after resize.

---

# 8. MOBILE PERFORMANCE

Cap renderer pixel ratio:

`Math.min(window.devicePixelRatio, 2)`

Target:

Desktop:

* approximately 60 FPS

Mobile:

* approximately 30–60 FPS

Prefer:

* simple geometry
* reused materials
* reused geometry
* low-poly props
* limited dynamic bodies
* lightweight particles

Avoid:

* post-processing frameworks
* fluid simulation
* expensive reflections
* high-resolution shadow maps
* uncontrolled transparent particles
* excessive draw calls
* creating objects every frame

Temporary effects must clean themselves up.

---

# 9. CAMERA

Use a fixed approximately 45-degree isometric workplace perspective.

The player must NOT rotate or orbit the camera.

Do not use OrbitControls.

Normal touch/mouse gestures are reserved entirely for object interaction.

Camera movement is allowed only for:

* stage intro
* major impact shake
* YOU'RE FIRED climax
* stage transition

After temporary animation, restore the gameplay camera.

---

# 10. POINTER INPUT

Use one unified input system based on:

* `pointerdown`
* `pointermove`
* `pointerup`
* `pointercancel`

Use:

`setPointerCapture()`

where appropriate.

The same interaction system must support:

* mouse
* touch
* Chrome DevTools touch emulation

Do not build separate game logic for mouse and touch.

---

# 11. GRABBING SYSTEM

Most visually obvious props should be grabbable.

Only entities with the:

`grabbable`

trait may be picked up.

On pointer down:

1. raycast from camera through pointer position
2. locate nearest eligible grabbable entity
3. calculate/store grab offset
4. slightly lift object
5. begin physics-driven carry behavior

While held:

* project pointer onto a virtual horizontal interaction plane
* calculate a target world-space position
* drive the rigid body toward target using controlled velocity or impulses
* do not teleport the rigid body directly every frame
* preserve physical collisions
* clamp excessive velocity
* minimize clipping/tunneling
* allow objects to sweep other props off tables

On release:

* retain reasonable throwing velocity
* clear grab state
* restore standard physics behavior

Fast flick gestures must allow throwing.

---

# 12. MOBILE DEPTH INDICATOR

While an object is being carried, render a circular procedural shadow marker underneath it.

The marker should:

* align to the relevant desk/floor plane
* follow X/Z position
* remain visually lightweight
* fade when released

Use geometry/materials only.

No external texture.

This exists to help mobile players judge object depth.

---

# 13. PHYSICS

Use Rapier 3D for:

* rigid bodies
* gravity
* collisions
* sensors
* impact detection

Level surfaces should have appropriate static colliders.

Add invisible boundaries around normal gameplay areas.

Important objects should not immediately fall out of the stage.

Objects intentionally meant to leave the scene may be allowed through special exits.

Use sensible damping and mass values.

Avoid uncontrollable explosive physics.

---

# 14. ENTITY SYSTEM

Create a structured entity registry.

Each entity should be capable of containing:

* ID
* Three.js Object3D
* Rapier rigid body
* collider handles
* traits
* gameplay state
* metadata

Example traits:

* `grabbable`
* `throwable`
* `breakable`
* `hazard`
* `document`
* `food`
* `liquid_container`
* `socket_station`
* `objective_prop`
* `npc`
* `customer_property`
* `electronic`
* `trashable`
* `stampable`

Do not rely only on object names for behavior.

Example:

`entity.traits.has("grabbable")`

Keep rendering and physics references mapped cleanly.

---

# 15. SENSOR / SOCKET SYSTEM

Create semantic interaction zones using Rapier sensor colliders.

Examples:

* shredder mouth
* laptop keyboard
* printer
* trash bin
* fryer
* serving tray
* service window
* refund ticket area
* headset console
* contract stamping area
* doorway
* NPC hit zones

Enable collision events properly.

Use:

* sensor colliders
* Rapier EventQueue
* active collision events

Drain the EventQueue every physics step.

Map collider handles back to entities.

Do not use only arbitrary mesh-distance checks when a sensor is more appropriate.

---

# 16. GAME EVENT BUS

Implement a lightweight event bus.

Gameplay systems should broadcast events such as:

* `PROP_GRABBED`
* `PROP_RELEASED`
* `PROP_THROWN`
* `PROP_IMPACT`
* `PROP_BROKEN`
* `PROP_SABOTAGED`
* `SECRET_DISCOVERED`
* `COMBO_UPDATED`
* `RAGE_UPDATED`
* `NPC_HIT`
* `NPC_REACTION`
* `STAGE_COMPLETE`
* `GAME_OVER_FIRED`
* `RUN_COMPLETE`

Systems such as:

* HUD
* sound
* particles
* scoring
* NPC animation
* achievements

should subscribe independently where reasonable.

---

# 17. GAME STATE MACHINE

Use an explicit Game Director finite-state machine.

Recommended states:

`BOOT`

→ `INIT`

→ `MAIN_MENU`

→ `STAGE_INTRO`

→ `PLAYING`

→ `MEME_FREEZE`

→ `STAGE_RESULT`

→ `NEXT_STAGE`

→ `LEADERBOARD_SUBMIT`

Normal gameplay input must be disabled outside:

`PLAYING`

---

# 18. RAGE SYSTEM

Rage ranges from:

`0–100`

Stage ends when:

`rage >= 100`

Clamp displayed Rage at 100.

Rage can be generated from:

* prop impacts
* NPC impacts
* destruction
* equipment misuse
* environmental mess
* inappropriate object placement
* major sabotage objectives
* secret combinations
* chain reactions
* combo bonuses

Do not restrict Rage only to predefined objectives.

---

# 19. DYNAMIC THROW RAGE

NPCs must have physical interaction hit zones.

At minimum:

* head
* torso
* hands/general body

When a thrown object hits an NPC, calculate Rage using factors such as:

* object mass
* impact velocity
* hit location
* object type
* current combo
* repetition penalty

Conceptually:

`rageGain = clamp(baseImpact × massFactor × velocityFactor × hitZoneMultiplier × varietyMultiplier, min, max)`

Very weak accidental contacts should provide little or no Rage.

Head impacts may provide more Rage than torso impacts.

Keep the presentation cartoonish and slapstick.

Do not simulate gore or realistic injury.

NPCs should:

* wobble
* squash
* recoil
* shake
* look angry
* shield themselves
* complain

rather than showing realistic harm.

---

# 20. ANTI-SPAM / VARIETY SYSTEM

Do not allow the best strategy to become endlessly throwing one object at the NPC.

Repeated identical interactions should produce diminishing Rage.

Example:

First use:
100% reward

Second repeat:
70% reward

Third repeat:
40% reward

Further repeats:
minimal reward

Using:

* different objects
* different sockets
* different interaction categories
* new secret interactions

should maintain strong scoring.

Occasionally display:

`VARIETY BONUS!`

for using several different interactions rapidly.

---

# 21. CHAOS COMBO SYSTEM

Successful Rage-producing events occurring within approximately 2–3 seconds of one another should build a combo.

Examples:

`CHAOS x2`

`CHAOS x3`

`CHAOS x4`

`CHAOS x5`

The combo may modestly multiply Rage.

Physics-generated secondary events also count.

Example:

player throws coffee mug

→ mug knocks monitor

→ monitor falls into telephone

→ telephone falls into trash

Display something like:

# DESK DISASTER ×4!

Award additional Rage.

Reset combo after a short period without another qualifying event.

---

# 22. CHAIN-REACTION CREDIT

When practical, recognize physics-generated chain reactions.

Examples:

* thrown object knocks another object into NPC
* monitor knocks telephone off desk
* bottle pushes gift through exit
* object knocks another object into shredder
* one tray pushes another into service area

Credit the player who initiated the chain.

Avoid double-awarding the exact same event repeatedly.

---

# 23. OBJECTIVE SYSTEM

Each stage should contain several major sabotage opportunities.

These are:

* obvious
* funny
* high-value
* useful for speedruns

But they are NOT mandatory.

Players may combine:

* major objectives
* throwing
* environmental destruction
* secret interactions
* NPC hits
* combos

to reach 100%.

Major objectives should only award their full bonus once per stage run.

---

# 24. INTERACTIVE PROP DENSITY

Each stage should contain approximately:

15–25 interactive props

where performance permits.

Most obvious props should be grabbable.

Include a mixture of:

* important objective items
* clutter
* throwable props
* breakable props
* equipment
* funny props
* environmental tools
* hidden-combination props

Avoid presenting many objects that appear interactive but cannot be touched.

General rule:

> If the player reasonably expects to grab an object, make it grabbable unless there is a strong technical reason not to.

---

# 25. LEVEL 1 — OFFICE CLERK

## 辦公室文職 — 激死同事

Create a stylized office workspace.

Environment:

* desk
* laptop
* monitor
* keyboard
* shredder
* office plant
* telephone
* paperwork
* chair
* printer
* trash bin
* stationery
* nearby colleague NPC

Possible props:

* coffee mug
* stapler
* laptop
* keyboard
* monitor
* VIP contract
* paper sheets
* phone
* handset
* pen cup
* plant pot
* calculator
* mouse
* document folder
* desk organizer

Major sabotage actions:

### Coffee Disaster

Coffee mug interacts with laptop/keyboard.

Reward approximately:

`+20 to +30 Rage`

Effects:

* fake coffee splash particles
* sparks
* electrical buzzing
* keyboard visual damage
* NPC reaction

Actual fluid simulation is NOT required.

Treat liquid as scripted visual particles/state changes.

### VIP Contract Shredding

VIP contract enters shredder sensor.

Reward approximately:

`+20 to +30 Rage`

Effects:

* document feeds into shredder
* paper-strip particles
* shredder sound
* NPC rage escalation

### Phone Assault

Telephone/handset hits colleague above impact threshold.

Reward based partly on physics impact.

Suggested bonus:

`+10 to +20 Rage`

Possible sandbox actions:

* throw stapler at colleague
* throw coffee mug
* knock monitor over
* throw keyboard
* sweep desk clean
* throw documents everywhere
* throw office plant
* shred random documents
* shred ridiculous objects
* put telephone in trash
* knock laptop off desk
* throw calculator
* smash handset
* knock multiple objects down in one swipe

Secret interaction examples:

`Coffee + Printer → LATTE PRINTER`

`Stapler + Shredder → WHY WOULD YOU DO THAT?!`

`Plant Pot + NPC → OFFICE GARDENING`

`Entire Desk Swept Clean → CLEAN DESK POLICY`

---

# 26. LEVEL 2 — FAST FOOD COOK

## 快餐廚師 — 激死顧客

Create a fast-food counter environment.

Include:

* fryer
* service counter
* cash register
* trays
* food preparation area
* rubbish bin
* customer NPC
* condiment bottles

Props may include:

* dirty boot
* burger bun
* burger patty
* fries carton
* ketchup bottle
* mustard bottle
* serving tray
* cup
* extinguisher
* cash register
* food box
* spatula
* paper bag
* phone
* tongs

Major sabotage actions:

### Deep-Fried Boot

Boot enters fryer sensor.

State becomes:

`FRIED_BOOT`

Effects:

* bubbles
* smoke
* popping audio

Award initial Rage.

If fried boot is then placed onto the serving tray and served:

award additional Rage.

Total major reward approximately:

`+25 to +35 Rage`

### Empty Order

Serve an empty tray through the customer service sensor.

Reward approximately:

`+10 to +20 Rage`

### Extinguisher Chaos

Use/manipulate extinguisher across service area.

Generate procedural foam/smoke particles.

Reward approximately:

`+15 to +20 Rage`

Sandbox actions:

* throw burger at customer
* throw fries
* throw condiment bottles
* smash register
* put phone in fryer
* put random objects in fryer
* throw trays
* spill drinks
* serve rubbish
* throw food into trash
* ring service bell repeatedly
* knock meal onto floor
* launch burger across counter

Secret recipe examples:

`Boot + Bun + Ketchup → McDISASTER`

`Phone + Fryer → EXTRA CRISPY PHONE`

`Empty Tray + Ketchup Only → CHEF'S SPECIAL`

`Five Wrong Items in Fryer → HEALTH & SAFETY NIGHTMARE`

---

# 27. LEVEL 3 — CUSTOMER SERVICE

## 熱線客服 — 激死投訴王

Create a customer-service desk.

Include:

* hotline
* computer console
* headset
* refund documents
* stationery
* trash
* customer NPC

Props:

* ringing telephone
* handset
* refund claim
* REJECT stamp
* water cup
* headset
* keyboard
* monitor
* pen
* complaint papers
* trash bin
* office bell
* calculator

Major sabotage:

### Reject Refund

Bring REJECT stamp onto refund ticket.

Change ticket to display:

`REJECTED / 唔得`

Then place ticket in trash.

Reward approximately:

`+20 to +30 Rage`

### Destroy Hotline

Throw/smash handset or telephone above impact threshold.

Reward approximately:

`+15 to +25 Rage`

### Water Disaster

Water cup interacts with headset console.

Reward approximately:

`+15 to +25 Rage`

Effects:

* splash
* sparks
* static sound
* broken-console state

Sandbox actions:

* throw handset at customer
* stamp random paperwork
* stamp desk items
* throw claim in bin
* throw pen
* smash keyboard
* hang up repeatedly
* throw headset
* throw monitor
* hit ringing telephone
* throw paperwork everywhere

Secret examples:

`REJECT Stamp + NPC → CUSTOMER REJECTED`

`Complaint + Shredder/Trash → CASE RESOLVED`

`Telephone + Trash → CALL TERMINATED`

`Stamp 5 Random Props → ABSOLUTELY DENIED`

---

# 28. LEVEL 4 — SALES EXECUTIVE

## 業務銷售 — 激死大客與老闆

Create a luxury sales meeting environment.

Include:

* luxury desk
* sales documents
* POS terminal
* gift basket
* champagne
* premium displays
* exit doorway
* client NPC
* optional boss NPC or boss reaction indicator

Props:

* penthouse contract
* 99% OFF stamp
* champagne bottle
* glass
* POS machine
* VIP gift basket
* calculator
* luxury brochure
* model property
* credit card prop
* trophy
* pen
* folder

Major sabotage:

### 99% Discount

Stamp contract:

`99% OFF`

Display absurd price reduction.

Reward approximately:

`+20 to +30 Rage`

Example visual:

`$8,900,000`

becomes:

`$89,000`

NPC should react dramatically.

### Champagne POS Smash

Champagne bottle impacts POS terminal above threshold.

Reward approximately:

`+15 to +25 Rage`

Effects:

* cracked terminal visual
* sparks
* screen flicker
* impact sound

### Throw Away VIP Gift

Gift basket passes through exit-door sensor.

Reward approximately:

`+15 to +25 Rage`

Sandbox actions:

* throw champagne
* throw contract
* throw trophy
* smash POS
* throw calculator
* throw credit card
* throw property model
* pour champagne on paperwork
* give away random office items
* throw gift through exit
* knock luxury items onto floor

Secret examples:

`99% OFF + Trophy → EVERYTHING MUST GO`

`99% OFF + Gift Basket → FREE VIP PACKAGE`

`Champagne + Contract → LIQUID ASSET`

`Property Model Through Door → REAL ESTATE EXIT`

---

# 29. NPC SYSTEM

Each stage must include at least one procedural low-poly NPC.

Build NPC from simple Three.js geometry.

Include:

* head
* eyes
* eyebrows
* mouth
* torso
* simple hands/arms if practical

NPC must contain interaction hit zones.

NPC emotional states:

0–20 Rage:
calm

21–40:
annoyed

41–60:
angry

61–80:
furious

81–99:
extreme rage

100:
YOU'RE FIRED climax

As Rage rises:

* skin becomes redder
* eyebrows rotate inward
* eyes widen
* head shaking increases
* mouth expression changes
* body reacts more aggressively

NPC should visually respond immediately after:

* being hit
* seeing sabotage
* equipment being destroyed
* secret interactions

---

# 30. NPC DIALOGUE

Spawn temporary speech bubbles.

Include Cantonese and English lines.

Examples:

* 「你做緊乜嘢？！」
* 「痴線㗎你！」
* 「你係咪玩嘢呀？！」
* 「叫你經理出嚟！」
* 「搞咩呀你？！」
* 「你仲做緊乜呀？！」
* “WHAT ARE YOU DOING?!”
* “ARE YOU SERIOUS?!”
* “STOP THAT!”
* “GET YOUR MANAGER!”
* “WHAT IS WRONG WITH YOU?!”

Dialogue should:

* appear briefly
* not block gameplay
* be selected with some variety
* become more aggressive as Rage increases

---

# 31. NPC PHYSICS REACTIONS

NPC hits should remain comedic rather than realistic.

Possible responses:

* head recoil
* wobble
* squash/stretch
* short spin
* flinch
* shield face
* shake fist
* duck
* stare at offending object

Use lightweight animation rather than full ragdoll simulation unless performance remains excellent.

---

# 32. MAJOR EVENT FEEDBACK

Each meaningful sabotage should produce appropriate feedback.

Possible feedback:

* floating Rage value
* particles
* sound
* camera shake
* NPC animation
* dialogue
* HUD flash

Examples:

`+6% RAGE`

`CHAOS x4`

`WHY WOULD YOU DO THAT?!`

`CUSTOMER REJECTED!`

`OFFICE DISASTER!`

---

# 33. SECRET INTERACTIONS

Each level should include approximately 3–6 hidden humorous combinations.

Do not list all secrets to the player.

When discovered:

* show a named bonus
* award bonus Rage
* play special feedback
* optionally record discovery during current session

Examples:

* weird object in fryer
* wrong object in shredder
* stamp NPC
* throw luxury gift away
* mix ridiculous fast-food recipe
* pour coffee into printer

The game should reward experimentation.

---

# 34. ACHIEVEMENT-LIKE MOMENTS

Optional lightweight achievements may appear during gameplay.

These do NOT need to be permanently stored unless easy to implement.

Examples:

### CLEAN DESK POLICY

Knock most desk props onto the floor.

### CUSTOMER IS ALWAYS RIGHT

Hit customer with five different objects.

### PAPERLESS OFFICE

Destroy or discard all documents.

### HEALTH & SAFETY NIGHTMARE

Put five inappropriate items into fryer.

### ABSOLUTELY DENIED

Stamp five unrelated objects.

### FIVE-SECOND EMPLOYEE

Reach high Rage extremely quickly.

### I QUIT ANYWAY

Throw many objects through exit.

These should add humor and exploration.

---

# 35. YOU'RE FIRED CLIMAX

Immediately when Rage reaches 100:

1. stop stage timer
2. stop normal gameplay input
3. freeze/pause active physics
4. perform strong camera shake
5. crash zoom toward NPC
6. flash screen red
7. turn NPC eyes glowing red
8. optionally add stylized laser-eye beams
9. display giant tilted text:

# YOU'RE FIRED!

and:

# 你被炒咗啦！

10. play synthesized bass-impact sound
11. briefly freeze the scene
12. transition to results screen

The meme sound must be generated procedurally.

Do not use copyrighted Vine Boom audio files.

Create an original Web Audio bass hit inspired by meme impact timing.

---

# 36. AUDIO

Use Web Audio API only.

No external audio files.

Initialize/resume audio after first user interaction because mobile browsers may block autoplay.

Synthesized sounds should include equivalents for:

* phone ring
* thud
* smash
* electric buzz
* sparks
* shredder
* fryer popping
* stamp
* register beep
* static
* buzzer
* bass impact
* UI click

Add:

* mute toggle
* master volume

If Web Audio fails, gameplay must continue silently.

---

# 37. CAMERA SHAKE

Strong impacts may produce lightweight camera shake.

Shake magnitude should depend on event strength.

Do not make the game difficult to control.

Reduce/exclude shake for minor collisions.

Return camera exactly to intended gameplay transform afterward.

---

# 38. PARTICLES

Use lightweight procedural particles.

Examples:

* paper strips
* sparks
* smoke
* bubbles
* foam
* coffee drops
* dust

Keep particle counts controlled.

Clean temporary effects automatically.

Do not use real fluid simulation.

---

# 39. SPEEDRUN MODES

Implement:

## Individual Stage Mode

Player chooses one level.

Timer starts the moment gameplay becomes interactive.

Timer ends when Rage reaches 100.

Save stage time.

## Full Any% Mode

Player begins Level 1.

Automatically continue:

Level 1 → Level 2 → Level 3 → Level 4

Full timer begins when Level 1 becomes interactive.

Do NOT reset total timer between levels.

Record stage split times.

Final timer ends at Level 4 Rage 100.

---

# 40. TIMER

Use:

`performance.now()`

Do not rely on timer accumulation from `setInterval()`.

Display:

`MM:SS.mmm`

Stop final recorded timing immediately when the winning condition occurs.

Menu/result time must not affect final result.

---

# 41. LOCAL LEADERBOARD

The leaderboard is LOCAL-DEVICE ONLY.

Do not implement a backend.

Use:

`localStorage`

Store Top 5 fastest times for:

* Full Any%
* Level 1
* Level 2
* Level 3
* Level 4

Each entry:

* 3-character arcade name
* raw milliseconds
* formatted time
* date

Sort fastest first.

Keep only five entries.

Validate names.

Permit:

* A–Z
* 0–9

Handle localStorage being unavailable gracefully.

Do not describe this leaderboard as globally online.

---

# 42. RESULTS SCREEN

After a stage:

display:

* completion time
* personal best indicator
* Rage reached
* optional chaos stats
* 3-character name entry
* Submit
* Try Again
* Level Select
* Leaderboard

For Full Any%:

also show:

* Level 1 split
* Level 2 split
* Level 3 split
* Level 4 split
* total time

---

# 43. OPTIONAL CHAOS STATISTICS

If practical, display fun statistics after a run:

* props thrown
* NPC hits
* objects destroyed
* biggest impact
* highest combo
* secrets found
* desk items knocked over

These should not block completion if implementation complexity becomes excessive.

---

# 44. HUD

During play display:

* stage name
* career title
* speedrun timer
* Boss Rage Meter
* current Rage %
* current combo
* optional major sabotage hints
* mute
* restart

Keep interface readable on phones.

Avoid covering central interaction space.

---

# 45. OBJECTIVE HINTS

Major sabotage objectives can be shown as optional suggestions.

Example:

`Suggested Chaos:`

* Ruin the laptop
* Destroy the contract
* Weaponize the phone

Do NOT make these appear mandatory.

Use wording such as:

`Suggested Chaos`

rather than:

`Required Objectives`

The player should understand:

> Any chaos that reaches 100% Rage wins.

---

# 46. MAIN MENU

Provide buttons for:

* Full Any% Speedrun
* Level 1 — Office Clerk
* Level 2 — Fast Food Cook
* Level 3 — Customer Service
* Level 4 — Sales Executive
* Leaderboards
* How to Play

---

# 47. HOW TO PLAY

Explain:

Desktop:

* click and hold an object
* drag to move
* flick and release to throw

Mobile:

* touch and hold an object
* drag to move
* flick and release to throw

Also explain:

* make NPCs angry
* destroy/misuse workplace props
* discover secret combinations
* reach 100% Rage as quickly as possible

---

# 48. RESET SYSTEM

Restarting a level must fully reset:

* physics bodies
* collider states
* prop transforms
* linear velocities
* angular velocities
* broken states
* sensor state
* objective flags
* secret triggers
* repetition counters
* combo
* Rage
* NPC appearance
* NPC animation
* particles
* timer
* speech bubbles
* grab state
* active pointer state

Repeated restarts must not duplicate:

* rigid bodies
* event listeners
* timers
* animation loops

---

# 49. PHYSICS SAFETY

Prevent important gameplay objects from becoming permanently inaccessible.

Possible strategies:

* invisible stage boundaries
* reasonable walls
* floor recovery threshold
* respawn objects if they fall far below the map

Do not interfere with special mechanics such as:

* throwing gift basket through exit

If an important object becomes unrecoverable accidentally, safely respawn it after a short delay.

---

# 50. IMPACT DETECTION

Use relative velocity and/or impulse information where available.

Do not count every tiny collider contact as sabotage.

Define sensible thresholds for:

* normal contact
* meaningful hit
* strong hit
* smash event

Large/high-speed objects should generally produce stronger reactions.

Clamp maximum Rage from a single generic impact to prevent accidental instant wins.

---

# 51. SCRIPTED LIQUIDS

For:

* coffee
* water
* champagne
* extinguisher foam

do not simulate actual fluid physics.

Use semantic triggers plus:

* particles
* decals/state changes
* audio

Example:

If coffee mug is near keyboard and the mug is tilted sufficiently or impacts keyboard:

trigger:

`COFFEE_KEYBOARD`

once.

---

# 52. BREAKABLE OBJECTS

Some props may visually break.

Examples:

* POS terminal
* monitor
* telephone
* glass
* keyboard

Use lightweight techniques:

* switch geometry state
* change material
* add crack texture through CanvasTexture
* detach simple fragments

Do not implement expensive fracture simulation.

---

# 53. PROCEDURAL ART STYLE

Use a consistent stylized low-poly aesthetic.

Suggested visual style:

* bright workplace colors
* chunky furniture
* rounded/simple props
* exaggerated NPC faces
* readable silhouettes
* arcade/meme tone

Use Three.js primitives such as:

* BoxGeometry
* SphereGeometry
* Capsule/Cylinder geometry
* PlaneGeometry
* simple extrusions where needed

Generate labels/signage using CanvasTexture.

Examples:

* REJECTED
* 99% OFF
* VIP CONTRACT
* FRYER
* TRASH
* YOU'RE FIRED

---

# 54. DEVELOPMENT PROCEDURE

Work incrementally.

Recommended order:

1. create index.html
2. initialize imports
3. initialize Rapier
4. establish Three.js renderer
5. create physics step loop
6. build camera/lights
7. implement entity registry
8. implement grab/throw system
9. implement collision/event mapping
10. implement sensors
11. implement Rage scoring
12. implement NPC
13. implement Level 1
14. test Level 1 completely
15. implement combo system
16. implement anti-spam system
17. implement secrets
18. implement Levels 2–4
19. implement audio
20. implement climax
21. implement timer/speedrun modes
22. implement menus
23. implement leaderboard
24. test resets
25. optimize mobile
26. final verification

Do not unnecessarily rewrite systems that already work.

When an error occurs:

1. inspect the actual runtime error
2. determine root cause
3. patch the smallest relevant system
4. rerun
5. verify
6. continue

---

# 55. TESTING — BOOTSTRAP

Verify:

* Three.js loads
* Rapier loads
* WASM initialization succeeds
* physics world exists
* renderer displays
* update loop runs
* no blank screen appears

---

# 56. TESTING — POINTER

Verify:

Desktop:

* pickup
* dragging
* release
* throwing

Touch emulation:

* pickup
* dragging
* release
* flick throwing

Verify pointer cancellation does not leave an object permanently grabbed.

---

# 57. TESTING — PHYSICS

Verify:

* objects collide naturally
* objects can knock other props around
* important objects stay accessible
* objects do not tunnel excessively
* static surfaces contain props
* intended exits work

---

# 58. TESTING — NPC IMPACTS

Verify:

* weak touch does not generate excessive Rage
* meaningful impacts generate Rage
* head/torso zones behave correctly
* repeat interactions diminish
* different props restore variety scoring

---

# 59. TESTING — COMBOS

Verify:

* consecutive qualifying events increase combo
* combo times out
* chain reactions can increase combo
* combo multipliers remain bounded
* no infinite Rage exploit exists

---

# 60. TESTING — EVERY LEVEL

Trigger every major sabotage action in all four stages.

Confirm:

* correct event fires
* Rage changes
* VFX plays
* audio plays
* NPC reacts
* objective cannot grant its full major bonus multiple times

Also verify players can reach 100 Rage without necessarily completing all major sabotage objectives.

---

# 61. TESTING — CLIMAX

Verify Rage reaching 100:

* stops timer
* disables normal input
* freezes physics
* performs camera sequence
* displays YOU'RE FIRED
* displays Chinese subtitle
* plays impact audio
* proceeds to result screen

Trigger only once.

---

# 62. TESTING — FULL ANY%

Complete all four stages sequentially.

Verify:

* total timer is continuous
* stage splits record correctly
* total ends at final Level 4 completion
* transitions do not duplicate systems

---

# 63. TESTING — STORAGE

Submit leaderboard score.

Reload page.

Verify:

* score persists
* Top 5 sorting works
* separate level boards work
* Full Any% board works

---

# 64. TESTING — RESET

Restart every level repeatedly.

Verify no:

* duplicate rigid bodies
* duplicate sensors
* duplicate audio triggers
* duplicate event listeners
* duplicated Rage awards
* stale held objects
* stuck pointers

---

# 65. LOCAL DEPLOYMENT

Provide these commands.

Python:

`python3 -m http.server 8000`

Alternative:

`python -m http.server 8000`

Node:

`npx serve .`

Explain that `file://index.html` should not be used for normal testing because module/WASM security behavior can differ.

Open:

`http://localhost:8000`

---

# 66. PHYSICAL MOBILE TESTING

For a phone on the same local network:

1. determine the computer LAN IP
2. start HTTP server
3. ensure local firewall permits the port
4. connect phone to same Wi-Fi
5. open:

`http://<LAN-IP>:8000`

Example format only:

`http://192.168.x.x:8000`

Do not hardcode an assumed LAN IP.

---

# 67. CHROME DEVTOOLS TESTING

Explain:

1. open Chrome DevTools
2. enable Device Toolbar
3. choose a phone preset
4. enable touch emulation
5. test portrait
6. test landscape
7. test drag and flick gestures

---

# 68. FOUR-POINT FINAL VERIFICATION CHECKLIST

The final documentation must include this checklist:

### 1. WASM Initialization

Confirm Rapier initializes successfully without uncaught errors.

### 2. Pointer Drag Smoothness

Confirm mouse and touch dragging/throwing are responsive.

### 3. Boundary Collider Containment

Confirm gameplay props remain within intended level bounds unless intentionally thrown through an exit.

### 4. localStorage Persistence

Confirm leaderboard scores remain after refresh/reload.

---

# 69. PRODUCTION DEPLOYMENT

Include one concise sentence explaining that the finished `index.html` may be deployed directly to:

* GitHub Pages
* Cloudflare Pages

with no build step required.

---

# 70. ACCEPTANCE CRITERIA

The project is NOT complete until all of the following are true:

* `index.html` runs through a local HTTP server
* Three.js loads
* Rapier initializes
* no blank startup screen
* all four career stages are playable
* each stage contains a physics sandbox
* most visually obvious props are interactable
* props can be grabbed
* props can be carried
* props can be thrown
* physics interactions work with mouse
* physics interactions work with touch
* objects collide with other props
* objects can hit NPCs
* meaningful NPC hits generate Rage
* impact scoring uses physics strength
* repeated interactions have diminishing returns
* variety is rewarded
* combo system works
* chain reactions can be rewarded
* major sabotage objectives work
* major sabotage actions cannot be infinitely farmed
* secret interactions exist
* each level can reach 100 Rage in multiple ways
* players are not forced to complete every major objective
* NPC emotional escalation works
* NPC dialogue appears
* NPC reacts physically to impacts
* Rage HUD works
* timer works
* individual stage speedruns work
* Full Any% works
* splits work
* YOU'RE FIRED climax works
* audio is procedural
* no external art assets are used
* no external audio assets are used
* leaderboard persists locally
* score sorting works
* Try Again works
* level selection works
* repeated resets do not duplicate systems
* mobile layout is usable
* performance remains practical
* there are no TODO placeholders
* no required code is omitted
* no uncaught console error occurs during standard gameplay testing

---

# 71. FINAL DELIVERABLES

Deliver:

1. complete production-ready `index.html`
2. local-server commands
3. physical mobile LAN testing instructions
4. Chrome DevTools mobile testing instructions
5. four-point verification checklist
6. one-sentence GitHub Pages / Cloudflare Pages deployment guide

Do not output abbreviated code.

Do not write:

* “rest omitted”
* “same as above”
* “implement other stages similarly”
* “TODO”
* “placeholder”
* “for brevity”

If filesystem access exists, create and update the real `index.html` directly instead of merely describing it.

Run the implementation and fix errors before declaring completion.

The final experience should feel like a small but complete physics workplace sandbox where the player can freely interact with the scene, invent ridiculous ways to annoy customers and colleagues, create chaotic combinations, and optimize the fastest route to getting fired.
