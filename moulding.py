from sql import SQL
import kiln
import cumixl
import utils
import math
#toto while instead of if

NO_KILNS = 8

CUT_OFF_LIMIT = [0.06,0.025]

def fill_simulated_shelf(shelf, firing_cycle, size):
	fraction = 1.0
	shelf_state = {}
	with SQL() as sql:
		orders = sql.get_orders_for_cycle(shelf, firing_cycle, mode='LEFT_TO_SIMULATE')
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
				shelf_state[x[0]] = x[2] - nos_left
				sql.update_order_column_value(order_id=x[0], value=nos_left, col='LEFT_TO_SIMULATE')
		return shelf_state, fraction


def fill_simulated_kiln(size):
	kiln_state = []
	wasted_fraction = []
	firing_cycle = SQL().get_best_firing_cycle(mode='LEFT_TO_SIMULATE')
	for x in range(1,8):
		state, fraction = fill_simulated_shelf(x, firing_cycle, size)
		kiln_state.append(state)
		wasted_fraction.append(fraction)
		with SQL() as sql:
			for a,b in state.iteritems():
				sql.add_to_moulding_order(a,b)



def simulate_moulding():
	next_kiln = SQL().get_setting('LAST_SIMULATED_KILN_USED')

	while SQL().left_to_simulate(): 
		miss = 0
		while True:
			if miss >= NO_KILNS:
				with SQL() as s:
					s.update_kiln_simulation_data()
			next_kiln =  kiln.get_next_kiln(next_kiln)
			params  =  SQL().get_kiln_params(next_kiln)
			print next_kiln, 'KILN'
			if int(params[2]) > 0:
				miss = 0
				break
			else:
				miss+=1
		fill_simulated_kiln(params[3])
		with SQL() as s:
			s.update_kiln_column_value(next_kiln, 'SIMULATED_RUNS_LEFT', int(params[2]) - 1 )
	
	with SQL() as s:
		s.update_setting('LAST_SIMULATED_KILN_USED',next_kiln)


def mould_wheels():
	with SQL() as sql:
		orders = sql.get_moulding_order()
		for x in range(0,40):
			sql.add_to_order_moulded_qty(order_id=orders[x][0], qty=orders[x][1])
