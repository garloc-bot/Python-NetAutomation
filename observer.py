#!/usr/bin/env python

class BussinessCustomer:
    def __init__(self, acct_id, money_owed) :
        
        self.acct_id = acct_id
        self.money_owed = money_owed

    def update(self) :
        if self.money_owed > 0:
            print(f"{self.acct_id}: Tiene mayor a 0")
        else:
            print(f"{self.acct_id}: Pagado")
            

class AccountingSystem:

    def __init__(self) :
        
        self.customers = set()

    def register (self, customer) :

        self.customers.add (customer)

    def unregister (self, customer) :

        self.customers.remove (customer)

    def notify (self) :
        
        for customer in self.customers:
            customer.update()

def main() :
    
    cust1 = BussinessCustomer("Garlo", 10)
    cust2 = BussinessCustomer("Marilin", 0)
    cust3 = BussinessCustomer("Laura", -10)
    cust4 = BussinessCustomer("Victor", 20)

    accounting_sys = AccountingSystem()
    accounting_sys.register(cust1)
    accounting_sys.register(cust2)
    accounting_sys.register(cust3)
    accounting_sys.register(cust4)

    accounting_sys.notify()

    print("** El cliente Cust 2 a pagado su cuenta")
    accounting_sys.unregister(cust2)

    accounting_sys.notify()

if __name__ == "__main__":
    main()

