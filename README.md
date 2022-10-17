# pizzapi2


## Description


This is a Python wrapper for the Dominos Pizza API.

It's an improved version of [pizzapi](https://github.com/ggrammar/pizzapi), maintained by [ggrammar](https://github.com/ggrammar). Added topping support, better class organization, fuzzy string matching when searching for items

## Quick Start


Pull the module into your namespace:

```python3
from pizzapi2 import *
```

First, construct a `Customer` object and set the customer's address:

```python3
customer = Customer("Bernie", "Sanders", " bsanders@berniesanders.com", "8028620697")
address = Address("1 Church St., 3rd Floor", "Burlington", "VT", "05401")
```
Then, find a store that will deliver to the address.

```python3
store = address.closest_store()
```
In order to add items to your order, you'll need the items' product and variant codes.
To find the codes, get the menu from the store, then search for items you want to add.
You can do this by asking your ``Store`` object for its ``Menu``.

```python3
menu = store.get_menu()
```

After you've found your items' product and variant codes, you can create an ``Order`` object add add your items:

```python3
# Add a 
# - build your own pizza (S_PIZZA)
# - 14 inch (large) variant (14SCREEN)
# - Add sausage, full coverage, normal amount
# - Add jalepenos, full coverage, normal amount
# - Add mushrooms, full coverage, normal amount
variant = m.order_product(product_code="S_PIZZA",
                          variant_code="14SCREEN",
                          toppings=[("S", ToppingCoverage.full, ToppingAmount.normal),
                                    ("J", ToppingCoverage.full, ToppingAmount.normal),
                                    ("M", ToppingCoverage.full, ToppingAmount.normal)])
# Get a coupon for a 16.99 large 3 topping
coupon = m.get_coupon(coupon_code="9012")

# Create an order
order = Order(store=store, customer=customer, address=address)

# Add your pizza
order.add_item(item=variant)

# Add your coupon
order.add_coupon(coupon=coupon)
```
Wrap your credit card information in a `PaymentObject`:
```python3
card = PaymentObject('4815772389572640', '0529', '98123', '05401')
```
And that's it! Now you can place your order.

```python3
order.place(card)
```

Or if you're just testing and don't want to actually order something, use `.pay_with`.
```python3
order.pay_with(card)
```
