#!/usr/bin/env python3
"""Offline template branding; optional bounded HTTPS logo import. No panel API access."""
import argparse, base64, binascii, html, json, re, struct, sys, urllib.parse, urllib.request
from pathlib import Path

LIMIT = 256 * 1024
MARKER = re.compile(r'<!-- GHOST_SETTINGS:([A-Za-z0-9+/=]+) -->')
START, END = '<!-- GHOST_LOGO_START -->', '<!-- GHOST_LOGO_END -->'
THEMES = {'red': 0, 'green': 1, 'blue': 2}


def settings(previous):
    if not previous or not Path(previous).is_file():
        return {}
    source = Path(previous).read_text(encoding='utf-8')
    match = MARKER.search(source)
    if not match:
        return {}
    value = json.loads(base64.b64decode(match[1], validate=True))
    if not isinstance(value, dict):
        raise ValueError('Invalid saved branding settings')
    return value


def image_uri(data):
    if len(data) > LIMIT:
        raise ValueError('Logo must be no larger than 256 KiB')
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        pos, size, has_pixels, ended = 8, None, False, False
        while pos + 12 <= len(data):
            n = struct.unpack('>I', data[pos:pos+4])[0]
            kind = data[pos+4:pos+8]
            chunk = data[pos+8:pos+8+n]
            if pos + n + 12 > len(data):
                raise ValueError('Truncated PNG')
            crc = struct.unpack('>I', data[pos+8+n:pos+12+n])[0]
            if binascii.crc32(kind+chunk) & 0xffffffff != crc:
                raise ValueError('Invalid PNG checksum')
            if pos == 8:
                if kind != b'IHDR' or n != 13:
                    raise ValueError('Invalid PNG header')
                size = struct.unpack('>II', chunk[:8])
            has_pixels |= kind == b'IDAT' and n > 0
            pos += n + 12
            if kind == b'IEND':
                ended = n == 0 and pos == len(data)
                break
        if not ended or not has_pixels:
            raise ValueError('Incomplete PNG')
        mime = 'image/png'
    elif data.startswith(b'\xff\xd8'):
        # Read bounded JPEG marker segments for dimensions; baseline/progressive supported.
        size=None;pos=2;scan=False
        if not data.endswith(b'\xff\xd9'):raise ValueError('Incomplete JPEG')
        while pos<len(data)-2:
            if data[pos]!=255:raise ValueError('Invalid JPEG marker')
            while pos<len(data) and data[pos]==255:pos+=1
            if pos>=len(data):raise ValueError('Truncated JPEG marker')
            kind=data[pos];pos+=1
            if kind in (0,0xd8,0xd9) or 0xd0<=kind<=0xd7:raise ValueError('Invalid JPEG segment')
            if pos+2>len(data):raise ValueError('Truncated JPEG')
            length=int.from_bytes(data[pos:pos+2],'big')
            if length<2 or pos+length>len(data):raise ValueError('Truncated JPEG segment')
            if kind in (0xc0,0xc1,0xc2):
                if length<8:raise ValueError('Invalid JPEG frame')
                height=int.from_bytes(data[pos+3:pos+5],'big')
                width=int.from_bytes(data[pos+5:pos+7],'big')
                components=data[pos+7]
                if components not in (1,3,4) or length!=8+3*components:raise ValueError('Invalid JPEG frame length')
                size=(width,height)
            if kind==0xda:
                if length<6 or pos+length>=len(data)-2:raise ValueError('Invalid JPEG scan')
                scan=True;break
            pos+=length
        if not scan or not size:raise ValueError('Unsupported or incomplete JPEG')
        mime='image/jpeg'
    elif len(data) >= 30 and data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        if int.from_bytes(data[4:8], 'little') + 8 != len(data):
            raise ValueError('Invalid WebP length')
        kind = data[12:16]
        if kind == b'VP8X' and len(data) >= 30:
            size = (1 + int.from_bytes(data[24:27], 'little'), 1 + int.from_bytes(data[27:30], 'little'))
        elif kind == b'VP8 ' and data[23:26] == b'\x9d\x01\x2a':
            size = (int.from_bytes(data[26:28], 'little') & 0x3fff, int.from_bytes(data[28:30], 'little') & 0x3fff)
        elif kind == b'VP8L' and data[20] == 0x2f:
            bits = int.from_bytes(data[21:25], 'little')
            size = ((bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1)
        else:
            raise ValueError('Unsupported WebP header')
        mime = 'image/webp'
    else:
        raise ValueError('Only PNG, JPG/JPEG or WebP raster logos are supported')
    if not size or not all(0 < n <= 2048 for n in size):
        raise ValueError('Logo dimensions must be between 1 and 2048 pixels')
    return 'data:' + mime + ';base64,' + base64.b64encode(data).decode('ascii')


def valid_https(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password:
        raise ValueError('Logo URL must be HTTPS with no embedded credentials')


class HTTPSRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        valid_https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def load_logo(source):
    source=source.strip().strip('"').strip("'")
    if re.match(r'^[A-Za-z]:[\\/]',source):
        raise ValueError('This is a Windows path. Upload the image to this server first, or use an HTTPS image URL.')
    if not source.startswith('https://') and '://' not in source and not Path(source).expanduser().is_file():
        raise ValueError('Logo file not found on this server. Use an uploaded server file or an HTTPS image URL.')
    source=str(Path(source).expanduser()) if '://' not in source else source
    if source.startswith('https://'):
        valid_https(source)
        with urllib.request.build_opener(HTTPSRedirect()).open(source, timeout=15) as response:
            data = response.read(LIMIT + 1)
    elif '://' in source:
        raise ValueError('Use a local file path or an HTTPS URL')
    else:
        with Path(source).open('rb') as file:
            data = file.read(LIMIT + 1)
    return image_uri(data)


def render(template, brand, theme, mode, logo_source='', previous=None, status_feed=None, usage_base=None, logo_shape=None, status_port=None):
    old = settings(previous)
    brand = brand or old.get('brand', '')
    if not isinstance(brand, str) or not 1 <= len(brand) <= 80 or any(ord(c) < 32 for c in brand):
        raise ValueError('Brand must contain 1–80 printable characters')
    theme = theme or old.get('theme', 'red')
    if theme not in THEMES:
        raise ValueError('Invalid theme')
    if mode == 'keep':
        mode = old.get('logo_mode', 'ghost')
        uri = old.get('logo_data', '')
        if mode == 'custom':
            if not isinstance(uri, str) or not re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=]+', uri):
                raise ValueError('Invalid saved logo')
            uri = image_uri(base64.b64decode(uri.split(',', 1)[1], validate=True))
    else:
        uri = load_logo(logo_source) if mode == 'custom' else ''
    if mode not in ('ghost', 'none', 'custom'):
        raise ValueError('Invalid logo mode')
    if template.count(START) != 1 or template.count(END) != 1:
        raise ValueError('This template does not support configurable logos; use the matching release files')
    logo_shape=logo_shape or old.get('logo_shape','square')
    if logo_shape not in ('circle','square'):raise ValueError('Invalid logo shape')
    if mode != 'ghost':
        radius='50%' if logo_shape=='circle' else '20px'
        replacement = '' if mode == 'none' else '<div class="logo-wrap"><div class="logo-ring" style="border-radius:'+radius+'"></div><div class="logo-inner" style="border-radius:'+radius+';overflow:hidden"><img class="brand-image" style="width:100%;height:100%;object-fit:cover;border-radius:'+radius+'" alt="Brand logo" src="'+uri+'"></div></div>'
        template = re.sub(re.escape(START)+r'.*?'+re.escape(END), lambda _: START+'\n'+replacement+'\n'+END, template, flags=re.S)
    # Encode < > & quotes and template delimiters before placing branding in
    # HTML/JS text contexts. Decoding remains browser-side, never panel template-side.
    safe = html.escape(brand, quote=True)
    for c in "{}%`$\\":
        safe = safe.replace(c, '&#'+str(ord(c))+';')
    template = template.replace('YOUR BRAND', safe)
    template, count = re.subn(r'^let themeIndex = [0-2];', 'let themeIndex = '+str(THEMES[theme])+';', template, flags=re.M)
    if count != 1:
        raise ValueError('Expected one initial theme setting')
    explicit_feed=status_feed is not None
    status_feed = old.get('status_feed', '') if status_feed is None else status_feed
    if status_feed:
        if any(ord(c) < 32 for c in status_feed) or len(status_feed)>2048:
            raise ValueError('Invalid status feed')
        if not (status_feed.startswith('/') and not status_feed.startswith('//')):
            valid_https(status_feed)
    marker = '<meta name="ghost-status-feed" content="">'
    if marker not in template:
        raise ValueError('Expected status feed marker')
    template = template.replace(marker, '<meta name="ghost-status-feed" content="'+html.escape(status_feed,quote=True)+'">', 1)
    explicit_usage=usage_base is not None
    usage_base=old.get('usage_base','') if usage_base is None else usage_base
    if usage_base and (not re.fullmatch(r'/[A-Za-z0-9_/-]+',usage_base) or usage_base.startswith('//')):
        raise ValueError('Usage path must be a same-origin root-relative path, e.g. /ghost-usage/')
    usage_marker='<meta name="ghost-usage-base" content="">'
    if usage_marker not in template:raise ValueError('Missing usage marker')
    template=template.replace(usage_marker,'<meta name="ghost-usage-base" content="'+html.escape(usage_base,quote=True)+'">',1)
    status_port=(0 if explicit_feed else old.get('status_port',0)) if status_port is None else status_port
    if not isinstance(status_port,int) or isinstance(status_port,bool) or (status_port!=0 and not 1024<=status_port<=65535):raise ValueError('Invalid monitor port')
    port_marker='<meta name="ghost-status-port" content="">'
    if port_marker not in template:raise ValueError('Missing monitor port marker')
    template=template.replace(port_marker,'<meta name="ghost-status-port" content="'+(str(status_port) if status_port else '')+'">',1)
    usage_port=0 if explicit_usage else old.get('usage_port',0)
    if not isinstance(usage_port,int) or isinstance(usage_port,bool) or (usage_port!=0 and not 1024<=usage_port<=65535):raise ValueError('Invalid usage port')
    usage_port_marker='<meta name="ghost-usage-port" content="">'
    if usage_port_marker not in template:raise ValueError('Missing usage port marker')
    template=template.replace(usage_port_marker,'<meta name="ghost-usage-port" content="'+(str(usage_port) if usage_port else '')+'">',1)
    saved = dict(usage_port=usage_port, status_port=status_port, logo_shape=logo_shape, usage_base=usage_base, status_feed=status_feed, brand=brand, theme=theme, logo_mode=mode, logo_data=uri if mode == 'custom' else '')
    encoded = base64.b64encode(json.dumps(saved, ensure_ascii=False).encode()).decode()
    template = MARKER.sub('', template)
    template = template.replace('</head>', '<!-- GHOST_SETTINGS:'+encoded+' -->\n</head>', 1)
    return template, saved


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--template', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--previous')
    p.add_argument('--brand', default='')
    p.add_argument('--theme', default='', choices=['', *THEMES])
    p.add_argument('--logo-mode', default='keep', choices=['keep', 'ghost', 'none', 'custom'])
    p.add_argument('--logo-source', default='')
    p.add_argument('--logo-shape', choices=['circle','square'])
    p.add_argument('--manifest')
    p.add_argument('--status-feed', default=None)
    p.add_argument('--usage-base', default=None)
    args = p.parse_args()
    result, state = render(Path(args.template).read_text(), args.brand, args.theme, args.logo_mode, args.logo_source, args.previous, args.status_feed, args.usage_base, args.logo_shape)
    Path(args.output).write_text(result)
    if args.manifest:
        manifest = {'name':state['brand'], 'short_name':state['brand'][:24], 'start_url':'./', 'display':'standalone', 'background_color':'#09080c', 'theme_color':{'red':'#ff4151','green':'#22d39a','blue':'#55b1ff'}[state['theme']]}
        if state['logo_mode'] == 'custom':
            manifest['icons'] = [{'src':state['logo_data'], 'sizes':'any', 'type':state['logo_data'].split(';')[0][5:]}]
        else:
            icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><rect width="192" height="192" rx="40" fill="'+manifest['theme_color']+'"/><path d="M48 108V76a48 48 0 0 1 96 0v32l14 40-24-10-18 10-20-10-20 10-18-10-24 10Z" fill="none" stroke="white" stroke-width="7"/><circle cx="80" cy="80" r="5" fill="white"/><circle cx="112" cy="80" r="5" fill="white"/></svg>'
            manifest['icons'] = [{'src':'data:image/svg+xml,'+urllib.parse.quote(icon), 'sizes':'any', 'type':'image/svg+xml'}]
        Path(args.manifest).write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print('Branding prepared; logo embedded, no public asset route required')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print('Branding failed: '+str(error), file=sys.stderr)
        sys.exit(1)
