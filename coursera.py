from lxml import etree
from bs4 import BeautifulSoup
from datetime import datetime
from openpyxl import Workbook
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


def get_json_course(course_url):
    response = requests.get(course_url)
    if not response.ok:
        return None
    soup = BeautifulSoup(response.content)
    json_data_course = soup.find('script', type="application/ld+json")
    return json_data_course

def get_course_info(course_url):

    json_data_course = get_json_course(course_url)
    if not json_data_course:
        return None
    data_course = json.loads(json_data_course.text)
    bread_crumb_list, product, course = data_course["@graph"]

    name_url = course['url']
    name_course = course['name']
    language = course['inLanguage']
    start_date = datetime.strptime(course['hasCourseInstance']['startDate'], '%Y-%m-%d')
    end_date = datetime.strptime(course['hasCourseInstance']['endDate'], '%Y-%m-%d')
    delta = end_date-start_date
    weeks = round(delta.days/7)
    rating = product.get('aggregateRating', {}).get('ratingValue', '')

    return (
        name_url,
        name_course,
        language,
        start_date.strftime('%Y-%m-%d'),
        weeks,
        rating
    )


def output_courses_info_to_xlsx(filepath, courses):

    wb = Workbook()
    ws = wb.active
    ws.append(('URL', 'Name', 'Language', 'Start date', 'Weeks', 'Rating'))
    for course in courses:
        course_info = get_course_info(course)
        ws.append(course_info)

    wb.save(filepath)


def main():
    filename = 'courses.xlsx'
    params = get_cmd_params()
    size = params.size
    courses = get_courses_list()
    if size > len(courses):
        size = len(courses)
    output_courses_info_to_xlsx(filename, random.choices(courses, k=size))


if __name__ == '__main__':
    main()
