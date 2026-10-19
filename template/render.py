"""Render 5 card-news PNGs from a content.json using template.html.

Usage: python3 template/render.py posts/YYYY-MM-DD/content.json
Outputs card_01.png ... card_05.png next to content.json and a
contact sheet preview.png for quick review.
"""
import asyncio, json, sys, pathlib
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).resolve().parent


async def main(content_path):
    content_path = pathlib.Path(content_path).resolve()
    out_dir = content_path.parent
    content = json.loads(content_path.read_text(encoding="utf-8"))
    env = Environment(loader=FileSystemLoader(str(HERE)))
    html = env.get_template("template.html").render(content=content)
    html_path = out_dir / "cards.html"
    html_path.write_text(html, encoding="utf-8")

    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        await pg.goto(html_path.as_uri())
        await pg.wait_for_timeout(500)
        # overflow check: any card whose content spills past the footer
        overflow = await pg.evaluate("""() => [...document.querySelectorAll('.card')].map(c => {
            const limit = c.getBoundingClientRect().bottom - 115;  // footer text starts ~1235px
            const kids = [...c.querySelectorAll('h1,h2,p,.row,.chip,.cta-box,.icons')];
            return kids.some(k => k.getBoundingClientRect().bottom > limit) ? c.id : null;
        }).filter(Boolean)""")
        for i in range(1, 6):
            await pg.locator(f"#c{i}").screenshot(path=str(out_dir / f"card_0{i}.png"))
        await b.close()

    from PIL import Image
    ims = [Image.open(out_dir / f"card_0{i}.png").resize((432, 540)) for i in range(1, 6)]
    sheet = Image.new("RGB", (432 * 5 + 40, 540), "white")
    for i, im in enumerate(ims):
        sheet.paste(im, (i * 442, 0))
    sheet.save(out_dir / "preview.png")
    if overflow:
        print("OVERFLOW on cards:", ", ".join(overflow), "- shorten the text and re-render")
        sys.exit(2)
    print("OK", out_dir)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
