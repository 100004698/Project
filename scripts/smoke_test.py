import requests, sys
BASE='http://127.0.0.1:5000'

def main():
    try:
        r = requests.get(f'{BASE}/media', timeout=5)
        print('GET /media ->', r.status_code, 'items:', len(r.json()))
    except Exception as e:
        print('GET /media failed:', e)
        sys.exit(1)

    payload = {
        'name': 'SMOKE TEST ITEM',
        'publication_date': '2025-12-12',
        'author': 'SmokeTester',
        'category': 'Book'
    }
    try:
        r = requests.post(f'{BASE}/media', json=payload, timeout=5)
        print('POST /media ->', r.status_code, r.text)
        if r.status_code not in (200, 201):
            sys.exit(2)
        item = r.json()
        item_id = item.get('id')
        if not item_id:
            print('No id returned')
            sys.exit(3)
    except Exception as e:
        print('POST /media failed:', e)
        sys.exit(1)

    try:
        r = requests.delete(f'{BASE}/media/{item_id}', timeout=5)
        print('DELETE /media/{id} ->', r.status_code, r.text)
    except Exception as e:
        print('DELETE failed:', e)
        sys.exit(1)

    print('SMOKE TEST PASSED')

if __name__ == '__main__':
    main()
