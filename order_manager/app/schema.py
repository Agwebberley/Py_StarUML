import graphene
from graphene_django.types import DjangoObjectType

class Query(graphene.ObjectType):


class OrderType(DjangoObjectType):
    class Meta:
        model = Order

    all_orders = graphene.List(OrderType)
    def resolve_all_orders(self, info, **kwargs):
        return Order.objects.all()



class Order_itemType(DjangoObjectType):
    class Meta:
        model = Order_item

    all_order_items = graphene.List(Order_itemType)
    def resolve_all_order_items(self, info, **kwargs):
        return Order_item.objects.all()



class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

    all_customers = graphene.List(CustomerType)
    def resolve_all_customers(self, info, **kwargs):
        return Customer.objects.all()



class PartType(DjangoObjectType):
    class Meta:
        model = Part

    all_parts = graphene.List(PartType)
    def resolve_all_parts(self, info, **kwargs):
        return Part.objects.all()

