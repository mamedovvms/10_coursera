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


def get_html_content(url):
    response = requests.get(url)
    if response.ok:
        return response.content
    else:
        return None


def get_courses_list(xml_courses):
    nodes = etree.fromstring(xml_courses)
    courses = [loc_node.text for url_node in nodes.getchildren()
               for loc_node in url_node.getchildren()]
    return courses


def get_json_course(html_content):
    soup = BeautifulSoup(html_content)
    data_course = soup.find('script', type="application/ld+json")
    if data_course:
        return data_course.text


def get_course_info(json_data_course):

    if not json_data_course:
        return None

    data_course = json.loads(json_data_course)
    bread_crumb_list, product, course = data_course["@graph"]

    url = course['url']
    name_course = course['name']
    language = course['inLanguage']
    start_date = datetime.strptime(course['hasCourseInstance']['startDate'], '%Y-%m-%d')
    end_date = datetime.strptime(course['hasCourseInstance']['endDate'], '%Y-%m-%d')
    delta = end_date-start_date
    weeks = round(delta.days/7)
    rating = product.get('aggregateRating', {}).get('ratingValue', '')

    return {
        'url': url,
        'name': name_course,
        'language': language,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'training_period': weeks,
        'rating': rating
    }


def get_courses_info(courses):
    for course_url in courses:
        course_html = get_html_content(course_url)
        course_json = get_json_course(course_html)
        course_info = get_course_info(course_json)
        if course_info:
            yield course_info


def output_courses_info_to_xlsx(filepath, courses_info):

    wb = Workbook()
    ws = wb.active

    for course_info in courses_info:
        try:
            ws.append([
                course_info['url'],
                course_info['name'],
                course_info['language'],
                course_info['start_date'],
                course_info['training_period'],
                course_info['rating'] if course_info['rating'] else '-'
            ])
        except:
            a= 1

    wb.save(filepath)


def main():

    url_courses_xml = 'https://www.coursera.org/sitemap~www~courses.xml'
    filename = 'courses.xlsx'
    params = get_cmd_params()
    size = params.size

    xml_courses = get_html_content(url_courses_xml)
    courses = get_courses_list(xml_courses)

    if size > len(courses):
        size = len(courses)

    courses_info = get_courses_info(random.choices(courses, k=size))

    output_courses_info_to_xlsx(filename, courses_info)


if __name__ == '__main__':
    main()
