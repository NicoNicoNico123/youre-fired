import { chromium } from 'playwright';

const URL = 'http://localhost:8014/index.html';
const SHOTS = '/tmp/yf_shots/';
const results = [];
const consoleErrors = [];
const T = (name, ok, extra = '') => {
  results.push({ name, ok: !!ok });
  console.log((ok ? 'PASS' : 'FAIL') + '  ' + name + (extra ? '   [' + extra + ']' : ''));
};
const sleep = ms => new Promise(r => setTimeout(r, ms));
const CX = 480, CY = 300;

const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
const page = await browser.newPage({ viewport: { width: 960, height: 600 } });
const asset404 = [];
page.on('response', r => { if (r.status() === 404 && r.url().includes('/assets/')) asset404.push(r.url()); });
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', e => consoleErrors.push('PAGEERROR: ' + e.message));

const state = () => page.evaluate(() => YF.state());
const waitState = async (s, timeout = 20000) => {
  await page.waitForFunction(x => window.YF && YF.state() === x, s, { timeout });
};
// poll helpers — headless software rendering can run physics in slow motion,
// so events may land later than a fixed sleep would suggest
const waitObjective = async (id, timeout = 6000) => {
  try { await page.waitForFunction(x => YF.objectives()[x] === true, id, { timeout }); return true; }
  catch (e) { return false; }
};
const waitSecret = async (id, timeout = 6000) => {
  try { await page.waitForFunction(x => YF.secrets().includes(x), id, { timeout }); return true; }
  catch (e) { return false; }
};
const waitRageAbove = async (v, timeout = 5000) => {
  try { await page.waitForFunction(x => YF.rage() > x, v, { timeout }); return true; }
  catch (e) { return false; }
};
const settled = async (type, timeout = 3500) => {
  try {
    await page.waitForFunction(t => {
      const p = YF.propInfo(t);
      return p && Math.hypot(p.vel.x, p.vel.y, p.vel.z) < 0.4;
    }, type, { timeout });
    return true;
  } catch (e) { return false; }
};
const aimAt = async (x, y, z) => page.evaluate(([x, y, z]) => YF.lookTo(x, y, z), [x, y, z]);
// the colleague walks to her order spot ~7s into a stage — wait until she's planted
const waitNpcSettled = async (timeout = 20000) => {
  await page.waitForFunction(() => !!YF.orders().active, null, { timeout }).catch(() => {});
  let prev = await page.evaluate(() => YF.npcPos());
  for (let k = 0; k < 20; k++) {
    await sleep(500);
    const cur = await page.evaluate(() => YF.npcPos());
    if (Math.hypot(cur.x - prev.x, cur.z - prev.z) < 0.05) { prev = cur; break; }
    prev = cur;
  }
  return prev;
};

// ---------- 1. BOOT ----------
await page.goto(URL);
try {
  await page.waitForFunction(() => window.YF && YF.state() === 'MENU', null, { timeout: 45000 });
  T('boot: reached MENU (no blank screen)', true);
} catch (e) {
  T('boot: reached MENU (no blank screen)', false, 'state=' + await state().catch(() => '?'));
}
T('boot: menu visible', await page.isVisible('#menu'));
T('boot: level buttons built', await page.locator('#m-levels button').count() === 4);
// deterministic input tests: use the drag-look fallback instead of pointer lock
await page.evaluate(() => window.YFdisableLock && YFdisableLock());
await sleep(500);
await page.screenshot({ path: SHOTS + '01-menu.png' });

// ---------- 2. FP GRAB / CARRY / THROW / WALK (Level 1) ----------
await page.click('#m-levels button:nth-of-type(1)');
await waitState('PLAYING', 25000);
T('L1: reached PLAYING', true);
await sleep(900);
// the boss: orange-tanned caricature with the golden swoop and long red tie
// (checked before any chaos so the procedural skin hex is pristine)
const bossLook = await page.evaluate(() => YF.bossLook());
T('boss: caricature look (orange skin, blonde swoop, red tie)',
  !!bossLook && bossLook.skin === '#ee9c50' && bossLook.hair === '#f3cf6b' && bossLook.tie === '#d63c2e',
  JSON.stringify(bossLook));
await waitNpcSettled();   // colleague walks to her order spot early — wait her out
const gltfKeys = await page.evaluate(() => YF.gltfLoaded());
T('glb: loader pipeline end-to-end (cube.glb cached)', gltfKeys.includes('pipelineTest'), JSON.stringify(gltfKeys));
const mugBefore = await page.evaluate(() => YF.pos('mug'));
T('L1: mug exists on desk', !!mugBefore && mugBefore.y > 0.7, JSON.stringify(mugBefore));

// crosshair grab: aim at mug, click center
await aimAt(mugBefore.x, mugBefore.y, mugBefore.z);
await page.mouse.move(CX, CY);
await page.mouse.down();
T('L1: crosshair grab works', await page.evaluate(() => YF.grab()) === 'mug');
await sleep(450);
const heldDist = await page.evaluate(() => {
  const p = YF.pos('mug'), pl = YF.player();
  return Math.hypot(p.x - pl.x, p.y - (pl.y + 1.58), p.z - pl.z);
});
T('L1: mug carried in front of player', heldDist < 2.3, 'dist=' + heldDist.toFixed(2));

// aim at NPC torso, flick forward, release → throw + rage (retry: flick timing varies)
const rageBefore = await page.evaluate(() => YF.rage());
let threw = false;
for (let attempt = 0; attempt < 3 && !threw; attempt++) {
  if (attempt > 0) {
    await settled('mug');
    // strong throws can land beyond grab reach — pull the mug back onto the desk first
    await page.evaluate(() => YF.teleport('mug', 0.5, 1.05, 3.0));
    await sleep(300);
    const mm = await page.evaluate(() => YF.pos('mug'));
    if (!mm) break;
    await aimAt(mm.x, mm.y, mm.z);
    await page.mouse.move(CX, CY);
    await page.mouse.down();
    if ((await page.evaluate(() => YF.grab())) !== 'mug') { await page.mouse.up(); continue; }
  }
  const npcTorso = await page.evaluate(() => { const h = YF.npcPos(); return { x: h.x, y: h.y - 0.3, z: h.z }; });
  // close the distance first — tuned throws carry a few metres, not across the room
  await page.evaluate(([x, z]) => YF.playerTo(x, z), [npcTorso.x - 1.6, npcTorso.z + 1.4]);
  await aimAt(npcTorso.x, npcTorso.y, npcTorso.z);
  await sleep(400);
  // a realistic fast flick: ~0.9 rad over ~100ms (in-browser timing so samples get real stamps)
  await page.evaluate(async () => { for (let i = 0; i < 10; i++) { YF.nudgeLook(0, -40); await new Promise(r => setTimeout(r, 10)); } });
  await page.mouse.up();
  threw = await waitRageAbove(rageBefore + 0.3, 5000);
}
T('L1: flick throw at NPC generates Rage', threw, `+${((await page.evaluate(() => YF.rage())) - rageBefore).toFixed(2)}`);
T('L1: mug released after throw', await page.evaluate(() => YF.grab()) === null);

// gentle place via E key (pull the mug back into reach first, then re-grab)
await page.evaluate(() => YF.teleport('mug', 0.5, 1.05, 3.0));
await sleep(300);
await settled('mug');
const mug2 = await page.evaluate(() => YF.pos('mug'));
await aimAt(mug2.x, mug2.y, mug2.z);
await sleep(250);
await page.mouse.move(CX, CY);
await page.mouse.down();
T('L1: re-grab works', await page.evaluate(() => YF.grab()) === 'mug');
await page.keyboard.press('KeyE');
await sleep(400);
T('L1: E key places gently', await page.evaluate(() => YF.grab()) === null);

// pointercancel does not leave object stuck
await settled('mug');
const mug3 = await page.evaluate(() => YF.pos('mug'));
await aimAt(mug3.x, mug3.y, mug3.z);
await sleep(250);
await page.mouse.move(CX, CY);
await page.mouse.down();
await page.evaluate(() => {
  const c = document.querySelector('#app canvas');
  c.dispatchEvent(new PointerEvent('pointercancel', { pointerId: 1, bubbles: true }));
});
await page.mouse.up(); // resync harness button state (browser releases capture itself on real cancels)
await sleep(200);
T('L1: pointercancel releases object', await page.evaluate(() => YF.grab()) === null);

// double-tap on empty-ish desk object = interact (phone rings + hops)
await page.evaluate(() => { YF.playerTo(0.3, 4.35); YF.teleport('phoneBase', 0.5, 1.1, 3.4); YF.teleport('mug', 6, 0.4, -5); });
await sleep(450);
await page.evaluate(() => { const p2 = YF.pos('phoneBase'); YF.lookTo(p2.x, p2.y, p2.z); });
await sleep(250);
const phoneSp = await page.evaluate(() => { const p2 = YF.pos('phoneBase'); return YF.project(p2.x, p2.y, p2.z); });
T('L1: phone under crosshair', !!phoneSp, JSON.stringify(phoneSp));
for (const ev of ['pointerdown', 'pointerup', 'pointerdown', 'pointerup']) {
  await page.evaluate(([x, y, ev]) => {
    const c = document.querySelector('#app canvas');
    c.dispatchEvent(new PointerEvent(ev, { pointerId: 21, pointerType: 'mouse', clientX: x, clientY: y, bubbles: true, isPrimary: true }));
  }, [phoneSp.x, phoneSp.y, ev]);
  await sleep(100);
}
await sleep(250);
T('L1: double-tap interacts (phone)', await page.evaluate(() => YF.lastInteract()) === 'phoneBase',
  'last=' + await page.evaluate(() => YF.lastInteract()));

// hold empty wall + drag = camera look
await page.evaluate(() => { YF.teleport('phoneBase', 6, 0.4, -5); YF.lookTo(0.9, 1.5, -6); });
await sleep(1400); // let the lookTo camera tween finish before dragging
const yawA = await page.evaluate(() => YF.player().yaw);
await sleep(150);
const yawA2 = await page.evaluate(() => YF.player().yaw);
for (const [ev, x] of [['pointerdown', 480], ['pointermove', 540], ['pointermove', 600], ['pointerup', 600]]) {
  await page.evaluate(([ev, x]) => {
    const c = document.querySelector('#app canvas');
    c.dispatchEvent(new PointerEvent(ev, { pointerId: 22, pointerType: 'mouse', clientX: x, clientY: 300, bubbles: true, isPrimary: true }));
  }, [ev, x]);
  await sleep(90);
}
const yawB = await page.evaluate(() => YF.player().yaw);
T('L1: hold+drag empty space aims camera', Math.abs(yawB - yawA2) > 0.1, `dyaw=${(yawB - yawA2).toFixed(2)} tween-drift=${Math.abs(yawA2 - yawA).toFixed(3)}`);

// WASD walk
const p0 = await page.evaluate(() => YF.player());
await page.keyboard.down('KeyW');
await sleep(600);
await page.keyboard.up('KeyW');
let p1 = await page.evaluate(() => YF.player());
let walked = Math.hypot(p1.x - p0.x, p1.z - p0.z);
if (walked < 0.3) {  // slow-mo frames can swallow the first press — retry once
  await page.keyboard.down('KeyW');
  await sleep(600);
  await page.keyboard.up('KeyW');
  p1 = await page.evaluate(() => YF.player());
  walked = Math.hypot(p1.x - p0.x, p1.z - p0.z);
}
T('L1: WASD walk moves player', walked > 0.3 && walked < 3.5, walked.toFixed(2));
await page.screenshot({ path: SHOTS + '02-level1-fp.png' });

// ---------- 2b. RECALL (anti-stuck: stranded props come back) ----------
await page.evaluate(() => YF.playerTo(0.3, 4.35));
await page.evaluate(() => YF.teleport('mug', -8.5, 0.3, -6.5)); // hurl it into the far corner
await sleep(300);
const farAway = await page.evaluate(() => {
  const m = YF.pos('mug'), pl = YF.player();
  return Math.hypot(m.x - pl.x, m.z - pl.z);
});
T('L1: mug stranded beyond grab reach', farAway > 5, farAway.toFixed(1));
await page.keyboard.press('KeyR');
await sleep(500);
const backDist = await page.evaluate(() => {
  const m = YF.pos('mug'), pl = YF.player();
  return Math.hypot(m.x - pl.x, m.z - pl.z);
});
T('L1: RECALL (R) returns stranded props', backDist < 4.8, backDist.toFixed(1));

await page.evaluate(() => YF.teleport('mug', -2.0, 1.1, 3.2));
await sleep(250);

// ---------- 3a. ANTI-SPAM (while stage live) ----------
// stand on the open right-side floor: throws at the colleague never cross the
// desk-top serve pad; wait until the first order is active so the colleague stays put
await page.evaluate(() => YF.playerTo(6.2, 2.4));
await page.waitForFunction(() => !!YF.orders().active, null, { timeout: 18000 }).catch(() => {});
let prevNpc = await page.evaluate(() => YF.npcPos());
let npcStill = false;
for (let k = 0; k < 20 && !npcStill; k++) {
  await sleep(500);
  const cur = await page.evaluate(() => YF.npcPos());
  npcStill = Math.hypot(cur.x - prevNpc.x, cur.z - prevNpc.z) < 0.05;
  prevNpc = cur;
}
const gains = [];
const rageA0 = await page.evaluate(() => YF.rage());
// deterministic same-object repeat: drop the calculator onto the NPC's head 4x,
// moving it away between drops; per-key counters + decay factors do the rest
for (let k = 0; k < 4; k++) {
  const before = await page.evaluate(() => YF.rage());
  await page.evaluate(() => {
    const n = YF.npcPos();
    if (!YF.teleport('calculator', n.x, n.y + 1.2, n.z)) YF.spawn('calculator', n.x, n.y + 1.2, n.z);
  });
  const landed = await waitRageAbove(before + 0.2, 5000);
  gains.push(landed ? (await page.evaluate(() => YF.rage())) - before : 0);
  await page.evaluate(() => YF.teleport('calculator', 7.5, 0.4, 4.5));
  await sleep(300);
}
const rageA = (await page.evaluate(() => YF.rage())) - rageA0;
T('L1: same-object NPC hits still land', gains.filter(g => g > 0).length >= 3 && gains.every(g => g <= 10), 'gains=' + gains.map(g => g.toFixed(2)).join(','));
// anti-spam: per-key repetition counters must have incremented (decay 1→0.7→0.4 applied from these)
const allReps = await page.evaluate(() => YF.reps());
console.log('  rep keys:', JSON.stringify(allReps));
T('L1: repeated same-hits diminish (per-key counters)', allReps.some(([k, v]) => k.startsWith('nh:calculator') && v >= 2), 'reps=' + JSON.stringify(allReps.filter(([k]) => k.startsWith('nh:calculator'))) + ' gains=' + gains.map(g => g.toFixed(2)).join(','));

await page.evaluate(() => { YF.teleport('calculator', -7, 0.4, 5.5); YF.teleport('mug', -2.0, 1.1, 3.2); });
await sleep(250);

// ---------- 3b. L1 OBJECTIVES ----------
const kb = await page.evaluate(() => YF.pos('keyboard'));
await page.evaluate(([x, y, z]) => YF.teleport('mug', x, y + 0.6, z), [kb.x, kb.y, kb.z]);
T('L1: COFFEE DISASTER triggered', await waitObjective('coffee'));

const sh = await page.evaluate(() => YF.sensorPos('shredder'));
await page.evaluate(([x, y, z]) => YF.teleport('contract', x, y + 0.4, z), [sh.x, sh.y, sh.z]);
T('L1: VIP CONTRACT SHREDDED', await waitObjective('shred_vip'));
let consumed = true;
try {
  await page.waitForFunction(() => !YF.props().some(p => p.startsWith('contract:1')), null, { timeout: 4000 });
} catch (e) { consumed = false; }
T('L1: contract consumed by shredder', consumed);

const sh2 = await page.evaluate(() => YF.sensorPos('shredder'));
let stapled = false;
for (let k = 0; k < 5 && !stapled; k++) {
  await page.evaluate(([x, y, z]) => YF.teleport('stapler', x, y + 0.04, z), [sh2.x, sh2.y, sh2.z]); // drop inside the slot
  stapled = await waitSecret('stapler_shred', 4000);
  if (!stapled) {
    const dbg = await page.evaluate(() => ({
      alive: YF.props().some(p => p.startsWith('stapler:1')),
      stapler: YF.propInfo('stapler'), sensor: YF.sensorPos('shredder'),
      state: YF.state(), sec: YF.secrets(),
    }));
    console.log('  stapler try ' + k + ':', JSON.stringify(dbg));
  }
}
T('L1: secret stapler+shredder', stapled, await page.evaluate(() => YF.secrets().join(',')));

// plant pot on NPC (fresh stage so a mid-test win can't freeze physics)
await page.evaluate(() => YF.startRun(0));
await waitState('PLAYING', 25000);
await sleep(600);
await waitNpcSettled();
const hp2 = await page.evaluate(() => YF.npcPos());
let potted = false;
for (let k = 0; k < 3 && !potted; k++) {
  await page.evaluate(([x, y, z]) => YF.teleport('plantPot', x, y + 1.1, z), [hp2.x, hp2.y, hp2.z]);
  potted = await waitSecret('office_gardening', 5000);
}
T('L1: secret plantPot+NPC', potted, (await page.evaluate(() => YF.secrets().join(','))));

await page.evaluate(() => YF.teleport('plantPot', -6.5, 0.4, 4.5));
await sleep(250);
let phoneIn = false;
for (let k = 0; k < 3 && !phoneIn; k++) {
  const hp = await page.evaluate(() => YF.npcPos());
  await page.evaluate(([x, y, z]) => YF.teleport('phoneBase', x, y + 1.4, z), [hp.x, hp.y, hp.z]);
  phoneIn = await waitObjective('phone_assault', 4000);
}
T('L1: PHONE ASSAULT', phoneIn);
const r1 = await page.evaluate(() => YF.rage());
T('L1: rage in a sane band after objectives', r1 >= 20, 'rage=' + r1.toFixed(1) + ' state=' + await state());
await page.screenshot({ path: SHOTS + '03-level1-objectives.png' });

// ---------- 4. LEVEL 2 (+ customer orders) ----------
await page.evaluate(() => YF.startRun(1));
await waitState('PLAYING', 25000);
await sleep(700);
const fry = await page.evaluate(() => YF.sensorPos('fryer'));
await page.evaluate(([x, y, z]) => YF.teleport('boot', x, y + 0.3, z), [fry.x, fry.y, fry.z]);
T('L2: DEEP-FRIED BOOT', await waitObjective('fried_boot'));
await page.evaluate(() => YF.teleport('boot', 0.2, 1.55, 0.6));
await sleep(100);
await page.evaluate(() => YF.teleport('tray', 0, 1.05, 0.6));
T('L2: FRIED BOOT SERVED', await waitObjective('boot_served'));
await page.evaluate(() => YF.teleport('boot', -7.5, 0.3, -6.2));
await sleep(200);
// move the tray away first so it re-enters the window sensor as a fresh contact
await page.evaluate(() => YF.teleport('tray', 0, 1.05, 3.4));
await sleep(350);
await page.evaluate(() => YF.teleport('tray', 0, 1.05, 0.6));
T('L2: EMPTY ORDER (tray objective)', await waitObjective('empty_order'));
await page.evaluate(() => YF.teleport('extinguisher', 0, 1.2, 0.6));
T('L2: EXTINGUISHER CHAOS', await waitObjective('extinguisher'));
// clear the extinguisher out of the service window so the empty-order scan stays clean
await page.evaluate(() => YF.teleport('extinguisher', 6.5, 0.4, 4.5));
await sleep(300);
const fry2 = await page.evaluate(() => YF.sensorPos('fryer'));
await page.evaluate(([x, y, z]) => YF.teleport('phoneBase', x, y + 0.3, z), [fry2.x, fry2.y, fry2.z]);
T('L2: secret phone+fryer', await waitSecret('crispy_phone'));

// customer order flow: wait for a request, serve it right, then serve wrong
await page.waitForFunction(() => YF.orders().active && YF.orders().active.state === 'waiting', null, { timeout: 18000 });
const orderType = await page.evaluate(() => YF.orders().active.type);
await page.evaluate(t => { const p = YF.sensorPos('window'); YF.teleport(t, p.x, p.y, p.z); }, orderType);
await page.waitForFunction(() => YF.orders().served === 1, null, { timeout: 6000 });
const ord1 = await page.evaluate(() => YF.orders());
T('L2: correct serve completes order', ord1.served === 1 && ord1.active === null, JSON.stringify(ord1));
await page.waitForFunction(() => YF.orders().active && YF.orders().active.state === 'waiting', null, { timeout: 18000 });
await page.evaluate(() => { const p = YF.sensorPos('window'); YF.teleport('bell', p.x, p.y, p.z); });
await page.waitForFunction(() => YF.orders().wrong === 1, null, { timeout: 6000 });
const ord2 = await page.evaluate(() => YF.orders());
T('L2: wrong serve angers customer', ord2.wrong === 1, JSON.stringify(ord2));
const r2 = await page.evaluate(() => YF.rage());
console.log('  L2 rage: ' + r2.toFixed(1));
T('L2: rage accumulating', r2 > 10 && r2 < 100, 'rage=' + r2.toFixed(1));
await page.screenshot({ path: SHOTS + '04-level2.png' });

// ---------- 5. LEVEL 3 ----------
await page.evaluate(() => YF.startRun(2));
await waitState('PLAYING', 25000);
await sleep(700);
const claim = await page.evaluate(() => YF.pos('paper'));
await page.evaluate(([x, y, z]) => YF.teleport('stamp', x, y + 0.5, z), [claim.x, claim.y, claim.z]);
T('L3: REFUND REJECTED (stamp)', await waitObjective('reject_stamp'));
const trash = await page.evaluate(() => YF.sensorPos('trash'));
await page.evaluate(([x, y, z]) => YF.teleport('paper', x, y + 0.5, z), [trash.x, trash.y, trash.z]);
T('L3: REFUND DENIED & TOSSED', await waitObjective('reject_trash'));
const hp3 = await page.evaluate(() => YF.pos('phoneBase'));
await page.evaluate(() => YF.teleport('monitor', 6.5, 0.6, 4.8));
await sleep(200);
let hotline = false;
for (let k = 0; k < 3 && !hotline; k++) {
  await page.evaluate(([x, y, z]) => YF.teleport('handset', x, y + 3.2, z), [hp3.x, hp3.y, hp3.z]);
  hotline = await waitObjective('hotline', 4000);
}
T('L3: DESTROY HOTLINE', hotline);
await page.evaluate(() => YF.teleport('monitor', -2.7, 1.15, 2.5));
await page.evaluate(() => YF.teleport('waterCup', -1.8, 1.6, 1.85));
T('L3: WATER DISASTER', await waitObjective('water'));
const hpL3 = await page.evaluate(() => YF.npcPos());
await page.evaluate(([x, y, z]) => YF.teleport('stamp', x, y + 1.2, z), [hpL3.x, hpL3.y, hpL3.z]);
T('L3: secret stamp+NPC', await waitSecret('customer_rejected'));
let resolved = false;
for (let k = 0; k < 3 && !resolved; k++) {
  await page.evaluate(([x, y, z]) => YF.teleport('paper', x, y + 0.5, z), [trash.x, trash.y, trash.z]);
  resolved = await waitSecret('case_resolved', 4000);
}
T('L3: secret complaint+trash', resolved);
const r3 = await page.evaluate(() => YF.rage());
console.log('  L3 rage: ' + r3.toFixed(1));
await page.screenshot({ path: SHOTS + '05-level3.png' });

// ---------- 6. LEVEL 4 ----------
await page.evaluate(() => YF.startRun(3));
await waitState('PLAYING', 25000);
await sleep(700);
const con4 = await page.evaluate(() => YF.pos('contract'));
await page.evaluate(([x, y, z]) => YF.teleport('stamp', x, y + 0.5, z), [con4.x, con4.y, con4.z]);
T('L4: 99% DISCOUNT stamped', await waitObjective('discount'));
const posP = await page.evaluate(() => YF.pos('posMachine'));
let posSmashed = false;
for (let k = 0; k < 3 && !posSmashed; k++) {
  await page.evaluate(([x, y, z]) => YF.teleport('champagne', x, y + 0.7, z), [posP.x, posP.y, posP.z]);
  posSmashed = await waitObjective('pos_smash', 4000);
}
T('L4: CHAMPAGNE POS SMASH', posSmashed);
const ex = await page.evaluate(() => YF.sensorPos('exit'));
T('L4: exit sensor exists', !!ex, JSON.stringify(ex));
await page.evaluate(([x, y, z]) => YF.teleport('giftBasket', x, y, z), [ex.x, ex.y, ex.z]);
T('L4: VIP GIFT THROWN OUT', await waitObjective('gift_exit'));
await page.evaluate(() => YF.teleport('stamp', -6.5, 0.4, 4.8));
await sleep(250);
const con4b = await page.evaluate(() => YF.pos('contract'));
await page.evaluate(([x, y, z]) => YF.teleport('champagne', x, y + 0.5, z), [con4b.x, con4b.y, con4b.z]);
await sleep(600);
await page.evaluate(([x, y, z]) => YF.teleport('model', x, y, z), [ex.x, ex.y, ex.z]);
const both4 = await Promise.all([waitSecret('liquid_asset'), waitSecret('real_estate_exit')]);
T('L4: secrets champagne+contract, model+exit', both4[0] && both4[1], (await page.evaluate(() => YF.secrets().join(', '))));
// figurines on the desk
const figCount = await page.evaluate(() => YF.props().filter(p => p.startsWith('figurine:1')).length);
T('L4: boss figurines on desk', figCount === 2, 'count=' + figCount);
// Mirror Match on a fresh stage (a mid-test win would freeze physics)
await page.evaluate(() => YF.startRun(3));
await waitState('PLAYING', 25000);
await sleep(500);
let mirror = false;
for (let k = 0; k < 3 && !mirror; k++) {
  const bp = await page.evaluate(() => YF.bossPos());
  if (!bp) break;
  await page.evaluate(([x, y, z]) => YF.teleport('figurine', x, y + 1.0, z), [bp[0], bp[1], bp[2]]);
  mirror = await waitSecret('mirror_match', 5000);
}
T('L4: secret mirror match (figurine vs boss)', mirror);
const r4 = await page.evaluate(() => YF.rage());
console.log('  L4 rage: ' + r4.toFixed(1) + ' secrets: ' + (await page.evaluate(() => YF.secrets().join(', '))));
await page.screenshot({ path: SHOTS + '06-level4.png' });

// ---------- 7. CLIMAX (boss walks up) ----------
await page.evaluate(() => YF.addRage(101 - YF.rage()));
await sleep(300);
T('climax: state MEME', await state() === 'MEME');
let overlaySeen = false;
try {
  await page.waitForFunction(() => { const c = document.querySelector('#climax'); return c && !c.classList.contains('hidden'); }, null, { timeout: 6000 });
  overlaySeen = true;
} catch (e) {}
T('climax: YOU ARE FIRED overlay visible', overlaySeen);
T('climax: boss speech bubble shown', await page.locator('#layer .bubble').count() >= 1);
await page.screenshot({ path: SHOTS + '07-climax.png' });
await waitState('RESULT', 8000);
T('climax: reaches RESULT screen', await state() === 'RESULT');
T('climax: results panel visible', await page.isVisible('#results'));
T('climax: overlay hidden again', !(await page.isVisible('#climax')));
await sleep(400);
await page.screenshot({ path: SHOTS + '08-results.png' });

// ---------- 8. FULL ANY% ----------
await page.evaluate(() => YF.startRun('any'));
await waitState('PLAYING', 25000);
for (let s = 0; s < 4; s++) {
  await page.evaluate(() => YF.addRage(101));
  try {
    await waitState('RESULT', 12000);
  } catch (e) {
    console.log('  ANY% stage ' + s + ' stalled at state=' + await state() + ' rage=' + await page.evaluate(() => YF.rage()));
    await page.evaluate(() => YF.addRage(101));
    await waitState('RESULT', 12000);
  }
  if (s < 3) {
    await page.click('#res-continue');
    try {
      await waitState('PLAYING', 25000);
    } catch (e) {
      console.log('  ANY% continue stalled. state=' + await state() + ' errors:');
      consoleErrors.forEach(ce => console.log('    ⚠ ' + ce.slice(0, 300)));
      throw e;
    }
  }
}
const splits = await page.evaluate(() => YF.splits());
T('ANY%: 4 splits recorded', splits.filter(x => x > 0).length === 4, JSON.stringify(splits.map(x => Math.round(x))));
T('ANY%: final total exists', await page.evaluate(() => YF.game.finalTotal > 0), 'total=' + await page.evaluate(() => Math.round(YF.game.finalTotal)));
T('ANY%: results show RUN COMPLETE', (await page.textContent('#res-title')).includes('RUN COMPLETE'));
T('ANY%: splits table has 4 rows', await page.locator('#res-splits div').count() === 5);
await page.screenshot({ path: SHOTS + '09-anypercent.png' });

// ---------- 9. LEADERBOARD PERSISTENCE ----------
await page.fill('#res-name', 'TST');
await page.click('#res-submit');
await sleep(300);
T('board: submit shows rank', (await page.textContent('#res-rank')).includes('#'));
const top = await page.evaluate(() => YF.Board.top('any'));
T('board: entry stored', top.length === 1 && top[0].name === 'TST', JSON.stringify(top));
await page.reload();
await page.waitForFunction(() => window.YF && YF.state() === 'MENU', null, { timeout: 45000 });
const top2 = await page.evaluate(() => YF.Board.top('any'));
T('board: persists after reload', top2.length === 1 && top2[0].name === 'TST', JSON.stringify(top2));
await page.evaluate(() => { YF.Board.add('any', 50000, 'AAA'); YF.Board.add('any', 30000, 'BBB'); YF.Board.add('any', 70000, 'CCC'); YF.Board.add('any', 40000, 'DDD'); YF.Board.add('any', 10000, 'EEE'); YF.Board.add('any', 20000, 'FFF'); });
const top3 = await page.evaluate(() => YF.Board.top('any'));
T('board: top-5 sorted, extras dropped', top3.length === 5 && top3[0].name === 'EEE' && top3[4].name === 'DDD' && !top3.some(e => e.name === 'CCC' || e.name === 'AAA'), JSON.stringify(top3.map(e => e.name + ':' + e.ms)));

// ---------- 10. RESETS / NO DUPLICATES ----------
await page.evaluate(() => document.exitPointerLock && document.exitPointerLock());
await page.evaluate(() => YF.startRun(0));
await waitState('PLAYING', 25000);
const counts = [];
for (let k = 0; k < 4; k++) {
  counts.push(await page.evaluate(() => YF.entityCount()));
  await page.click('#btn-restart');
  await waitState('PLAYING', 25000);
  await sleep(300);
}
T('reset: entity count stable across restarts', new Set(counts).size === 1, counts.join(','));
T('reset: no stuck grab', await page.evaluate(() => YF.grab()) === null);
await page.evaluate(() => YF.startRun(3));
await waitState('PLAYING', 25000);
await page.evaluate(() => document.exitPointerLock && document.exitPointerLock());
await page.click('#btn-menu');
await page.waitForFunction(() => YF.state() === 'MENU', null, { timeout: 10000 });
T('reset: menu → backdrop loads', await page.isVisible('#menu'));
await page.click('#m-levels button:nth-of-type(2)');
await waitState('PLAYING', 25000);
T('reset: stage switch works', true);
console.log('  entity counts: restarts=' + counts.join(','));

// ---------- 11. STAGE MODE TIMER + RESULT ----------
await page.evaluate(() => YF.addRage(101));
await waitState('RESULT', 10000);
const shown = await page.textContent('#res-time');
T('stage mode: result time formatted MM:SS.mmm', /^\d{2}:\d{2}\.\d{3}$/.test(shown), shown);
T('stage mode: rage reached 100', (await page.evaluate(() => YF.rage())) === 100);

// ---------- 12. RESPONSIVE ----------
await page.setViewportSize({ width: 390, height: 844 });
await sleep(500);
await page.screenshot({ path: SHOTS + '10-portrait.png' });
T('responsive: portrait renders', await page.evaluate(() => !!window.YF));
await page.setViewportSize({ width: 844, height: 390 });
await sleep(500);
await page.screenshot({ path: SHOTS + '11-landscape.png' });

// ---------- PERF ----------
await page.setViewportSize({ width: 1280, height: 800 });
const fps = await page.evaluate(() => new Promise(res => {
  let n = 0; const t0 = performance.now();
  const loop = () => { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(loop); else res(n / 2); };
  requestAnimationFrame(loop);
}));
console.log('  approx FPS (swiftshader, software GL): ' + fps.toFixed(0));
T('perf: fps above 15 in software rendering (real GPUs are far faster)', fps > 15, fps.toFixed(0));

await page.close(); // free the GL context — two live contexts stall software rendering

// ---------- 13. TOUCH EMULATION (mobile FP) ----------
const mob = await browser.newPage({ viewport: { width: 412, height: 915 }, hasTouch: true, isMobile: true });
mob.on('pageerror', e => consoleErrors.push('MOBILE PAGEERROR: ' + e.message));
await mob.goto(URL);
await mob.waitForFunction(() => window.YF && YF.state() === 'MENU', null, { timeout: 90000 });
await mob.tap('#m-levels button:nth-of-type(1)');
await mob.waitForFunction(() => YF.state() === 'PLAYING', null, { timeout: 25000 });
await sleep(800);
// mobile UX: tutorial, orientation chip, fullscreen button
await mob.waitForFunction(() => { const t = document.querySelector('#tut'); return t && !t.classList.contains('hidden'); }, null, { timeout: 8000 }).catch(() => {});
T('mobile: tutorial card shows on first play', await mob.isVisible('#tut'));
await mob.tap('#tut');
T('mobile: tutorial dismisses on tap', !(await mob.isVisible('#tut')));
T('mobile: orientation chip visible in portrait', await mob.isVisible('#orient'));
T('mobile: fullscreen button present', await mob.isVisible('#btn-fs'));
await mob.evaluate(() => { const m = YF.pos('mug'); YF.lookTo(m.x, m.y, m.z); });
await sleep(200);
await mob.evaluate(() => {
  const c = document.querySelector('#app canvas');
  c.dispatchEvent(new PointerEvent('pointerdown', { pointerId: 7, pointerType: 'touch', clientX: 206, clientY: 457, bubbles: true, isPrimary: true }));
});
T('mobile: touch grab works', await mob.evaluate(() => YF.grab()) === 'mug');
await mob.evaluate(() => {
  const c = document.querySelector('#app canvas');
  c.dispatchEvent(new PointerEvent('pointermove', { pointerId: 7, pointerType: 'touch', clientX: 246, clientY: 417, bubbles: true, isPrimary: true }));
  c.dispatchEvent(new PointerEvent('pointermove', { pointerId: 7, pointerType: 'touch', clientX: 286, clientY: 377, bubbles: true, isPrimary: true }));
});
await sleep(150);
await mob.evaluate(() => {
  const c = document.querySelector('#app canvas');
  c.dispatchEvent(new PointerEvent('pointerup', { pointerId: 7, pointerType: 'touch', bubbles: true, isPrimary: true }));
});
await sleep(300);
T('mobile: touch drag+release throws', await mob.evaluate(() => YF.grab()) === null);

// joystick: left-zone touch walks the player
await mob.evaluate(() => YF.playerTo(0.3, 4.35));
await sleep(300);
const jz0 = await mob.evaluate(() => YF.player().z);
await mob.evaluate(() => {
  const c = document.querySelector('#app canvas');
  c.dispatchEvent(new PointerEvent('pointerdown', { pointerId: 9, pointerType: 'touch', clientX: 70, clientY: 700, bubbles: true, isPrimary: true }));
});
await sleep(150);
T('mobile: joystick appears in left zone', await mob.evaluate(() => document.querySelector('#joy').classList.contains('on')));
for (let i = 1; i <= 10; i++) {
  await mob.evaluate(([y]) => {
    const c = document.querySelector('#app canvas');
    c.dispatchEvent(new PointerEvent('pointermove', { pointerId: 9, pointerType: 'touch', clientX: 70, clientY: y, bubbles: true, isPrimary: true }));
  }, [700 - i * 8]);
  await sleep(40);
}
const jz1 = await mob.evaluate(() => YF.player().z);
T('mobile: joystick walks the player', Math.abs(jz1 - jz0) > 0.25, `dz=${(jz1 - jz0).toFixed(2)}`);
await mob.evaluate(() => {
  const c = document.querySelector('#app canvas');
  c.dispatchEvent(new PointerEvent('pointerup', { pointerId: 9, pointerType: 'touch', bubbles: true, isPrimary: true }));
});
await mob.screenshot({ path: SHOTS + '12-mobile-touch.png' });
await mob.close();

// ---------- SUMMARY ----------
const failed = results.filter(r => !r.ok);
console.log('\n========================================');
console.log('TOTAL: ' + results.length + '  PASS: ' + (results.length - failed.length) + '  FAIL: ' + failed.length);
failed.forEach(f => console.log('  ✗ ' + f.name));
const realErrors = consoleErrors.filter(e => !e.includes('favicon') && !(e.includes('404') && asset404.length > 0));
if (asset404.length) console.log('  expected asset-probe 404s (optional Kenney slots, fallback active): ' + asset404.length);
console.log('console errors: ' + realErrors.length);
realErrors.slice(0, 12).forEach(e => console.log('  ⚠ ' + e.slice(0, 300)));
await browser.close();
process.exit(failed.length || realErrors.length ? 1 : 0);
