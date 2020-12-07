#!/usr/bin/env python

import csv
import copy
import sys
import heapq
from itertools import combinations

SECTIONS = set()
PERSONS = set()
SLOTS = set()

class Person(object):
  pass

def read_input(fname):
  with open(fname) as tsv:
    reader = csv.reader(tsv, delimiter='\t')
    header = reader.next()
    for row in reader:
      person = Person()
      person.section = row[0]
      person.name = row[1] + row[2]
      person.avail = set()
      person.removed = set()
      for time in row[3].split(','):
        person.avail.add('Monday ' + time.strip())
      for time in row[4].split(','):
        person.avail.add('Tuesday ' + time.strip())
      for time in row[5].split(','):
        person.avail.add('Wednesday ' + time.strip())
      for time in row[6].split(','):
        person.avail.add('Thursday ' + time.strip())
      for time in row[7].split(','):
        person.avail.add('Friday ' + time.strip())
      for item in copy.copy(person.avail):
        if 'Not avail' in item:
          person.avail.remove(item)
      PERSONS.add(person)
      SECTIONS.add(person.section)
      SLOTS.update(person.avail)

def prioritize():
  slots = []
  for s in SLOTS:
    value = (len([p for p in PERSONS if s in p.avail]), s)
    heapq.heappush(slots, value)
  return slots

def method_by_removing_slots():
  # REMOVE time slots
  slots = prioritize()
  while len(SLOTS) > 9:
    n, s = heapq.heappop(slots)
    print 'REMOVING CANDIDATE slot', n, s
    skip = False
    for p in sorted(PERSONS):
      if len(p.avail) == 1 and s in p.avail:
        skip = True
    if skip:
      continue
    for p in sorted(PERSONS):
      p.avail.discard(s)
      p.removed.add(s)
    print 'REMOVING slot', n, s
    SLOTS.discard(s)
    slots = prioritize()

  print 'how man slots?', len(SLOTS)
  for p in sorted(PERSONS):
    if not p.avail:
      print p.name, 'has no slots', len(p.removed)


def brute_force_remove_slots():
  # ran this for 25 choose 9 possibilities, 123 of them had 2 people forced into a 'Not available' slot
  candidates = open('candidates', 'w')
  best = 1000

  i = 0
  for slots in combinations(SLOTS, 9):
    slots = set(slots)
    sys.stderr.write('\r')
    sys.stderr.write(str(i))
    sys.stderr.write('/2042975') # 25 choose 9

    # remove the chosen slots
    persons = copy.deepcopy(PERSONS)
    for s in SLOTS.difference(slots):
      for p in persons:
        p.avail.discard(s)

    # compute how many people won't fit
    count = len([p for p in persons if not p.avail])
    if count <= best:
      best = count
      candidates.write('%2d %s\n'%(count, slots))
      candidates.flush()
    sys.stderr.write('   %d'%count)

    i += 1
    sys.stderr.flush()

  candidates.close()


if __name__ == '__main__':
  read_input('survey.tsv')


  # NOTES

  # If we were to set priorities: (ideal)
  #  each slot has ~15 students, all from the same section
  #  heuristically prefer students with less availability elsewhere
  # How to anneal to fewer slots?

  # put people into a slot:
  # pick slot that has highest subscription
  # 1. prioritize people with low availablity elsewhere (15 people)
  # will reach a point where top N slots are full, but remaining can't fill, how to re-assign?
