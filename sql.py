import sqlite3
import cumixl


class SQL:

    def __init__(self):
        self.conn = sqlite3.connect('cumi.db')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()

    


    def add_order(self, order_id, ship_date, qty, o_dia, thickness, bs):
        import datetime
        params = cumixl.get_bond_params(bs,o_dia)
        today = datetime.date.today().strftime('%Y-%m-%d')
        cmd = """INSERT INTO ORDERS (ORDER_ID,O_DIA,THICKNESS,BS,SHIP_DATE, ENTRY_DATE, QTY, FNSO, MOULDED, FIRED, LEFT_TO_SIMULATE,
         FIRING_CYCLE, COOLING_CYCLE, GREATER_THAN_SHELF, SHELF_EXCLUSIONS)
        VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s','%s','%s','%s','%s' )
        """%(order_id, o_dia, thickness, bs,ship_date,today, qty,qty,0,0, qty,params['FIRING_CYCLE'],params['COOLING_CYCLE'],params['GREATER_THAN_SHELF'],params['SHELF_EXCLUSIONS'])
        self.conn.execute(cmd)

    

    def view_orders(self, order_id, from_date, to_date):
        if order_id:
            cmd = """SELECT * FROM ORDERS WHERE ORDER_ID LIKE '%s%%' """%order_id

            if from_date:
                cmd += "and SHIP_DATE >= '%s' "%from_date
            if to_date:
                cmd += "and SHIP_DATE <= '%s' "%to_date
        elif from_date:
            cmd = "SELECT * FROM ORDERS WHERE SHIP_DATE >= '%s' "%from_date

            if to_date:
                cmd += "and SHIP_DATE <= '%s'"
        else:
            cmd = "SELECT * FROM ORDERS WHERE SHIP_DATE <= '%s' "%to_date
        cursor = self.conn.execute(cmd)
        return cursor.fetchall()

    

    def add_kiln_params(self, kiln_no, max_runs, size):
        cmd = """INSERT INTO KILNS (KILN, MAX_RUNS, SIZE, RUNS_LEFT, SIMULATED_RUNS_LEFT) VALUES ('%s','%s','%s','%s','%s')"""%(kiln_no, max_runs, size, max_runs, max_runs)
        self.conn.execute(cmd)

    

    def delete_kiln_data(self):
        self.conn.execute('DELETE FROM KILNS;')

    

    def get_best_firing_cycle(self, mode):
        import datetime
        import re
        cmd = ' WHERE %s > 0 '%mode
        cursor = self.conn.execute("""SELECT FIRING_CYCLE FROM ORDERS %s 
            GROUP BY FIRING_CYCLE ORDER BY COUNT(*) DESC ;"""%cmd).fetchall()
        try:
            val = cursor[0][0]
        except:
            return None
        match = re.search(r'([0-9]+)/([0-9]+)', val)
        if match:
            return [match.group(1), match.group(2)]
        else:
            return [val]

    

    def left_to_simulate(self):
        return int(self.conn.execute('select count(*) from orders where left_to_simulate > 0;').fetchall()[0][0])

    

    def get_setting(self, key):
        return self.conn.execute('''SELECT VALUE FROM SETTINGS WHERE KEY = '%s' ;'''%key).fetchall()[0][0]

    

    def update_setting(self, key, value):
        cmd = """UPDATE SETTINGS SET VALUE = '%s' WHERE KEY = '%s';"""%(value, key)
        self.conn.execute(cmd)

    

    def get_kiln_params(self, kiln):
        cmd = """SELECT MAX_RUNS, RUNS_LEFT,SIMULATED_RUNS_LEFT, SIZE FROM KILNS WHERE KILN == '%s' """%kiln
        cursor = self.conn.execute(cmd).fetchall()
        return cursor[0]

    

    def get_orders_for_cycle(self, shelf, firing_cycle, mode):
        if len(firing_cycle) == 2:
            cmd = """SELECT order_id, o_dia, {mode}, shelf_exclusions, bs, thickness FROM ORDERS WHERE 
            FIRING_CYCLE IN ('{cycle_1}','{cycle_2}','{cycle_1}/{cycle_2}')  AND {mode} > 0 AND 
            GREATER_THAN_SHELF <= {shelf} ORDER BY SHIP_DATE;""".format(mode=mode, cycle_1=firing_cycle[0], cycle_2=firing_cycle[1], shelf=shelf)
        else:
            cmd = """SELECT order_id, o_dia, %s, shelf_exclusions, bs, thickness FROM ORDERS WHERE FIRING_CYCLE = '%s' and %s > 0
            and GREATER_THAN_SHELF <= %s ORDER BY SHIP_DATE;"""%(mode, firing_cycle[0], mode, shelf)

        return self.conn.execute(cmd)

    
    def update_order_column_value(self, order_id, value, col):
        cmd = """UPDATE ORDERS 
            SET {col} = '{value}' WHERE ORDER_ID = '{order_id}';""".format(order_id=order_id, value=value, col=col)
        self.conn.execute(cmd)

    

    def add_to_moulding_order(self, order_id, qty):
        cmd = """INSERT INTO MOULDING (order_id, qty) VALUES ('%s','%s')"""%(order_id, qty)
        self.conn.execute(cmd)

    def get_moulding_order(self):
        cmd = """SELECT * FROM MOULDING;"""
        return self.conn.execute(cmd).fetchall()
    

    def update_kiln_column_value(self, kiln, col, value):
        cmd = """UPDATE KILNS 
            SET {col} = '{value}' WHERE kiln = '{kiln}';""".format(kiln=kiln, value=value, col=col)
        self.conn.execute(cmd)
    

    def update_kiln_simulation_data(self):
        cmd = """UPDATE kilns set simulated_runs_left = max_runs;"""
        self.conn.execute(cmd)

    def add_to_order_moulded_qty(self, order_id, qty):
        cmd = """UPDATE ORDERS SET MOULDED = MOULDED + %s WHERE ORDER_ID = '%s';"""%(qty, order_id)
        self.conn.execute(cmd)

    def update_kiln_data(self):
        cmd = """UPDATE kilns set runs_left = max_runs;"""
        self.conn.execute(cmd)

    
    def commit(self):
        self.conn.commit()

