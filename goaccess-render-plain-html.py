#coding: utf-8

import os
import re
import json
import codecs
import argparse
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

# from jinja2 import Template
# template = Template(codecs.open('template.html', 'r', "utf-8").read())

def file_in_samedir(filename):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)

def shaded(seq):
	return "" if (seq%2 == 1) else "shaded"

def format_bytes(bytes_cnt):
	gb = 1024*1024*1024
	mb = 1024*1024
	kb = 1024
	if bytes_cnt > gb*10:
		return "%s GB" % round(bytes_cnt / (gb*1.0), 2)
	elif bytes_cnt > mb*10:
		return "%s MB" % round(bytes_cnt / (mb*1.0), 2)
	elif bytes_cnt > kb:
		return "%s KB" % round(bytes_cnt / (kb*1.0), 2)
	else:
		return "%s bytes" % bytes_cnt

def main(args):
	CRTDIR = os.path.dirname(os.path.abspath(__file__))

	env = Environment(
	    loader=FileSystemLoader(CRTDIR),
	    autoescape=select_autoescape(['html', 'xml'])
	)
	env.filters['shaded'] = shaded
	env.filters['format_bytes'] = format_bytes
	template = env.get_template('template.html')

	data = json.loads(codecs.open(args.input, "r", "utf-8").read().replace('"items": ', '"details": ').replace('HTTP/1.1\\N', 'HTTP/1.1\\\\N'))

	html = template.render(data=data, render_child=args.child, render_limit=args.limit, render_title=args.title)
	if args.style == "inline":
		html = html.replace('<!-- style here -->', "<style>%s</style>" % open(file_in_samedir('style.css'), 'r').read())
	else:
		html = html.replace('<!-- style here -->', '<link href="%s" rel="stylesheet" type="text/css" />' % (args.style))
	# compress
	html = re.sub(r'\n\s*', '', html)
	codecs.open(args.output, "w", "utf-8").write(html)

if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--input', dest='input', type=str, required=True, help='path of json file')
    argParser.add_argument('-o', '--output', dest='output', type=str, required=True, help='path of output html file')
    argParser.add_argument('-l', '--limit', dest='limit', type=int, default=100, help='limit of data rows in panel table, default 100')
    argParser.add_argument('-c', '--child', dest='child', default=False, action='store_true', help='whether generate the child items of a data row in panel table, default not')
    argParser.add_argument('-s', '--style', dest='style', type=str, default="inline", help='embed the css in html file with "inline"(default), or specify a path')
    argParser.add_argument('-t', '--title', dest='title', type=str, default="Server&nbsp;Statistics", help='the page title, default "Server Statistics"')
    args = argParser.parse_args()
    main(args)
