#!/usr/bin/env python3
"""
Script de atualização automática dos Mentores (Inatel Startups).
Busca a view oficial 'Vitrine - Time de Mentores' no Airtable, baixa fotos novas
via endpoint assinado, preserva os cargos curados, ordena A-Z e atualiza
mentores_data.json e index.html.
"""
import html
import http.cookiejar
import json
import os
import re
import unicodedata
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "elementos", "mentores")
DATA_JSON = os.path.join(BASE_DIR, "mentores_data.json")
INDEX_HTML = os.path.join(BASE_DIR, "index.html")

APP_ID = "appNpzNg1CLsXf3Hn"
AIRTABLE_VIEW_URL = "https://airtable.com/appNpzNg1CLsXf3Hn/shrhHcTKwTnzAdM4o/tblz2ADXqNnD830uA"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

LINKEDIN_SVG = (
    '<svg class="linkedin-icon" width="14" height="14" viewBox="0 0 24 24" fill="currentColor">'
    '<path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14'
    'c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.784-1.75-1.75s.784-1.75 '
    '1.75-1.75 1.75.784 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-1.337-.026-2.54-'
    '1.545-2.54-1.528 0-1.766 1.216-1.766 2.473v5.671h-3v-11h2.875v1.502h.04c.4-.754 1.378-1.547 '
    '2.836-1.547 3.03 0 3.59 1.995 3.59 4.592v6.453z"/></svg>'
)

EXTERNAL_SVG = (
    '<svg class="external-link-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>'
    '<polyline points="15 3 21 3 21 9"></polyline>'
    '<line x1="10" y1="14" x2="21" y2="3"></line></svg>'
)

ARROW_SVG = (
    '<svg class="arrow-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<line x1="5" y1="12" x2="19" y2="12"></line>'
    '<polyline points="12 5 19 12 12 19"></polyline></svg>'
)


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")


def summarize_bio(bio):
    if not bio:
        return "Mentor Especialista - Inatel Startups"
    first_line = bio.strip().split("\n")[0]
    first_sentence = re.split(r"[.!?]", first_line)[0].strip()
    if len(first_sentence) > 72:
        first_sentence = first_sentence[:69].rsplit(" ", 1)[0] + "..."
    return first_sentence or "Mentor Especialista - Inatel Startups"


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    existing_roles = {}
    existing_imgs = {}
    if os.path.exists(DATA_JSON):
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            for item in json.load(f):
                existing_roles[item["name"]] = item["role"]
                existing_imgs[item["name"]] = item["img"]

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(AIRTABLE_VIEW_URL, headers={"User-Agent": UA})
    with opener.open(req, timeout=20) as resp:
        html_page = resp.read().decode("utf-8")

    policy_str = (
        re.search(r'"accessPolicy":\s*"(.*?)(?<!\\)"', html_page)
        .group(1)
        .encode("utf-8")
        .decode("unicode_escape")
    )
    page_load_id = re.search(r'"pageLoadId":\s*"(.*?)"', html_page).group(1)
    view_id = json.loads(policy_str)["allowedActions"][0]["modelIdSelector"]

    api_url = f"https://airtable.com/v0.3/view/{view_id}/readSharedViewData"
    headers = {
        "User-Agent": UA,
        "x-airtable-application-id": APP_ID,
        "x-airtable-page-load-id": page_load_id,
        "x-airtable-access-policy": policy_str,
        "x-requested-with": "XMLHttpRequest",
        "x-time-zone": "America/Sao_Paulo",
        "x-user-locale": "pt-BR",
    }
    req2 = urllib.request.Request(api_url, headers=headers)
    with opener.open(req2, timeout=20) as resp2:
        res = json.loads(resp2.read().decode("utf-8"))

    data = res["data"]
    rows = data.get("rows", [])
    signed_urls = data.get("signedUserContentUrls", {})
    existing_files = set(os.listdir(IMG_DIR))

    mentors_list = []
    for r in rows:
        vals = r.get("cellValuesByColumnId", {})
        name = (vals.get("fldGk6LdpUhqTSjkr") or "").strip()
        if not name:
            continue
        bio = (vals.get("fldwHK4CbsY83i85D") or "").strip()
        role = existing_roles.get(name) or summarize_bio(bio)

        raw_li = (vals.get("fldoL2ndztTLxot8q") or "").strip()
        if raw_li:
            linkedin_url = raw_li if raw_li.startswith("http") else f"https://{raw_li}"
            has_li = True
        else:
            linkedin_url = AIRTABLE_VIEW_URL
            has_li = False

        slug = slugify(name)
        if name in existing_imgs and os.path.exists(os.path.join(BASE_DIR, existing_imgs[name])):
            img_rel = existing_imgs[name]
        elif f"{slug}.jpg" in existing_files:
            img_rel = f"elementos/mentores/{slug}.jpg"
        else:
            img_rel = f"elementos/mentores/{slug}.jpg"
            fotos = vals.get("fldenpuRM4MOcmLoR") or []
            if fotos:
                foto = fotos[0]
                dl_key = foto.get("largeThumbUrl") or foto.get("fullThumbUrl") or foto.get("url")
                signed_dl = signed_urls.get(dl_key)
                if signed_dl:
                    r_img = urllib.request.Request(signed_dl, headers={"User-Agent": UA})
                    with opener.open(r_img, timeout=15) as resp_img:
                        with open(os.path.join(BASE_DIR, img_rel), "wb") as f_out:
                            f_out.write(resp_img.read())

        mentors_list.append(
            {
                "name": name,
                "role": role,
                "link": linkedin_url,
                "has_custom_linkedin": has_li,
                "img": img_rel,
            }
        )

    mentors_list.sort(
        key=lambda m: unicodedata.normalize("NFKD", m["name"]).encode("ascii", "ignore").decode("ascii").lower()
    )

    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(mentors_list, f, ensure_ascii=False, indent=2)

    cards_html = []
    for idx, m in enumerate(mentors_list):
        name_esc = html.escape(m["name"])
        role_esc = html.escape(m["role"])
        link_esc = html.escape(m["link"])
        if m["has_custom_linkedin"]:
            btn = (
                f'                        <a href="{link_esc}" target="_blank" rel="noopener noreferrer" class="mentor-link-btn" aria-label="Ver perfil de {name_esc} no LinkedIn">\n'
                f"                            {LINKEDIN_SVG}\n"
                f"                            <span>LinkedIn</span>\n"
                f"                            {ARROW_SVG}\n"
                f"                        </a>"
            )
        else:
            btn = (
                f'                        <a href="{link_esc}" target="_blank" rel="noopener noreferrer" class="mentor-link-btn" aria-label="Ver perfil completo de {name_esc} no Airtable">\n'
                f"                            {EXTERNAL_SVG}\n"
                f"                            <span>Ver Perfil</span>\n"
                f"                            {ARROW_SVG}\n"
                f"                        </a>"
            )

        cards_html.append(
            f'                <!-- CARD: {name_esc} -->\n'
            f'                <div class="mentor-card" data-index="{idx}">\n'
            f'                    <div class="mentor-avatar-container">\n'
            f'                        <img src="{m["img"]}?v=5" alt="Foto de {name_esc}" class="mentor-avatar-img" loading="lazy">\n'
            f'                    </div>\n'
            f'                    <div class="mentor-info">\n'
            f'                        <h4 class="mentor-name">{name_esc}</h4>\n'
            f'                        <p class="mentor-role">{role_esc}</p>\n'
            f'                    </div>\n'
            f'                    <div class="mentor-footer">\n'
            f"{btn}\n"
            f"                    </div>\n"
            f"                </div>"
        )

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        full_html = f.read()

    pattern = r'(<div class="mentors-track" id="mentors-track">\n).*?(\n\s*</div>\s*</div>\s*<button class="slider-arrow next")'
    match = re.search(pattern, full_html, re.DOTALL)
    if not match:
        raise RuntimeError("Não foi possível localizar o container #mentors-track no index.html")

    full_html = full_html[: match.start(1) + len(match.group(1))] + "\n\n".join(cards_html) + full_html[match.start(2) :]
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"SUCESSO! {len(mentors_list)} mentores atualizados no index.html e mentores_data.json.")


if __name__ == "__main__":
    main()
