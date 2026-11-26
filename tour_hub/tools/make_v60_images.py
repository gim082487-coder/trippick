#!/usr/bin/env python3
"""v60 이미지 — 신규 가이드 10편 히어로(1200×800+WebP 480/720/960)·OG(1200×630).

    python3 tools/make_v60_images.py

사진은 위키미디어 공용의 실제 촬영지 사진만 씁니다(2026-11-26 확인, 라이선스·저작자 병기).
"""
from __future__ import annotations

import io
import json
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
V60 = ROOT / "images" / "v60"
OG = ROOT / "images" / "og"
FONT_BOLD = Path("/workspace/tmp_font/Pretendard-Bold.otf")
FONT_NOTO = Path("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf")

GUIDES = [
    {
        "slug": "beppu-onsen-1n2d-course",
        "file": "Beppu_Tower02s4s3200.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/d1/Beppu_Tower02s4s3200.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Beppu_Tower02s4s3200.jpg",
        "artist": "663highland",
        "license": "CC BY 2.5",
        "alt": "벳푸 온천가와 벳푸 타워가 보이는 시가지",
        "place": "Beppu, Oita, Japan",
        "og": "v60-beppu-og.jpg",
        "kicker": "트립픽 · 벳푸 온천 1박2일",
        "title": "지옥순례 7곳 2,400엔",
        "title2": "모래찜질과 료칸 1박",
        "sub": "하카타에서 소닉 2시간  |  공통권 이틀 유효  |  노천탕·족욕",
    },
    {
        "slug": "kaohsiung-tainan-3n4d-course",
        "file": "Cityscape_of_Kaohsiung,_Taiwan_202303.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Cityscape_of_Kaohsiung%2C_Taiwan_202303.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Cityscape_of_Kaohsiung,_Taiwan_202303.jpg",
        "artist": "臺灣港務股份有限公司高雄港務分公司",
        "license": "CC BY-SA 4.0",
        "alt": "가오슝 항구와 아시아신만구의 항공 전경",
        "place": "Kaohsiung, Taiwan",
        "og": "v60-kaohsiung-og.jpg",
        "kicker": "트립픽 · 가오슝·타이난 3박4일",
        "title": "고속철 1,490대만달러",
        "title2": "치진섬 페리 30元",
        "sub": "타이베이→타이난 1,350元  |  이지카드 100元  |  야시장",
    },
    {
        "slug": "kota-kinabalu-3n4d-course",
        "file": "Panoramic_view_of_Kota_Kinabalu_City.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Panoramic_view_of_Kota_Kinabalu_City.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Panoramic_view_of_Kota_Kinabalu_City.jpg",
        "artist": "FILMR Production",
        "license": "CC BY 3.0",
        "alt": "코타키나발루 시내와 앞바다 전경",
        "place": "Kota Kinabalu, Sabah, Malaysia",
        "og": "v60-kota-kinabalu-og.jpg",
        "kicker": "트립픽 · 코타키나발루 3박4일",
        "title": "톤주아루 입장료 25링깃",
        "title2": "보트 2섬 58링깃",
        "sub": "선착장 사우스 제티  |  마지막 배 16시  |  석양 18시",
    },
    {
        "slug": "bohol-3n4d-course",
        "file": "Chocolate_Hills_Bohol.JPG",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/af/Chocolate_Hills_Bohol.JPG",
        "page": "https://commons.wikimedia.org/wiki/File:Chocolate_Hills_Bohol.JPG",
        "artist": "P199",
        "license": "CC BY-SA 3.0",
        "alt": "보홀 초콜릿 힐스의 언덕들",
        "place": "Chocolate Hills, Bohol, Philippines",
        "og": "v60-bohol-og.jpg",
        "kicker": "트립픽 · 보홀 3박4일",
        "title": "세부에서 오션젯 960페소",
        "title2": "2시간 · 하루 10편",
        "sub": "팡라오 직항  |  알로나비치 30~40분  |  무비자 30일",
    },
    {
        "slug": "beijing-3n4d-course",
        "file": "The_Forbidden_City_-_View_from_Coal_Hill.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/ef/The_Forbidden_City_-_View_from_Coal_Hill.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:The_Forbidden_City_-_View_from_Coal_Hill.jpg",
        "artist": "Pixelflake",
        "license": "CC BY-SA 3.0",
        "alt": "징산공원에서 내려다본 자금성",
        "place": "Forbidden City, Beijing, China",
        "og": "v60-beijing-og.jpg",
        "kicker": "트립픽 · 베이징 3박4일",
        "title": "자금성 겨울 40위안",
        "title2": "공항철도 25위안",
        "sub": "무비자 30일(2026-12-31까지)  |  7일 전 예약  |  월요일 휴관",
    },
    {
        "slug": "qingdao-2n3d-course",
        "file": "Tsingtao_Brewery_in_Qingdao.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Tsingtao_Brewery_in_Qingdao.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Tsingtao_Brewery_in_Qingdao.jpg",
        "artist": "Lennartbj",
        "license": "CC BY-SA 4.0",
        "alt": "칭다오 맥주박물관이 있는 칭다오 맥주공장 옛 건물",
        "place": "Tsingtao Brewery, Qingdao, China",
        "og": "v60-qingdao-og.jpg",
        "kicker": "트립픽 · 칭다오 2박3일",
        "title": "맥주박물관 60위안",
        "title2": "공항 8호선 40분",
        "sub": "무비자 30일  |  5·4광장 거점  |  12~2월 휴관 주의",
    },
    {
        "slug": "sydney-4n5d-course",
        "file": "Sydney_Opera_House_2026.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e1/Sydney_Opera_House_2026.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Sydney_Opera_House_2026.jpg",
        "artist": "BAVhah",
        "license": "CC BY-SA 4.0",
        "alt": "시드니 오페라하우스와 서큘러키 항만",
        "place": "Sydney, Australia",
        "og": "v60-sydney-og.jpg",
        "kicker": "트립픽 · 시드니 4박5일",
        "title": "오팔 하루 상한 19.30달러",
        "title2": "공항역 18.61달러 별도",
        "sub": "ETA 앱 20호주달러  |  블루마운틴 2시간  |  컨택리스 승차",
    },
    {
        "slug": "switzerland-jungfrau-zermatt-pass",
        "file": "Sphinx_et_Jungfrau_-_img_06980.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Sphinx_et_Jungfrau_-_img_06980.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Sphinx_et_Jungfrau_-_img_06980.jpg",
        "artist": "Pmau",
        "license": "CC BY-SA 4.0",
        "alt": "융프라우요흐 스핑크스 전망대와 융프라우 봉우리",
        "place": "Jungfraujoch, Switzerland",
        "og": "v60-switzerland-og.jpg",
        "kicker": "트립픽 · 스위스 4박5일",
        "title": "트래블 패스 3일 254프랑",
        "title2": "하프 페어 150프랑",
        "sub": "융프라우 25% vs 50%  |  좌석 예약 10프랑  |  체르마트",
    },
    {
        "slug": "eastern-europe-prague-vienna-budapest",
        "file": "Prague_(6365119737).jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Prague_%286365119737%29.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Prague_(6365119737).jpg",
        "artist": "Moyan Brenn",
        "license": "CC BY 2.0",
        "alt": "카를교와 블타바강 건너로 보이는 프라하 성",
        "place": "Prague, Czech Republic",
        "og": "v60-eastern-europe-og.jpg",
        "kicker": "트립픽 · 동유럽 6박7일",
        "title": "프라하→비엔나 4시간 12분",
        "title2": "레기오젯 16.90유로",
        "sub": "비엔나→부다페스트 2시간 39분  |  세체니 13,200포린트",
    },
    {
        "slug": "japan-shinkansen-jr-pass-guide",
        "file": "Series-N700S-J2.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/88/Series-N700S-J2.jpg",
        "page": "https://commons.wikimedia.org/wiki/File:Series-N700S-J2.jpg",
        "artist": "MaedaAkihiko",
        "license": "CC BY-SA 4.0",
        "alt": "도카이도 신칸센을 달리는 N700S 노조미",
        "place": "Tokaido Shinkansen, Japan",
        "og": "v60-jr-pass-og.jpg",
        "kicker": "트립픽 · 일본 신칸센·JR패스",
        "title": "7일권 50,000엔",
        "title2": "도쿄–오사카 왕복 29,440엔",
        "sub": "노조미 추가권 4,960엔  |  스마트EX  |  특대 수하물 좌석",
    },
]


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    for p in (path, FONT_NOTO):
        if p.exists():
            return ImageFont.truetype(str(p), size)
    raise SystemExit(f"폰트를 찾지 못했습니다: {path}")


CACHE = ROOT / "images" / "v60" / "_src"


def fetch(name: str, url: str) -> Image.Image:
    """위키미디어 공용 원본을 한 번만 받아 캐시한다(봇 요청 제한 대비 재시도)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    local = CACHE / name.replace("/", "_")
    if local.exists():
        return Image.open(local)
    req = urllib.request.Request(url, headers={
        "User-Agent": "TrippickBot/6.0 (https://trippick.pages.dev; gim082487@gmail.com) python-urllib",
        "Accept": "image/jpeg,image/png,*/*",
    })
    last = None
    for wait in (0, 20, 40, 70):
        if wait:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
            local.write_bytes(raw)
            return Image.open(io.BytesIO(raw))
        except Exception as e:  # 429 등
            last = e
    raise SystemExit(f"이미지 받기 실패 {name}: {last}")


def crop_ratio(im: Image.Image, tw: int, th: int, top: float = 0.42) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")
    target = tw / th
    sw, sh = im.size
    if sw / sh > target:
        nw = int(sh * target)
        im = im.crop(((sw - nw) // 2, 0, (sw + nw) // 2, sh))
    else:
        nh = int(sw / target)
        t = int((sh - nh) * top)
        im = im.crop((0, t, sw, t + nh))
    return im.resize((tw, th), Image.LANCZOS)


def hero(job: dict) -> Path:
    V60.mkdir(parents=True, exist_ok=True)
    im = crop_ratio(fetch(job["file"], job["url"]), 1200, 800, 0.45)
    p = V60 / f"{job['slug']}.jpg"
    im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
    for w in (480, 720, 960):
        im.resize((w, round(800 * w / 1200)), Image.LANCZOS).save(
            V60 / f"{job['slug']}-{w}.webp", "WEBP", quality=78, method=6
        )
    return p


def og(job: dict) -> Path:
    W, H = 1200, 630
    img = crop_ratio(fetch(job["file"], job["url"]), W, H, 0.42)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for x in range(W):
        a = int(200 * max(0.0, 1 - x / (W * 1.18)))
        d.rectangle([x, 0, x + 1, H], fill=(7, 18, 33, a))
    d.rectangle([0, H - 190, W, H], fill=(7, 18, 33, 120))
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")

    draw = ImageDraw.Draw(img)
    x, y = 68, 150
    draw.text((x, y), job["kicker"], font=font(FONT_NOTO, 30), fill=(196, 219, 255))
    y += 64
    draw.text((x, y), job["title"], font=font(FONT_BOLD, 66), fill=(255, 255, 255))
    y += 90
    draw.text((x, y), job["title2"], font=font(FONT_BOLD, 72), fill=(255, 255, 255))
    y += 108
    draw.text((x, y), job["sub"], font=font(FONT_NOTO, 26), fill=(221, 231, 243))
    draw.ellipse([x, H - 74, x + 15, H - 59], fill=(27, 92, 240))
    draw.text((x + 26, H - 82), "trippick.pages.dev", font=font(FONT_NOTO, 26), fill=(226, 234, 244))

    OG.mkdir(parents=True, exist_ok=True)
    p = OG / job["og"]
    img.save(p, "JPEG", quality=88, optimize=True, progressive=True)
    return p


def main() -> int:
    pri = json.loads((ROOT / "data" / "photo_credits.json").read_text(encoding="utf-8"))
    for job in GUIDES:
        h = hero(job)
        o = og(job)
        print(f"  · {h.relative_to(ROOT)} {Image.open(h).size} {h.stat().st_size // 1024}KB")
        print(f"  · {o.relative_to(ROOT)} {Image.open(o).size} {o.stat().st_size // 1024}KB")
        pri["photos"][f"v60/{job['slug']}"] = {
            "source": "위키미디어 공용",
            "file": job["file"],
            "page": job["page"],
            "artist": job["artist"],
            "license": job["license"],
            "place": job["place"],
            "alt": job["alt"],
        }
    (ROOT / "data" / "photo_credits.json").write_text(
        json.dumps(pri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
