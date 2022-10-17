from __future__ import print_function, annotations

from abc import ABC
from enum import Enum

import typing
import attr
import copy

from .urls import Urls, COUNTRY_USA
from .utils import request_json

from fuzzywuzzy import fuzz


def converter_splitlist(val: str) -> typing.List[str]:
    return val.split(",")


def lazy_float_convert(val: str) -> float:
    try:
        return float(val)
    except ValueError:
        return 0.0


@attr.dataclass
class MenuItem(ABC):
    code: str
    name: str

    def pprint(self) -> str:
        ...


@attr.dataclass
class Side(MenuItem):
    availability: list
    description: str
    local: bool = attr.field(converter=attr.converters.to_bool)
    tags: typing.Dict[str, typing.Any]
    qty: int = 1

    def order(self, qty: int = 1) -> Side:
        cside = copy.deepcopy(self)
        cside.qty = qty
        return cside

    @classmethod
    def from_dict(cls, side_dict: typing.Dict[str, typing.Any]) -> Side:
        return Side(
            availability=side_dict["Availability"],
            code=side_dict["Code"],
            description=side_dict["Description"],
            local=side_dict["Local"],
            name=side_dict["Name"],
            tags=side_dict["Tags"],
        )

    @classmethod
    def build_all(
        cls, sides_dict: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Dict[str, Side]]:
        ret = {}
        for product_type in sides_dict:
            prod_dict = {product_type: {}}
            for data in sides_dict[product_type].values():
                side = Side.from_dict(side_dict=data)
                prod_dict[product_type].update({side.code: side})
            ret.update(prod_dict)
        return ret

    @classmethod
    def parse_default_sides(cls, ins: str):
        """
        Default sides need to be parsed, again annoyingly
        """
        sides = []
        for side_data in ins.split(","):
            side = side_data.split("=")[0]
            if side:
                sides.append(side)
        return sides


class ToppingCoverage(Enum):
    half = "1/2"
    full = "1/1"


class ToppingAmount(Enum):
    normal = "1"
    double = "2"


@attr.dataclass
class Topping(MenuItem):
    availability: list
    description: str
    local: bool = attr.field(converter=attr.converters.to_bool)
    tags: typing.Dict[str, typing.Any]
    coverage: ToppingCoverage = ToppingCoverage.full
    amount: ToppingAmount = ToppingAmount.normal

    def to_dict(self):
        return {self.code: {self.coverage.value: self.amount.value}}

    @classmethod
    def from_dict(cls, topping_dict: typing.Dict[str, typing.Any]) -> Topping:
        return Topping(
            availability=topping_dict["Availability"],
            code=topping_dict["Code"],
            description=topping_dict["Description"],
            local=topping_dict["Local"],
            name=topping_dict["Name"],
            tags=topping_dict["Tags"],
        )

    @classmethod
    def build_all(
        cls, toppings_dict: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Dict[str, Topping]]:
        ret = {}
        for product_type in toppings_dict:
            prod_dict = {product_type: {}}
            for data in toppings_dict[product_type].values():
                topping = Topping.from_dict(topping_dict=data)
                prod_dict[product_type].update({topping.code: topping})
            ret.update(prod_dict)
        return ret

    @classmethod
    def parse_codes_from_product(cls, data: str) -> typing.List[str]:
        """
        The available/default toppings fields annoyingly need to be parsed out as such
        """
        codes = []
        for item in data.split(","):
            code = item.split("=")[0]
            if code:
                codes.append(code)
        return codes


@attr.dataclass
class Variant(MenuItem):
    flavor_code: str
    image_code: str
    local: bool = attr.field(converter=attr.converters.to_bool)
    price: float = attr.field(converter=float)
    product_code: str
    size_code: str
    tags: typing.Dict[str, typing.Any]
    allowed_cooking_instructions: str
    default_cooking_instructions: str
    prepared: bool = attr.field(converter=attr.converters.to_bool)
    pricing: typing.Dict[str, typing.Any]
    surcharge: float = attr.field(converter=float)
    options: typing.Dict[typing.Any, typing.Any] = {}
    qty: int = 1

    def pprint(self) -> str:
        return f"{self.name}: ${self.price:.2f}"

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        variant_dict = {
            "Code": self.code,
            "FlavorCode": self.flavor_code,
            "ImageCode": self.image_code,
            "Local": self.local,
            "Name": self.name,
            "Price": self.price,
            "ProductCode": self.product_code,
            "SizeCode": self.size_code,
            "Tags": self.tags,
            "AllowedCookingInstructions": self.allowed_cooking_instructions,
            "DefaultCookingInstructions": self.default_cooking_instructions,
            "Prepared": self.prepared,
            "Pricing": self.pricing,
            "Surcharge": self.surcharge,
            "Options": self.options,
            "Qty": self.qty
        }
        if self.options:
            variant_dict.update({"Options": self.options})
        return variant_dict

    @classmethod
    def from_dict(cls, variant_dict: typing.Dict[str, typing.Any]) -> Variant:
        return Variant(
            code=variant_dict["Code"],
            flavor_code=variant_dict["FlavorCode"],
            image_code=variant_dict["ImageCode"],
            local=variant_dict["Local"],
            name=variant_dict["Name"],
            price=variant_dict["Price"],
            product_code=variant_dict["ProductCode"],
            size_code=variant_dict["SizeCode"],
            tags=variant_dict["Tags"],
            allowed_cooking_instructions=variant_dict["AllowedCookingInstructions"],
            default_cooking_instructions=variant_dict["DefaultCookingInstructions"],
            prepared=variant_dict["Prepared"],
            pricing=variant_dict["Pricing"],
            surcharge=variant_dict["Surcharge"],
        )

    @classmethod
    def build_all(
        cls, variants_dict: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, Variant]:
        ret = {}
        for data in variants_dict.values():
            variant = Variant.from_dict(variant_dict=data)
            ret.update({variant.code: variant})
        return ret

    def add_topping(
        self, topping: Topping, coverage: ToppingCoverage, amount: ToppingAmount
    ):
        ctopping = copy.deepcopy(topping)  # Make a new topping
        ctopping.coverage = coverage
        ctopping.amount = amount
        self.options.update(ctopping.to_dict())


@attr.dataclass(frozen=True)
class Product(MenuItem):
    available_toppings: typing.Dict[str, Topping]
    available_sides: typing.Dict[str, Side]
    default_toppings: typing.Dict[str, Topping]
    default_sides: typing.Dict[str, Side]
    description: str
    image_code: str
    local: bool = attr.field(converter=attr.converters.to_bool)
    product_type: str
    tags: typing.Dict[str, typing.Any]
    variants: typing.Dict[str, Variant]

    def pprint(self) -> str:
        ret = f"{self.name}: ({self.product_type}) {self.description}\n"
        for variant in self.variants.values():
            ret = f"{ret}\t{variant.pprint()}\n"
        return ret

    @classmethod
    def from_dict(
        cls,
        product_dict: typing.Dict[str, typing.Any],
        variants_dict: typing.Dict[str, Variant],
        toppings_dict: typing.Dict[str, typing.Dict[str, Topping]],
        sides_dict: typing.Dict[str, typing.Dict[str, Side]],
    ) -> Product:
        variants = {}
        product_type = product_dict["ProductType"]

        # Deal with variants
        for variant_code in product_dict["Variants"]:
            if variant_code in variants_dict.keys():
                variants.update({variant_code: variants_dict[variant_code]})

        # Deal with toppings
        avail_toppings = {}
        for topping_code in Topping.parse_codes_from_product(
            product_dict["AvailableToppings"]
        ):
            avail_toppings.update({topping_code: toppings_dict[product_type][topping_code]})
        default_toppings = {}
        for topping_code in Topping.parse_codes_from_product(
            product_dict["DefaultToppings"]
        ):
            default_toppings.update({topping_code: toppings_dict[product_type][topping_code]})

        # Deal with sides
        avail_sides = {}
        for side_code in product_dict["AvailableSides"].split(","):
            if side_code:
                avail_sides.update({side_code: sides_dict[product_type][side_code]})
        default_sides = {}
        for side_code in Side.parse_default_sides(product_dict["DefaultSides"]):
            default_sides.update({side_code: sides_dict[product_type][side_code]})

        return Product(
            available_toppings=avail_toppings,
            available_sides=avail_sides,
            code=product_dict["Code"],
            default_toppings=default_toppings,
            default_sides=default_sides,
            description=product_dict["Description"],
            image_code=product_dict["ImageCode"],
            local=product_dict["Local"],
            name=product_dict["Name"],
            product_type=product_type,
            tags=product_dict["Tags"],
            variants=variants,
        )

    @classmethod
    def build_all(
        cls,
        products_dict: typing.Dict[str, typing.Any],
        variants_dict: typing.Dict[str, Variant],
        toppings_dict: typing.Dict[str, typing.Dict[str, Topping]],
        sides_dict: typing.Dict[str, typing.Dict[str, Side]],
    ) -> typing.Dict[str, Product]:
        ret = {}
        for data in products_dict.values():
            product = Product.from_dict(
                product_dict=data,
                variants_dict=variants_dict,
                toppings_dict=toppings_dict,
                sides_dict=sides_dict,
            )
            ret.update({product.code: product})
        return ret

    def order(
        self,
        variant: Variant,
        toppings: typing.List[
            typing.Tuple[str, ToppingCoverage, ToppingAmount]
        ] = typing.List,
        qty: int = 1,
    ) -> Variant:
        # TODO: Sides
        variant = copy.deepcopy(self.variants[variant.code])  # Need a new copy of this
        variant.qty = qty
        for topping_code, topping_coverage, topping_amount in toppings:
            if topping_code not in self.available_toppings.keys():
                raise ValueError(
                    f"{topping_code} is not available for {self.name} ({self.code})"
                )
            variant.add_topping(
                topping=self.available_toppings[topping_code], amount=topping_amount, coverage=topping_coverage
            )
        return variant


@attr.dataclass
class PreconfiguredProduct(MenuItem):
    description: str
    size: str
    options: str
    referenced_product_code: str = ""
    tags: typing.Dict[str, typing.Any] = {}
    qty: int = 1
    options: typing.Dict[str, typing.Any] = {}

    def to_dict(self) -> dict:
        return {
            "Code": self.code,
            "Description": self.description,
            "Name": self.name,
            "Size": self.size,
            "Options": self.options,
            "ReferencedProductCode": self.referenced_product_code,
            "Tags": self.tags,
            "Qty": self.qty
        }

    def order(self, qty: int = 1) -> PreconfiguredProduct:
        # TODO: Sides
        cpreconf = copy.deepcopy(self)
        cpreconf.qty = qty
        return cpreconf

    @classmethod
    def from_dict(
        cls, preconf_product_dict: typing.Dict[str, typing.Any]
    ) -> PreconfiguredProduct:
        return PreconfiguredProduct(
            code=preconf_product_dict["Code"],
            description=preconf_product_dict["Description"],
            name=preconf_product_dict["Name"],
            size=preconf_product_dict["Size"],
            options=preconf_product_dict["Options"],
            referenced_product_code=preconf_product_dict["ReferencedProductCode"],
            tags=preconf_product_dict["Tags"],
        )

    @classmethod
    def build_all(
        cls, preconf_products_dict: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, PreconfiguredProduct]:
        ret = {}
        for data in preconf_products_dict.values():
            preconf_product = cls.from_dict(preconf_product_dict=data)
            ret.update({preconf_product.code: preconf_product})
        return ret


@attr.dataclass
class Coupon(MenuItem):
    image_code: str
    description: str
    price: float = attr.field(converter=lazy_float_convert)
    tags: typing.Dict[str, typing.Any]
    local: bool = attr.field(converter=attr.converters.to_bool)
    bundle: bool = attr.field(converter=attr.converters.to_bool)
    qty: int = 1

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "Code": self.code,
            "ImageCode": self.image_code,
            "Description": self.description,
            "Name": self.name,
            "Price": self.price,
        }

    @classmethod
    def from_dict(cls, coupon_dict: typing.Dict[str, typing.Any]) -> Coupon:
        return Coupon(
            code=coupon_dict["Code"],
            image_code=coupon_dict["ImageCode"],
            description=coupon_dict["Description"],
            name=coupon_dict["Name"],
            price=coupon_dict["Price"],
            tags=coupon_dict["Tags"],
            local=coupon_dict["Local"],
            bundle=coupon_dict["Bundle"],
        )

    @classmethod
    def build_all(
        cls, coupons_dict: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, Coupon]:
        ret = {}
        for data in coupons_dict.values():
            coupon = cls.from_dict(coupon_dict=data)
            ret.update({coupon.code: coupon})
        return ret


@attr.dataclass(frozen=True)
class Menu(object):
    """The Menu is our primary interface with the API.

    This is far and away the most complicated class - it wraps up most of
    the logic that parses the information we get from the API.

    Next time I get pizza, there is a lot of work to be done in
    documenting this class.
    """

    variants: typing.Dict[str, Variant]
    products: typing.Dict[str, Product]
    coupons: typing.Dict[str, Coupon]
    preconfigured_products: typing.Dict[str, PreconfiguredProduct]
    _all_toppings: typing.Dict[str, typing.Dict[str, Topping]]
    country: str = COUNTRY_USA

    def order_product(
        self,
        product_code: str,
        variant_code: str,
        toppings: typing.List[typing.Tuple[str, ToppingCoverage, ToppingAmount]] = typing.List,
        qty: int = 1
    ) -> Variant:
        return self.products[product_code].order(variant=self.variants[variant_code], toppings=toppings, qty=qty)

    def order_preconf_product(
        self,
        preconf_product_code: str,
        qty: int = 1
    ) -> PreconfiguredProduct:
        return self.preconfigured_products[preconf_product_code].order(qty=qty)

    def get_coupon(
        self,
        coupon_code: str
    ) -> Coupon:
        return copy.deepcopy(self.coupons[coupon_code])

    @classmethod
    def from_store(cls, store_id, lang="en", country=COUNTRY_USA) -> Menu:
        response = request_json(Urls(country).menu_url(), store_id=store_id, lang=lang)
        return cls.from_menu_dict(menu_data=response)

    @classmethod
    def from_menu_dict(
        cls, menu_data: typing.Dict[str, typing.Any], country: str = COUNTRY_USA
    ):
        variants = Variant.build_all(variants_dict=menu_data["Variants"])
        toppings = Topping.build_all(toppings_dict=menu_data["Toppings"])
        sides = Side.build_all(sides_dict=menu_data["Sides"])
        products = Product.build_all(
            products_dict=menu_data["Products"],
            variants_dict=variants,
            toppings_dict=toppings,
            sides_dict=sides,
        )
        coupons = Coupon.build_all(coupons_dict=menu_data["Coupons"])
        preconf_products = PreconfiguredProduct.build_all(
            preconf_products_dict=menu_data["PreconfiguredProducts"]
        )
        return Menu(
            variants=variants,
            products=products,
            coupons=coupons,
            preconfigured_products=preconf_products,
            country=country,
            all_toppings=toppings,
        )

    @property
    def product_types(self) -> typing.List[str]:
        prod_types = []
        for product in self.products.values():
            if product.product_type not in prod_types:
                prod_types.append(product.product_type)
        return prod_types

    def get_product_by_type(self, product_type: str) -> typing.List[Product]:
        products = []
        for product in self.products.values():
            if product.product_type.casefold() == product_type.casefold():
                products.append(product)
        return products

    def search(self, query: str, threshold: int) -> typing.List[Product]:
        products = []
        # Check the name, description, type for normal products
        for product in self.products.values():
            if fuzz.ratio(query.casefold(), product.name.casefold()) > threshold:
                products.append(product)
            elif (
                fuzz.ratio(query.casefold(), product.product_type.casefold())
                > threshold
            ):
                products.append(product)
            else:
                for word in product.description.split(" "):
                    if fuzz.ratio(query.casefold(), word.casefold()) > threshold:
                        products.append(product)
        # Check the name, description for preconfigured products
        for product in self.preconfigured_products.values():
            if fuzz.ratio(query.casefold(), product.name.casefold()) > threshold:
                products.append(product)
            else:
                for word in product.description.split(" "):
                    if fuzz.ratio(query.casefold(), word.casefold()) > threshold:
                        products.append(product)
        return products
