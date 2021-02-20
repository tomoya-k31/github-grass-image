import os
import sys

import cairosvg
import lxml.etree as et
import requests
from scrapy.http import HtmlResponse


def main() -> None:
    input_github_accounts = os.getenv('INPUT_GITHUBACCOUNTS')
    if not input_github_accounts:
        sys.exit('inputs:github_accounts is required.')

    github_accounts = [x.strip() for x in input_github_accounts.split(',') if x.strip()]
    res_output_paths = []

    session = requests.session()
    for github_account in github_accounts:
        url = f'https://github.com/{github_account}'
        github_page = session.get(url)
        if not github_page:
            continue

        response = HtmlResponse(url=url, body=github_page.text, encoding='utf-8')
        svg_elm = response.xpath("//svg[@class='js-calendar-graph-svg']").get()
        svg_tree = et.fromstring(svg_elm)

        width = int(svg_tree.attrib["width"])
        height = int(svg_tree.attrib["height"])

        # /svg
        svg_tree.attrib['xmlns'] = 'http://www.w3.org/2000/svg'
        svg_tree.attrib['width'] = str(width + 2)
        svg_tree.attrib['height'] = str(height + 2)
        del svg_tree.attrib['class']

        # /svg/rect
        bg = et.Element('rect')
        bg.attrib['width'] = str(width + 2)
        bg.attrib['height'] = str(height + 2)
        bg.attrib['x'] = '0'
        bg.attrib['y'] = '0'
        bg.attrib['fill'] = '#ffffff'
        bg.attrib['stroke'] = 'none'
        svg_tree.insert(0, bg)

        # /svg/g
        for svg_g in svg_tree.xpath('/svg/g'):
            svg_g.attrib['transform'] = 'translate(14, 24)'  # base: translate(10, 20)
            svg_g.attrib['font-family'] = 'Helvetica sans-serif'
            svg_g.attrib['font-size'] = '11'
            del svg_g.attrib['data-hydro-click']
            del svg_g.attrib['data-hydro-click-hmac']

        # /svg/g//text
        for text in svg_tree.xpath("//text[@class='ContributionCalendar-label']"):
            del text.attrib['class']

        # /svg/g//rect
        for rect in svg_tree.xpath("//rect[@class='ContributionCalendar-day']"):
            level = rect.attrib['data-level']
            if level == '0':
                rect.attrib['fill'] = '#eeeeee'
            elif level == '1':
                rect.attrib['fill'] = '#d6e685'
            elif level == '2':
                rect.attrib['fill'] = '#8cc665'
            elif level == '3':
                rect.attrib['fill'] = '#44a340'
            elif level == '4':
                rect.attrib['fill'] = '#1e6823'

            del rect.attrib['class']
            del rect.attrib['data-date']
            del rect.attrib['data-level']

        svg_bytes = et.tostring(svg_tree)

        # output png
        local_output_path = f'./out/{github_account}.png'
        cairosvg.svg2png(bytestring=svg_bytes.decode('utf-8'), write_to=local_output_path)

        # output paths for docker volumes
        output_dir = os.getenv('INPUT_IMAGEOUTPUTDIR', './out')
        res_output_path = f'{output_dir}/{github_account}.png'
        res_output_paths.append(res_output_path)

    # [github actions] outputs
    print(f'::set-output name=githubGrassOutputImagePath::{",".join(res_output_paths)}')


if __name__ == "__main__":
    main()
