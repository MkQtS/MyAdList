#!/usr/bin/python3
# Uniq and Merge options of domain level rules
# Todo: handle subdomains
# Usage: ./MDR.py tobeMDRed.txt

import os
import re
import sys

filename = sys.argv[1]
tempfile = f"{filename}.temp"
okOptions = {'omit','1p','3p','all','css','doc','document','font','image','important','inline-script','media','object','other','ping','popunder','popup','script','stylesheet','subdocument','third-party','websocket','xhr','xmlhttprequest','~css','~font','~image','~media','~object','~ping','~script','~stylesheet','~subdocument','~third-party','~xhr','~xmlhttprequest'}

with open(filename, 'r', encoding='utf-8') as inputfile, open(tempfile, 'a', encoding='utf-8', newline='\n') as outputfile:
	inputFilters = set(inputfile.readlines())
	handledFilters = set()
	resultFilters = set()
	domain_block_dict = {}
	domain_except_dict = {}

	for line in inputFilters:
		domainObj = re.match(r'^(\@\@)?\|\|([\w\.-]+)\^(\$[^/=]+)?$', line)
		if domainObj:
			if '^$' in line and '=' not in line:
				opts = line.strip().split('^$')[1].split(',')
			elif line.endswith('^\n'):
				opts = ['omit']

			if set(opts).issubset(okOptions):
				handledFilters.add(line)
				if not domainObj.group(1):
					target_dict = domain_block_dict
				else:
					target_dict = domain_except_dict

				domain = domainObj.group(2)
				if domain not in target_dict:
					target_dict[domain] = {}
				if 'options' not in target_dict[domain]:
					target_dict[domain]['options'] = set()

				for opt in opts:
					target_dict[domain]['options'].add(opt)

	def mergeOpts(optTuple):
		opts = set(optTuple)
		for opt in optTuple:
			if opt == 'omit':
				return {'omit'}
			elif opt == 'all':
				opts = {'all'}
			elif opt.startswith('~'):
				opts.discard(opt[1:])
		return opts

	for domain in list(domain_except_dict.keys()):
		domain_except_dict[domain]['options'] = mergeOpts(tuple(domain_except_dict[domain]['options']))
		mergedDomainRule = ''
		if 'omit' in domain_except_dict[domain]['options']:
			domain_block_dict.pop(domain, None)
			mergedDomainRule = '@@||' + domain + '^'
		else:
			mergedDomainRule = '@@||' + domain + ('^$' + ','.join(sorted(domain_except_dict[domain]['options'])))
		resultFilters.add(mergedDomainRule + '\n')

	for domain in list(domain_block_dict.keys()):
		domain_block_dict[domain]['options'] = mergeOpts(tuple(domain_block_dict[domain]['options']))
		mergedDomainRule = ''
		if 'omit' in domain_block_dict[domain]['options']:
			mergedDomainRule = '||' + domain + '^'
		else:
			mergedDomainRule = '||' + domain + ('^$' + ','.join(sorted(domain_block_dict[domain]['options'])))
		resultFilters.add(mergedDomainRule + '\n')

	outputfile.writelines(sorted((inputFilters - handledFilters).union(resultFilters)))

os.remove(filename)
os.rename(tempfile, filename)
