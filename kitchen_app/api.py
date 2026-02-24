import frappe
from frappe.utils import now_datetime

def handle_kitchen_order(doc, method):

    if not doc.is_pos:
        return
    
    if doc.pos_profile == "Kitchen Order":
        create_kitchen_order(doc)
     
def create_kitchen_order(doc):
    kitchen = frappe.get_doc({
        "doctype": "Kitchen Order",
        "kitchen_pos_invoice":doc.name,
        "status":"Received",
        "order_datetime": now_datetime(),
        "customer": doc.customer
    })

    kitchen.insert()

    frappe.publish_realtime(
        event="new_kitchen_order",
        message={
            "name":kitchen.name,
            "status":kitchen.status,
            "kitchen_pos_invoice": kitchen.kitchen_pos_invoice
        },
        after_commit=True
    )
    frappe.msgprint("New Kitchen Order Listed")


