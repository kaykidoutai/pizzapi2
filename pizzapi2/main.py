from pizzapi import ToppingAmount, ToppingCoverage
from pizzapi import Order
from pizzapi import Customer
from pizzapi import Address
from pizzapi import PaymentObject


# @click.group()
# def cli():
#     ...
#
#
# @cli.command()
# @click.option("--keyword", type=str, help="Item keyword to search for", required=True)
# @click.option("--street", type=str, help="Your street name", required=True)
# @click.option("--city", type=str, help="Your city name", required=True)
# @click.option("--state", type=str, help="Your state", required=True)
# @click.option("--zipcode", type=str, help="Your zipcode", required=True)
# def search(street: str, city: str, state: str, zipcode: str, keyword: str) -> bool:
#     search_product(
#         menu=closest_menu(street=street, city=city, region=state, zipcode=zipcode),
#         query=keyword,
#     )
#     return True


def main():
    customer = Customer("Bernie", "Sanders", " bsanders@berniesanders.com", "8028620697")
    address = Address("1 Church St., 3rd Floor", "Burlington", "VT", "05401")
    store = address.closest_store()
    m = store.get_menu()
    variant = m.order_product(product_code="S_PIZZA",
                              variant_code="14SCREEN",
                              toppings=[("S", ToppingCoverage.full, ToppingAmount.normal),
                                        ("J", ToppingCoverage.full, ToppingAmount.normal),
                                        ("M", ToppingCoverage.full, ToppingAmount.normal)])
    coupon = m.get_coupon(coupon_code="9012")
    order = Order(store=store, customer=customer, address=address)
    order.add_item(item=variant)
    order.add_coupon(coupon=coupon)
    card = PaymentObject('4815772389572640', '0529', '98123', '05401')
    response = order.place(card)
    # exit(0) if cli() else exit(1)


if __name__ == "__main__":
    main()