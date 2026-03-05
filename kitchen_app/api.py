import frappe
from frappe.utils import now_datetime


def handle_kitchen_order(doc, method):
    if not doc.is_pos and not doc.pos_profile:
        return

    pos_profile=frappe.get_doc("POS Profile", doc.pos_profile)

    print("handle_kitchen_order", pos_profile.custom_kitchen_device)

    if not pos_profile.enable_kitchen_app and not pos_profile.custom_kitchen_device:
        return

    create_kitchen_order(doc,pos_profile.custom_kitchen_device)


def create_kitchen_order(doc,kitchen_device_id=None):
    kitchen = frappe.get_doc(
        {
            "doctype": "Kitchen Order",
            "kitchen_pos_invoice": doc.name,
            "status": "Received",
            "order_datetime": now_datetime(),
            "customer": doc.customer,
            "device_id": kitchen_device_id,
        }
    )

    kitchen.insert()

    if kitchen_device_id is not None:
        frappe.publish_realtime(
            event=f"new_kitchen_order_{kitchen_device_id}",
            message={
                "name": kitchen.name,
                "status": kitchen.status,
                "kitchen_pos_invoice": kitchen.kitchen_pos_invoice,
            },
            after_commit=True,
        )
    frappe.msgprint("New Kitchen Order Listed")


@frappe.whitelist()
def get_pos_invoice_print_url(invoice_name, print_format=None):
    from frappe.utils import get_url

    doctype = "POS Invoice"
    format_name = print_format or "Kitchen Order Ticket"
    relative_url = (
        f"/printview?doctype={doctype}"
        f"&name={invoice_name}"
        f"&trigger_print=1"
        f"&format={format_name}"
        "&no_letterhead=1&_lang=en"
    )
    return get_url(relative_url)

