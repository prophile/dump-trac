from xmlrpc.client import ServerProxy as TracAPI
from getpass import getpass
import yaml

HOST = 'www.studentrobotics.org'

URL = 'https://{host}/trac/xmlrpc'.format(un=quote(username),
                                          pw=quote(password),
                                          host=HOST)

TRAC = TracAPI(URL)

def dump_wiki():
    pages = TRAC.wiki.getAllPages()

    def get_page_dump(n, c, page):
        print('Getting page {} ({} of {})'.format(page, n, c))
        major_info = TRAC.wiki.getPageInfo(page)
        records = {}
        for version in range(1, major_info['version'] + 1):
            info = TRAC.wiki.getPageInfo(page, version)
            record = {'author': info['author'],
                      'name': info['name'],
                      'comment': info['comment'],
                      'date': str(info['lastModified']),
                      'content': TRAC.wiki.getPage(page, version)}
            records[version] = record
        # TODO: dump attachments
        return records

    data = {page: get_page_dump(n + 1, len(pages), page) for n, page in enumerate(pages)}

    print('Dumping wiki data to wiki.yaml')

    with open('wiki.yaml', 'w') as f:
        yaml.dump(data, f)

def dump_tickets():
    valid_ids = TRAC.ticket.query('max=0')

    def get_ticket_dump(n, c, ticket):
        print('Getting ticket #{} ({} of {})'.format(ticket, n, c))
        _ticket_dup, _date, _eyes, basic_data  = TRAC.ticket.get(ticket)
        record = {'reporter': basic_data['reporter'],
                  'cc': ([] if not basic_data['cc']
                               else [x.strip() for x in basic_data['cc'].split(',')]),
                  'status': basic_data['status'],
                  'resolution': basic_data['resolution'] if basic_data['resolution'] else None,
                  'type': basic_data['type'],
                  'milestone': basic_data['milestone'] if basic_data['milestone'] else None,
                  'component': basic_data['component'] if basic_data['component'] else None,
                  'priority': basic_data['priority'],
                  'time': str(basic_data['time']),
                  'changed': str(basic_data['changetime']),
                  'description': basic_data['description'],
                  'keywords': ([] if not basic_data['keywords']
                                     else [x.strip() for x in basic_data['keywords'].split(',')]),
                  'owner': basic_data['owner'] if basic_data['owner'] else None}
        # TODO: dump attachments
        changes = []
        for change in TRAC.ticket.changeLog(ticket):
            date, user, *data = change
            change_record = {'date': str(date),
                             'user': user}
            for n in range(0, len(data), 4):
                what, old, new, _bees = data[n:n+4]
                change_record[what] = new
            changes.append(change_record)
        record['changes'] = changes
        try:
            yaml.dump(record)
        except TypeError:
            print('Broken record on ticket {}: {}'.format(ticket, record))
            exit(1)
        return record

    data = {ticket: get_ticket_dump(n + 1, len(valid_ids), ticket) for n, ticket in enumerate(valid_ids)}

    print('Dumping ticket data to tickets.yaml')

    with open('tickets.yaml', 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

#dump_wiki()
dump_tickets()

# TODO: dump tickets
# ticket.query(max=0) gives all ticket IDs
# ticket.listAttachments(ticket) gives (filename, desc, size, time, author) for ticket attachments
# ticket.get(ticket) gives main ticket information

