import typing

from .menu import ToppingAmount, ToppingCoverage, Menu, Variant, PreconfiguredProduct
from .order import Order
from .customer import Customer
from .address import Address
from .payment import PaymentObject
from .utils import yesno
from .store import Store


def build_customer() -> Customer:
    correct = False
    c = None
    while not correct:
        fname = input("First Name: ")
        lname = input("Last Name: ")
        email = input("Email: ")
        phone = input("Phone Number: ")
        c = Customer(fname=fname, lname=lname, email=email, phone=phone)
        print(f"Customer:\n{c}\nIs this correct?")
        correct = yesno()
    return c


def build_address() -> Address:
    correct = False
    a = None
    while not correct:
        street = input("Street: ")
        city = input("City: ")
        region = input("State (Region): ")
        zipcode = input("Zip Code: ")
        a = Address(street=street, city=city, region=region, zip=zipcode)
        print(f"Address:\n{a}\nIs this correct?")
        correct = yesno()
    return a


def build_menu(address: Address, ignore_closed: bool = True) -> typing.Tuple[Menu, Store]:
    print(f"Getting the closest store to {address}...")
    store = address.closest_store(ignore_closed=ignore_closed)
    print(f"Found store! {store.details_str()}")
    print("Fetching menu...")
    return store.get_menu(), store


def select_products(menu: Menu) -> typing.Tuple[typing.List[Variant], typing.List[PreconfiguredProduct]]:
    # Show the whole menu, shortform, organized by product type
    variants = []
    preconf_products = []
    # User choice: show category/show whole menu/add item to order/remove item from order/done
    # Show category: dump category products to terminal, goto User Choice
    # Show whole menu: dump whole menu to terminal, goto User Choice
    # Add item: Input product code, input variant code, pick toppings, pick quantity. Add to order. Goto UserChoice
    # Remove item: User chooses which to remove. Goto user choice
    # Done: print order, ask user to confirm. Return if yes, goto UserChoice if no
    return variants, preconf_products


def main():
    customer = build_customer()
    address = build_address()
    menu, store = build_menu(address=address)
    variant = menu.order_product(product_code="S_PIZZA",
                              variant_code="14SCREEN",
                              toppings=[("S", ToppingCoverage.full, ToppingAmount.normal),
                                        ("J", ToppingCoverage.full, ToppingAmount.normal),
                                        ("M", ToppingCoverage.full, ToppingAmount.normal)])
    coupon = menu.get_coupon(coupon_code="9012")
    order = Order(store=store, customer=customer, address=address)
    order.add_item(item=variant)
    order.add_coupon(coupon=coupon)
    return
    card = PaymentObject('4815772389572640', '0529', '98123', '05401')
    response = order.pay_with(card)
    # exit(0) if cli() else exit(1)


if __name__ == "__main__":
    main()