from sql import SQL
import cumixl
import utils
import math


KLIN_USE_ORDER = [1,6,7,8,2,5,3,4]
CUT_OFF_LIMIT = [0.08,0.06]

def get_next_kiln(kiln):
	old_index = KLIN_USE_ORDER.index(int(kiln))
	new_index = (old_index + 1)%len(KLIN_USE_ORDER)
	return KLIN_USE_ORDER[new_index]


def fill_shelf(shelf, firing_cycle, size):
	fraction = 1.0
	shelf_state = []
	with SQL() as sql:
		orders = sql.get_orders_for_cycle(shelf, firing_cycle, mode='MOULDED')
		for x in orders:
			if fraction < CUT_OFF_LIMIT[size]:
				break

			if utils.is_order_shelf_compatible(shelf, x[3]):
				nos = cumixl.get_wheels_per_base(dia=x[1], base_size=size, shelf_no=shelf, bond=x[4])
				nos_left = x[2]
				pile_size = utils.pile_size(bond=x[4], thickness=x[5])
				no_piles = float(nos_left)/pile_size
				no_whole_piles = int(math.ceil(no_piles))

				i = 0
				for _ in range(no_whole_piles):
		
					if fraction > CUT_OFF_LIMIT[size]:
						fraction = fraction - 1.0/nos
						i+=1
					else:	
						break
				nos_left = no_piles - i

				if nos_left >0:
					nos_left = int(math.ceil(nos_left * pile_size))
				else:
					nos_left = 0
				shelf_state.append([x[0], (x[2] - nos_left), pile_size])
				sql.update_order_column_value(order_id=x[0], value=nos_left, col='MOULDED')
		return shelf_state, fraction


def fill_kiln(size):
	kiln_state = []
	wasted_fraction = []
	firing_cycle = SQL().get_best_firing_cycle(mode='MOULDED')
	for x in range(1,8):
		state, fraction = fill_shelf(x, firing_cycle, size)
		kiln_state.append(state)
		wasted_fraction.append(fraction)
	#print kiln_state, wasted_fraction
	return kiln_state



def fire_wheels():
	next_kiln = SQL().get_setting('LAST_REAL_KILN_USED')
	while True:
		next_kiln =  get_next_kiln(next_kiln)
		params  =  SQL().get_kiln_params(next_kiln)
		if int(params[1]) > 0:
			break
	fill_kiln(params[3])
	with SQL() as s:
		s.update_kiln_column_value(next_kiln, 'RUNS_LEFT', int(params[2]) - 1 )
	
	with SQL() as s:
		s.update_setting('LAST_REAl_KILN_USED',next_kiln)