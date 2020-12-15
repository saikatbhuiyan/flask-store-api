import os
from typing import List

from db import db


items_to_orders = db.Table(
    "items_to_orders",
    db.Column("item_id", db.Integer, db.ForeignKey("items.id")),
    db.Column("order_id", db.Integer, db.ForeignKey("orders.id"))
)


class OrderModel(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)

    items = db.relationship("ItemModel", secondary=items_to_orders, lazy="dynamic")

    @classmethod
    def find_all(cls) -> List["OrderModel"]:
        return cls.query.all()

    @classmethod
    def find_by_id(cls, _id: int) -> "OrderModel":
        return cls.query.filter_by(id=_id).first()

    def set_status(self, new_status: str) -> None:
        """
        Sets the new status for the order and saves to the database—so that an order is never not committed to disk.
        :param new_status: the new status for this order to be saved.
        """
        self.status = new_status
        self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()