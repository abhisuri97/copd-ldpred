import csv
import math


def line_to_dict(ln, obj):
    line = ln[0]
    line = line.split(' ')
    line = list(filter(lambda x: len(x) > 0, line))
    dict = {}
    for idx, s in enumerate(obj):
        dict[obj[idx]] = line[idx]
    return dict

def assoc_to_ssf(filepath, outputdir):
    arr = []
    obj = []
    with open(filepath) as tsvfile:
        reader = csv.reader(tsvfile)
        for idx, line in enumerate(reader):
            if (idx == 0):
                line = line[0]
                line = line.split(' ')
                line = list(filter(lambda x: len(x) > 0, line))
                obj = line
            else:
                line = line_to_dict(line, obj)
                if (line['P'] == 'NA' or line['OR'] == 'NA' or float(line['OR']) == 0):
                    continue
                dict = { 
                        'chr': 'chr{}'.format(line['CHR']), 
                        'pos': line['BP'],
                        'ref': line['A2'],
                        'alt': line['A1'],
                        'reffrq': float(line['F_A']) + float(line['F_U']),
                        'info': 1,
                        'rs': line['SNP'],
                        'pval': line['P'], 
                        'effalt': math.log(float(line['OR']))
                        }
                arr.append(dict)

    with open('{}/sum_stat_fmt.txt'.format(outputdir), 'w') as writefile:
        fieldnames = ['chr', 'pos', 'ref', 'alt', 'reffrq', 'info', 'rs', 'pval', 'effalt']
        writer = csv.DictWriter(writefile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for a in arr:
            writer.writerow(a)
