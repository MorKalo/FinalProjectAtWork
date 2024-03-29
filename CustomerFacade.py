import logging
from BaseFacade import BaseFacade
from Db_config import local_session, create_all_entities
from DbRepo import DbRepo
from Administrator import Administrator
from Flight import Flight
from Customer import Customer
from Ticket import Ticket
from FlightNotFound import FlightNotFound
from NoMoreTicketsForFlightsException import NoMoreTicketsForFlightsException
from TicketNotFoundException import TicketNotFoundException


class CustomerFacade(BaseFacade):

    def __init__(self):
        self.repo=DbRepo(local_session)


    def update_customer(self, customer):#func check + log
        self.repo.print_to_log(logging.DEBUG, f'update customer is about to happen')
        if not isinstance(customer.id, int):
            print('Customer ID must to be integer')
            self.repo.print_to_log(logging.ERROR,
                                   f'--FAILED--  {customer.id} must be INTEGER')
            return
        if customer.id <= 0 :
            print('Customer ID must to be positive')
            self.repo.print_to_log(logging.ERROR,
                                   f'--FAILED--  {customer.id} must be POSITIVE')
            return
        original_customer = self.repo.get_by_condition(Customer, lambda query: query.filter(Customer.id == customer.id).all())
        if not original_customer:
            print('Failed, we cant find customer with this ID number.')
            self.repo.print_to_log(logging.ERROR,
                               f'--FAILED--  {customer.id} we cant find customer with this ID number')
            return
        #trying to find this customer in Customer, and to check if there isnt another customer with does deatils:
        #Phone number
        if self.repo.get_by_condition(Customer,
                                      lambda query: query.filter(Customer.phone_number == customer.phone_number).all()) and \
                self.repo.get_by_condition(Customer, lambda query: query.filter(
                    Customer.phone_number == customer.phone_number).all()) != original_customer:
            print('Failed, a customer with this phone number is already exists.')
            self.repo.print_to_log(logging.ERROR,
                                   f'--FAILED--  {customer.id} a customer with the same Phone number {customer.phone_number}'
                                   f'is alredy exists.')
            return
        #Credit-Card number
        if self.repo.get_by_condition(Customer,
                                      lambda query: query.filter(Customer.cradit_card_no == customer.cradit_card_no).all()) and \
                self.repo.get_by_condition(Customer, lambda query: query.filter(
                    Customer.cradit_card_no == customer.cradit_card_no).all()) != original_customer:
            print('Failed, a customer with this credit card number is already exists.')
            self.repo.print_to_log(logging.ERROR,
                                   f'--FAILED--  {customer.id} a customer with the Credit card  number {customer.cradit_card_no}'
                                   f'is alredy exists.')
            return
        self.repo.update_by_id(Customer, Customer.id, customer.id, {Customer.first_name: customer.first_name, Customer.last_name: customer.last_name,
                                                                    Customer.address: customer.address, Customer.phone_number: customer.phone_number,
                                                                    Customer.cradit_card_no: customer.cradit_card_no})
        self.repo.print_to_log(logging.INFO,
                           f'--Sucsses--  customer id  {customer.id}  update details:'
                           f' {customer}')

    # CHECK: func + log
    def add_ticket(self, ticket):#Need to input object of ticket, with flight_id & customer_id
        self.repo.print_to_log(logging.DEBUG, f'adding ticket is about to happen')
        flight= self.repo.get_by_condition(Flight, lambda query: query.filter(Flight.id==ticket.flight_id).all())
        #if flight num not exists:
        if not flight:
            self.repo.print_to_log(logging.ERROR, f'--FAILED--  customer id {ticket.customer_id} trying to add ticket for flight'
                                                  f' NO. {ticket.flight_id}, but we cant find this flight')
            raise FlightNotFound
        if flight[0].remaining_Tickets < 1:
            try:
                self.repo.print_to_log(logging.INFO, f'--FAILED--  customer id {ticket.customer_id} trying to add ticket for'
                                                     f' flight No. {ticket.flight_id} but no more tickets are available'
                                                     f' for this flight')
                raise NoMoreTicketsForFlightsException(ticket.flight_id)
            except NoMoreTicketsForFlightsException as e:
                print (e)
        customer = self.repo.get_by_condition(Customer, lambda query: query.filter(Customer.id == ticket.customer_id).all())
        if not customer:
            print('Failed, we cant find customer with this ID number.')
            self.repo.print_to_log(logging.ERROR,
                               f'--FAILED--  {ticket.customer_id} we cant find customer with this ID number.')
        if self.repo.get_by_condition(Ticket, lambda query: query.filter(Ticket.customer_id == ticket.customer_id,
                                                                         Ticket.flight_id == ticket.flight_id).all()):
            print('Failed, this customer already heve ticket for this flight.')
            self.repo.print_to_log(logging.ERROR,
                                   f'--FAILED-- customer id {ticket.customer_id} already heve ticket for this flight number {ticket.flight_id}.')
            return
        else:
            flight[0].remaining_Tickets -=1
            self.repo.add(ticket)
            self.repo.print_to_log(logging.INFO, f'--SUCCESS--  adding ticket for customer id  {ticket.customer_id} to flight {ticket.flight_id} is finish Successfully')
            self.repo.print_to_log(logging.DEBUG, f'there is more {flight[0].remaining_Tickets} ticket for flight {ticket.flight_id}')

    #CHECK: func + log ---cant get customer id for log---
    def remove_ticket(self, ticket): #FUNC BY ID
        self.repo.print_to_log(logging.DEBUG, f'removing ticket is about to happen.')
        ticket_exists = self.repo.get_by_condition(Ticket, lambda query: query.filter(Ticket.id == ticket).all())
        if not ticket_exists:
            self.repo.print_to_log(logging.ERROR,
                                   f'--FAILED--  customer id {Ticket.customer_id} trying to remove ticket id {ticket}'
                                   f'  but we cant find this ticket')
            raise TicketNotFoundException
        else:
            fullticket = self.repo.get_by_id(Ticket, ticket)
            flight = self.repo.get_by_condition(Flight,
                                                lambda query: query.filter(Flight.id == fullticket.flight_id).all())
            ticketforflight=flight[0].remaining_Tickets
            self.repo.update_by_id(Flight,ticket,{Flight.remaining_Tickets:ticketforflight+1})
            self.repo.delete(Ticket, ticket)
            self.repo.print_to_log(logging.INFO, f'--SUCCESS--  remove ticket for customer id  {Ticket.customer_id} to flight {ticket} is finish Successfully')
            self.repo.print_to_log(logging.DEBUG, f'there is more {flight[0].remaining_Tickets} ticket for flight {ticket}')

    # CHECK: func + log
    def get_tickets_by_customer(self, customer):#FUNC BY ID
        self.repo.print_to_log(logging.DEBUG, f'start Get_tickets_by_customer func.')
        checkcustomer=self.repo.get_by_condition(Customer, lambda query: query.filter(Customer.id==customer).all())
        if not checkcustomer:
            print(f' Failed. We cant find this customer id')
            self.repo.print_to_log(logging.ERROR,
                               f'--FAILED-- we cant find customer id {customer}')
        else:
            self.repo.print_to_log(logging.INFO,
                       f'--SUCCESS--  get ticket by customer id  {customer} is finish Successfully')
            return self.repo.get_by_condition(Ticket, lambda query:query.filter(Ticket.customer_id==customer).all())








