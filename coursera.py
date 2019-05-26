from lxml import etree
from bs4 import BeautifulSoup
import requests
import random
import argparse
import json

def get_cmd_params():
    parser = argparse.ArgumentParser()
    parser.add_argument('-size', type=int, default=20, help='Size list courses')
    params = parser.parse_args()

    if params.size <= 0:
        parser.error('Error value. Value must be greater than 0.')

    return params


def get_courses_list():

    url = 'https://www.coursera.org/sitemap~www~courses.xml'
    response = requests.get(url)
    xml = response.content
    nodes = etree.fromstring(xml)
    courses = [loc_node.text for url_node in nodes.getchildren()
               for loc_node in url_node.getchildren()]
    return courses


def get_course_info(course_url):
    response = requests.get(course_url)
    if not response.ok:
        return None
    print(response.content)
    soup = BeautifulSoup(response.content)

    _json = soup.find('script', type="application/ld+json")
    if _json:
        print(json.dumps(json.loads(_json.text), indent=4))
    name_course = soup.find('h1', attrs={
        'class': 'H2_1pmnvep-o_O-weightNormal_s9jwp5-o_O-fontHeadline_1uu0gyz '
                 'max-text-width-xl m-b-1s'
    }).text

    ball_tag = soup.find('span', attrs={
        'class': 'H4_1k76nzj-o_O-weightBold_uvlhiv-o_O-bold_1byw3y2 m-l-1s m-r-1 m-b-0'
        }
    )
    if ball_tag:
        ball = ball_tag.text
    else:
        ball = None

    start_tag = soup.find('div', id='start-date-string')
    if start_tag:
        start = start_tag.span.text
    else:
        start = None

    print(name_course)
    print(ball)
    print(start)


def output_courses_info_to_xlsx(filepath, courses):
    for course in courses:
        course_info = get_course_info(course)
        #print(course_info)




def main():
    filename = 'courses.xlsx'
    params = get_cmd_params()
    size = params.size
    courses = get_courses_list()

    output_courses_info_to_xlsx(filename, random.choices(courses, k=size))
    print(random.choices(courses, k=size))

if __name__ == '__main__':
    main()
