import io
path = '/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/query-cosientist.md'
with io.open(path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'run159A' in line:
            print(f'line {i}: {line[:400]}')
            break
    else:
        print('NOT FOUND')
