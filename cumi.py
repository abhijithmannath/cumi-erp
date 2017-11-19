import Tkinter as tk
from sql import SQL
import tkMessageBox
import datetime
import table
import utils
import cumixl
import moulding

MIN_DAYS_FOR_MANUFACTURING = 20
MIN_DAYS_MOULDING_VB = 6
MIN_DAYS_MOULDING = 10
AVG_WHEELS_MOULDED_PER_DAY = 30



class VerticalScrolledFrame(tk.Frame):


    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill='y', side='right', expand='FALSE')
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side='left', fill='both', expand='TRUE')
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor='nw')

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)



class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        tk.Button(self.parent, text='New Order', command=self.add_order, width=25).pack()
        tk.Button(self.parent, text='View Order', command=self.view_order, width=25).pack()
        tk.Button(self.parent, text='Moulding Schedule', command=self.show_moulding_schedule, width=25).pack()
        tk.Button(self.parent, text='Firing Schedule', command=self.show_firing_schedule, width=25).pack()
        #tk.Button(self.parent, text='Kiln Schedule', command=self.say_hello, width=25).pack()


    def add_order(self):
        AddOrderView(self.parent, width=1000, height=500)

    def view_order(self):
        ViewOrderView(self.parent, width=1000, height=500)

    def show_moulding_schedule(self):
        MouldingSchedule(self.parent)

    def show_firing_schedule(self):
        FiringSchedule(self.parent)


    def say_hello(self):
        print 'hi'


class FiringSchedule(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        import kiln
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.container = VerticalScrolledFrame(self, padx=5, pady=5)
        self.container.pack()
        self.title('Firing Sedule')
        kiln_state = kiln.fill_kiln(1)
        self.results_frame = []
        headers = table.DrawTable(self.container, 1,3)
        headers.pack(side="top", fill="x")
        headers_str = ['ORDER_ID','NOS','PILE SIZE']

        for x in range(3):
            headers.set(0,x,headers_str[x])
        i= 0    
        for x in kiln_state:
            self.results_frame.append(table.DrawTable(self.container, len(x),3))
            self.results_frame[i].pack()
            row = 0
            for y in x: # y is each row
                for col in range(0,3):
                    self.results_frame[i].set(row, col, y[col])
                row+=1
            i+=1





class AddMoulded(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.container = tk.Frame(self, padx=5, pady=5, relief='sunken')
        self._widgets = {}
        self.title('Add moulded')
        self.container.pack()
        tk.Label(self.container, text='ORDER ID').grid(row=0, column=0, padx=10, pady=10)
        self._widgets['order_id'] = tk.Entry(self.container, relief='raised')
        self._widgets['order_id'].grid(row=0,column=1, padx=10, pady=10)

        tk.Label(self.container, text='QTY').grid(row=0, column=2, padx=10, pady=10)
        self._widgets['qty'] = tk.Entry(self.container, relief='raised')
        self._widgets['qty'].grid(row=0,column=3, padx=10, pady=10)

        tk.Button(self.container,text='Add Moulded', command=self.add_moulded).grid(row=1, column=3, padx=5, pady=5)

    def add_moulded(self):
        order_id = self._widgets['order_id'].get()
        qty = self._widgets['qty'].get()

        self.destroy()


class MouldingSchedule(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.container = tk.Frame(self, padx=5, pady=5, relief='sunken')
        self.container.pack()
        self.results_frame = None
        self.title('Moulding Sedule')
        self._widgets = {}
        tk.Button(self.container,text='Add new Moulded', command=self.add_moulded).pack()

        headers = table.DrawTable(self, 1,2)
        headers.pack(side="top", fill="x")
        headers_str = ['Order ID', 'QTY']
        for x in range(2):
            headers.set(0,x,headers_str[x])
        self.update_results()

    def update_results(self):
        with SQL() as sql:
            orders = sql.get_moulding_order()
        if self.results_frame:
            self.results_frame.destroy()
            
        self.results_frame = table.DrawTable(self, len(orders),2)
        self.results_frame.pack(side="top", fill="x")
        
        row = 0
        for x in orders:
            for i in range(0,2):
                self.results_frame.set(row, i, x[i])
            row+=1


    def add_moulded(self):
        AddMoulded(self)
        



class ViewOrderView(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.search_frame = tk.Frame(self, padx=10,pady=10, relief='raised')
        self.search_frame.pack()
        self.title('View Order')
        self._widgets = {}
        self.results_frame = None


        tk.Label(self.search_frame, text='Order ID').grid(column=0)
        self._widgets['id'] = tk.Entry(self.search_frame, width=30)
        self._widgets['id'].grid(row=0,column=1, columnspan=1, padx=10)

        tk.Label(self.search_frame, text='Shipping Date b/w').grid(row=0,column=2)
        self._widgets['from_date'] = tk.Entry(self.search_frame, width=14)
        self._widgets['from_date'].grid(row=0,column=3, padx=10)

        self._widgets['to_date'] = tk.Entry(self.search_frame, width=14)
        self._widgets['to_date'].grid(row=0,column=4, padx=10)

        tk.Button(self.search_frame, text='Search', command=self.search_orders, width=10).grid(row=0, column=5,padx=10, pady=5, stick='s')

        self._widgets['results_count'] = tk.Label(self.search_frame, text='')
        self._widgets['results_count'].grid(row=1,columnspan=5, pady=10)
        
        headers = table.DrawTable(self, 1,10)
        headers.pack(side="top", fill="x")
        headers_str = ['Order ID', 'Outer Dia', 'Thickness', 'Bond', 'Ship Date', 'Entry Date', 'Qty', 'FNSO', 'MOULDED', 'FIRED']

        for x in range(10):
            headers.set(0,x,headers_str[x])

        self.bind('<Return>', self.search_orders)


    def search_orders(self, event=None  ):
        if self._widgets['id'].get() or self._widgets['from_date'].get() or self._widgets['to_date'].get():
            from_date = self._widgets['from_date'].get()
            to_date = self._widgets['to_date'].get()

            try:
                if from_date:
                    from_date = utils.reverse_date(from_date)
                if to_date:
                    to_date = utils.reverse_date(to_date)
            except Exception as e:
                print e
                tkMessageBox.showerror('Invalid Input', 'Date should be of the format dd-mm-yyyy')
                return 

            with SQL() as sql:
                orders = sql.view_orders(self._widgets['id'].get(), from_date, to_date)
            
            if self.results_frame:
                #self.grid_forget()
                self.results_frame.destroy()

            
            self._widgets['results_count'].configure(text=str(len(orders))+' results')
            self.results_frame = table.DrawTable(self, len(orders),10)
            self.results_frame.pack(side="top", fill="x")
            row = 0

            for x in orders:
                for i in range(0,10):
                    if i ==4 or i == 5:
                        self.results_frame.set(row, i, datetime.datetime.strptime(x[i],'%Y-%m-%d').strftime('%d-%m-%Y'))
                    else:
                        self.results_frame.set(row, i, x[i])

                row+=1
        else:
            tkMessageBox.showerror('Incomplete Input', 'Please Enter atleast one value')
            return
        

class AddOrderView(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.container = tk.Frame(self, padx=10,pady=10, relief='raised')
        self.container.pack()
        self.title('Add Order')
        input_var = ['Order ID','Outer Dia', 'Thickness','Bond','Shipping Date', 'Qty']
        self._widgets = {}
        i=j=0
        for x in input_var:
            tk.Label(self.container, text=x).grid(row=i,column=j,padx=2,pady=5)
            self._widgets[x] = tk.Entry(self.container, relief='raised')
            self._widgets[x].grid(row=i, column=j+1,padx=2,pady=5)
            j=(j+2)%4
            if j == 0:
                i+=2
        self._widgets['Shipping Date'].insert(0,'dd-mm-yyyy')



        tk.Button(self.container, text='Add', command=self.add_this_order, width=10).grid(row=i+1, column=3)
        tk.Button(self.container, text='Add Orders from File', command=self.add_orders_from_file,).grid(row=i+1, column=0)

    def add_orders_from_file(self):
        from tkFileDialog import askopenfilename
        filename =  askopenfilename()
        orders = cumixl.read_orders_from_sheet(filename)

        try:
            with SQL() as sql:
                for o in orders:
                    sql.add_order(*o)
        except Exception as e:
            print e
            tkMessageBox.showerror('Invalid Input', 'Either the the Order Sheet does not follow the template or the order already exists.')
        else:
            moulding.simulate_moulding()
            tkMessageBox.showinfo('Success!', 'All orders have been added')




    def add_this_order(self):
        try:
            ship_date = utils.reverse_date(self._widgets['Shipping Date'].get())
        except Exception as e:
            print e
            tkMessageBox.showerror('Invalid Input', 'Date should be of the form dd-mm-yy')
            return 
        ip = self._widgets
        with SQL() as sql:
            try:
                sql.add_order(ip['Order ID'].get(), ship_date, ip['Qty'].get(), ip['Outer Dia'].get(), ip['Thickness'].get(), ip['Bond'].get())
            except Exception as e:
                tkMessageBox.showerror('Order Not saved', 'Either the order already exists or one of the inputs are invalid')
            else:
                tkMessageBox.showinfo('Success', 'Order was successfully added')

        





if __name__ == '__main__':
    root = tk.Tk()
    root.config(cursor='hand1')
    MainApplication(root, height=200, width=1000,)
    root.title('CUMI Application')
    root.resizable(width=False, height=False)
    root.mainloop()
