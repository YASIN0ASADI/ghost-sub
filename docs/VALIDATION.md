# Ghost Sub appearance refresh — 2026-11-08

Local candidate from the eight uploaded source files. No GitHub push or server install performed. GitHub connector reports push=false for YASIN0ASADI/ghost-sub.

- 10 branding tests PASS: panel/template bindings, themes, optional logo absence, embedded custom PNG preservation across update without original image file, input bounds/formats, escaping and unchanged Tracker files.
- Installer bash syntax PASS. Python branding CLI and generated branded manifest PASS.
- JavaScript syntax PASS for 18 scripts across 9 rendered panel/theme fixtures.
- Browser QA: actual 390px iframe (375px content with scrollbar), English/Persian, RTL, red/green/blue theme changes, week/month chart rendering. RTL document clientWidth=scrollWidth=375 (no page horizontal overflow in that sample).
- Fixed an extra closing div in supplied templates which placed subsequent cards outside .container. No data-contract changes.
- Template data bindings unchanged; Tracker Python/service byte-for-byte unchanged. Chart fetching, fallback and aggregation unchanged in production templates. Demo pages alone embed illustrative data for offline viewing.
- QR/copy keyboard hooks and text-only config names added. Live app imports, actual clipboard writes, third-party QR rendering and actual panel API deployment were not comprehensively exercised.
- Installer/logo HTTPS retrieval and restart of real panels NOT executed. Three-panel live integration, actual image decode breadth and PWA installability remain unverified.
- Existing Tracker/backend routing and connection-doctor behavior remain outside this visual change. This is not a full security audit.

## Measured node status + SVG flags candidate
- Added a separate standard-library fixed-target TCP monitor with persistent SQLite samples, loopback-only read-only HTTP feed, optional explicit installer/unit, and same-origin HTTPS proxy instructions. No real server installation performed.
- 11 monitor tests PASS: no invented empty uptime, stale/failed/mixed states, partial sample coverage, unknown history gaps, identity normalization, duplicate rejection, real local TCP success/failure, persistent state, no raw endpoint in exported JSON.
- 11 branding tests PASS including persisted/disabled/invalid feed URLs and preservation of uploaded Tracker files.
- JS core tests PASS: SVG country assets, no duplicate regional-flag emoji in rendered names, protocol parsing, stale feed rejection, matching monitor/browser SHA256 identifiers with WebCrypto and fallback (DNS,IPv4,IPv6,multi-block inputs).
- Actual local subprocess monitor -> TCP listener -> SQLite -> HTTP JSON integration PASS. No external targets probed.
- Browser mobile QA: four demo states present; English and Persian/RTL labels; expandable sample ratio, probe label, last check, observed span and unknown history segments. 375px content had clientWidth=scrollWidth (no horizontal overflow in that sample).
- Removed misleading static ONLINE summary; current overview now depends on fresh measured feed. Browser port checks do not establish user config health or OS uptime; chart is successful sample ratio, not continuous uptime.
- Static preview clearly marks illustrative sample data and uses YOUR BRAND; production templates contain no fabricated monitoring data.
- All nine panel/theme rendered fixtures pass JavaScript syntax checks; both installer shells pass bash syntax.
- Country artwork supports the documented subset with neutral globe fallback; full worldwide SVG artwork is not bundled.
- Public HTTPS route, real panel deployment, multi-probe aggregation, long-term WAN monitoring and service-account/systemd lifecycle on a new server remain unverified. No public GitHub changes.

## Compact line-graph revision
- Replaced verbose per-node paragraphs and segmented bars with a default-visible compact SVG line plot, 24h axis, sample ratio and recorded span; probe/TCP limitations remain available as hover/help text.
- Null, absent, non-finite and out-of-range samples break the line rather than inventing availability; isolated observations draw dots. Pure JS regression tests PASS.
- Existing 22 Python tests and JS identity/country/freshness tests PASS. All 9 preview script sets pass node syntax checks.
- Browser QA verified English/Persian graphs and compact mobile rows with YOUR BRAND. Demonstration graphs clearly use sample data; production templates retain null feed until configured.
- 3X-UI official API docs reviewed: per-client cumulative traffic is available. Existing supplied sub.html already binds uploadByte/downloadByte but has no history chart. No 3X-UI collector is shipped in this revision; installed panel version/auth/response mapping is required before adapter implementation.

## Optional 3X-UI sampled history and terminal manager (supersedes prior collector note)
- Added an optional separate 3X-UI collector and same-origin subscription-token history route. Existing Marzban/Pasarguard tracker files remain byte-for-byte unchanged. No history is invented before collection begins; stale/absent history hides the new chart.
- 18 history tests PASS: old/new response fixtures, wrapping, deduplication, authentication boundaries, no adapter switch on transient failure, pinned adapter, baseline/delta/reset/gap handling, removed subscriptions, isolation, no secret export, TLS and redirect restrictions. These fixtures do not prove compatibility with every release/fork.
- Real loopback mock-panel HTTP integration PASS for form/cookie login, custom base path, old/new routes and persisted adapter selection. Actual 3X-UI panel integration remains pending.
- 12 branding tests + 11 monitor tests PASS (41 Python tests total); JS identity/country/freshness/gap tests and all nine rendered fixture script sets PASS. Shell syntax checks PASS.
- Staged manager file layout, modes including restrictive umask, symlink refusal, harmless menu entry/exit and noninteractive mutation guard verified. No real host service installation performed.
- Browser: 3X-UI preview English/Persian, week bars and month line chart visible; Persian mobile document width and scroll width both 375px. Preview uses clearly labelled illustrative data only; its history cache is intentionally permanent for offline demonstration.
- Terminal manager installs bundled sources, configures optional collectors with explicit separate start/boot choices, reports read-only local checks and restores matching tagged template backups. It does not fetch releases, configure a reverse proxy, or provide whole-system/database rollback.
- Real panel API/auth, public HTTPS history routing, fresh-server systemd lifecycle and live three-panel regressions are pending. No GitHub push, real credentials, or production/server changes.

## One-command menu restoration
- install.sh now downloads a complete source archive and opens the installed terminal menu, including when invoked via bash process substitution. Only an explicit application file whitelist is read from the archive; missing/non-regular files stop preparation.
- Appearance installation moved to scripts/install_template.sh; menu options invoke it directly without recursively downloading/reopening the manager. No panel is restarted merely by entering the menu.
- Two subprocess tests PASS: process-substitution command with mock download reaches menu; incomplete archive fails before host installer. Mock Python blocks all host installation. Existing 12 branding tests PASS; shell syntax PASS. Real remote download/system installation still requires a live host test after publication.
- README restores the branded header/panel badges and original one-line command; test-count section removed at user request.

## Profile-image input and JPEG support
- Image address can be supplied directly; uploaded server files and HTTPS image URLs supported. Windows paths get an explicit upload explanation. Circle/rounded-square profile frames and saved shape verified.
- Added bounded JPEG frame/scan header parsing and image/jpeg embedding; real JPEG fixture, malformed/truncated input and retention across reinstallation tested. This validates structure and bounds, not a complete image codec decoder. Existing PNG/WebP support remains.
- 18 script tests PASS, including two mocked bootstrap checks. No real SSH transfer or production panel install executed here. README documents Windows full-file-path selection, SCP, optional monitor/history prompts and updates.
