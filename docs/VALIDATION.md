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

## Subscription target discovery
- Added admin-configured URL import for raw/base64 VLESS/Trojan/VMess/SS and rendered Ghost HTML; deduplicated bounded TCP endpoints only. No request-side scanning API.
- Manager hidden input stores the subscription source in private config; monitor refreshes targets every 900 seconds and samples at its configured interval. Cross-origin redirects refused, reads bounded to 2 MiB, generic errors omit URL/token; public feed remains endpoint-ID/sample-only.
- Eight importer tests PASS including real local HTTP response, format parsing, duplicate removal, IPv6, unsupported TCP transports and endpoint-count bounds; existing 11 monitor and 18 script tests PASS. No live panel subscription or proxy route tested.

## Domain-free subscription gateway
- Added optional rootless HTTP gateway on a separate public IPv4 port: fixed loopback subscription backend and fixed monitor endpoint, subscription-prefix route allowlist, no arbitrary proxy requests, no access logs or cookie forwarding, bounded responses/threads/timeouts, no redirects. Current Ghost HTML gets a same-origin status meta value; raw subscriptions retain traffic/profile headers.
- Option 7 installs/starts/enables after explicit consent, checks port availability, reuses the private monitor subscription source and prints the new private subscription URL locally. Option 4 offers the same setup. YES/y/yes accepted case-insensitively. Existing web-server configs/firewall are not modified.
- Real loopback integration PASS: browser HTML feed injection, backend Host preservation, raw-body/usage header forwarding, JSON feed, denied unrelated/traversal paths and refused redirect. Config bounds and missing template marker tests PASS. No real panel deployment, WAN port reachability, performance/load or TLS integration tested.
- HTTP IP:port requires using the new URL and an accessible inbound port. HTTPS certificate automation and root-path-only subscriptions are outside this implementation. README includes upload/image/setup/monitor/gateway/firewall/update/stop steps and these limits; no test-count promotion added.

## Original-subscription attachment (supersedes separate entrance workflow)
- Option 7 now patches the installed original template with the monitor UI and a persisted monitor-data port, preserving branding/profile image, Go/Jinja bindings, original URL/port/token and database. No Apache/Nginx changes. Gateway becomes status-only, returns no subscription pages and emits CORS only for the exact original HTTP Origin.
- Existing separate entrance can be reused as the data port; original panel restarts after backup to load the attached template. A bounded readiness retry handles data-service startup; template restoration is attempted on setup failure. Real systemd/panel restart and rollback paths remain untested on a live host.
- Local real HTTP tests PASS for CORS allowed/other origins, JSON and disabled subscription entrance; Node fetch tests PASS for same-host data port, omitted credentials, no insecure HTTPS fallback and disallowed foreign HTTP feed. Three-template attachment/preserved bindings, settings retention and future branding updates tested. No live-host validation yet.
- Current HTTP same-host mode requires an accessible data port. HTTPS origins are refused before mutation and need an HTTPS feed. README rewrites installation/migration/upload/monitor/update/troubleshooting around the original subscription URL; no test-count marketing section.

## Original-subscription usage-chart connection
- Added option 8 and post-collector setup offer. Reuses the existing status-only data service or creates one without requiring a reachability monitor; original subscription URL remains unchanged. Template and service config backed up, readiness checked and selected 3X-UI panel restarted. No new API credentials requested for chart attachment.
- Added per-subscription-token history forwarding to fixed loopback 19192, enabled only by private admin config. No history list route, query requests and unrelated paths denied, exact-origin CORS, omitted cookies/access logs/referrer and no API credential export.
- Real loopback test uses actual history DB/ingestion/read logic with two tokens: each gets only its own measured delta; unknown/list/query/disabled requests fail. Browser-function Node tests verify only own token to configured same-host port and refusal of foreign-origin/insecure HTTPS fallback. Branding updates retain both attachments.
- User reported successful live collector v3 sampling for one subscription; new chart attachment not yet validated on that live host. No claim of universal panel compatibility or retrospective history.

## Purple theme candidate — 2026-11-11

- Added fourth theme to all three templates, installer, retained settings and PWA manifest. Existing default selections remain unchanged until explicitly selected.
- Python scripts suite: 22 tests, 20 passed and 2 bootstrap tests skipped in this environment. All 17 branding tests passed, including all panel/theme/logo combinations, saved purple selection and private-route preservation.
- Theme JS test: all four initial themes, two complete cycles from each starting theme in all three panels; no previous purple class remains after switching; gradient/logo/browser meta colors match. Syntax checked across all 12 generated fixtures.
- Existing status-port, usage-port and status UI Node tests passed. Appearance installer shell syntax and capture helper Python syntax passed.
- Purple browser screenshot/mobile visual QA could not run in this environment: local Chromium failed its Unix socket startup, and the cloud browser blocked file-URL navigation. The README clearly labels the included purple SVG as a palette illustration, not a screenshot. The optional capture helper is supplied for operator execution and has NOT been browser-validated here.
- No GitHub push or live panel/server changes performed. Current public README edits were retained as the base.
