import argparse
from pathlib import Path
import pandas as pd
import sys
import time
import json

from parser import read_all
from csp import solve
from evaluator import evaluate


def write_output(assignments, data, out_path: Path):
	# Desired columns: instructor_id, instructor_name, day, start, end, room, course_id, course_name
	rows = []
	for (cid, sid, sess), (tid, rid, iid) in assignments.items():
		course = data['courses'][cid]
		timeslot = data['timeslots'][tid]
		instr_id = iid or course.get('instructor', '')
		instr_name = data['instructors'].get(instr_id, {}).get('name', '')
		rows.append({
			'instructor_id': instr_id,
			'instructor_name': instr_name,
			'day': timeslot.get('day',''),
			'start': timeslot.get('start',''),
			'end': timeslot.get('end',''),
			'room': rid,
			'course_id': cid,
			'course_name': course.get('name','')
		})
	df = pd.DataFrame(rows)
	# simple day ordering: try to keep Monday..Sunday if days are strings
	day_order = {'monday':0,'tuesday':1,'wednesday':2,'thursday':3,'friday':4,'saturday':5,'sunday':6}
	def day_key(d):
		if not isinstance(d, str):
			return 999
		return day_order.get(d.strip().lower(), 999)
	df['__day_idx'] = df['day'].apply(day_key)
	# normalize time strings for sorting; prefer lexicographic if like '09:00' or '9:00 AM'
	def time_key(t):
		if not isinstance(t, str):
			return t
		return t
	df['__start_key'] = df['start'].apply(time_key)
	df = df.sort_values(['__day_idx','__start_key'])
	df = df.drop(columns=['__day_idx','__start_key'])
	out_path.parent.mkdir(parents=True, exist_ok=True)
	df.to_excel(out_path, index=False)


def main():
	p = argparse.ArgumentParser()
	p.add_argument('--instructors', required=False, default=None)
	p.add_argument('--rooms', required=False, default=None)
	p.add_argument('--courses', required=False, default=None)
	p.add_argument('--timeslots', required=False, default=None)
	p.add_argument('--out', required=False, default=None)
	args = p.parse_args()

	data_dir = Path('data')
	output_dir = Path('output')

	default_instructors = data_dir / 'instructors.xlsx'
	default_rooms = data_dir / 'rooms.xlsx'
	default_courses = data_dir / 'courses.xlsx'
	default_times = data_dir / 'timeslots.xlsx'
	default_out = output_dir / 'timetable_result.xlsx'

	instructors_path = Path(args.instructors) if args.instructors else default_instructors
	rooms_path = Path(args.rooms) if args.rooms else default_rooms
	courses_path = Path(args.courses) if args.courses else default_courses
	times_path = Path(args.timeslots) if args.timeslots else default_times
	out_path = Path(args.out) if args.out else default_out

	missing = []
	for pth in (instructors_path, rooms_path, courses_path, times_path):
		if not pth.exists():
			missing.append(str(pth))
	if missing:
		print('Error: the following expected input files are missing:')
		for m in missing:
			print('  -', m)
		print('\nPut your input Excel files into the `data/` folder with these names, or pass paths via CLI flags.')
		sys.exit(2)

	instructors, rooms, courses, timeslots, sections = read_all(instructors_path, rooms_path, courses_path, times_path, None)
	data = {'instructors': instructors, 'rooms': rooms, 'courses': courses, 'timeslots': timeslots, 'sections': sections}
	print('Data loaded: {} instructors, {} rooms, {} courses, {} timeslots'.format(len(instructors), len(rooms), len(courses), len(timeslots)))

	t0 = time.time()
	sol = solve(data)
	t1 = time.time()
	runtime = t1 - t0

	if sol is None:
		print('No solution found')
		return
	write_output(sol, data, out_path)
	print('Solution written to', out_path)
	metrics = evaluate(sol, data)
	metrics['solve_time_seconds'] = runtime
	out_metrics = out_path.parent / 'metrics.json'
	with open(out_metrics, 'w', encoding='utf-8') as fh:
		json.dump(metrics, fh, indent=2)
	print('Metrics written to', out_metrics)


if __name__ == '__main__':
	main()

