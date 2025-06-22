import json
import csv

def safe_get(dct, keys, default=None):
    """Safely get nested dictionary keys."""
    for key in keys:
        if isinstance(dct, dict) and key in dct:
            dct = dct[key]
        else:
            return default
    return dct

# Load the JSON file
with open('roposo_clout.json', 'r') as f:
    all_data = json.load(f)

rows = []

for data in all_data.get("orderDetailsList", []):
    order_details = data.get("orderDetails", {})
    resell_suborders = data.get("resellSuborderDetailsList", [])
    resell = resell_suborders[0] if resell_suborders else {}
    dropshipping = resell.get("dropshippingMarginDetails", {})

    row = {
        "payment_mode": data.get("orderPaymentMode"),
        "id": order_details.get("orderId"),
        "created_at": order_details.get("orderTimestamp"),
        "customer_name": order_details.get("orderCustomerName"),
        "address": order_details.get("orderCustomerAddress"),
        "city": order_details.get("orderCustomerCity"),
        "pincode": order_details.get("orderCustomerPincode"),
        "phone": order_details.get("orderCustomerPhone"),
        "email": order_details.get("orderCustomerEmail"),
        "sub_order_id": resell.get("suborderId"),
        "product_id": resell.get("productId"),
        "product_name": resell.get("suborderProductName"),
        "quantity": resell.get("suborderQuantity"),
        "price": safe_get(resell, ["suborderPrice", "source"]),
        "status": resell.get("suborderStatus"),
        "coupon_discount": resell.get("couponDiscountPrice"),
        "credits_applied": resell.get("creditsApplied"),
        "delivered_date": resell.get("deliveredDate"),
        "last_return_date": resell.get("lastReturnDate"),
        "coupon_code": resell.get("couponCode"),
        "rto_risk_bucket": resell.get("rtoRiskBucket"),
        "cod_charge": resell.get("codCharge"),
        "shipping_charge": safe_get(resell, ["shippingCharge", "parsedValue"]),
        "thumbnail_url": resell.get("thumbnailUrl"),
        "mode_of_payment": resell.get("suborderModeOfPayment"),
        "online_payment_status": resell.get("onlinePaymentStatus"),
        "shipping_partner": resell.get("shippingPartner"),
        "tracking_number": resell.get("trackingNumber"),
        "tracking_url": resell.get("trackingUrl"),
        "reverse_shipping_partner": resell.get("reverseShippingPartner"),
        "reverse_tracking_number": resell.get("reverseTrackingNumber"),
        "reverse_tracking_url": resell.get("reverseTrackingUrl"),
        "pickup_date": resell.get("pickupDate"),
        "pickup_time_slot": resell.get("pickupTimeslot"),
        "pickup_address": resell.get("pickupAddress"),
        "pickup_pincode": resell.get("pickupPincode"),
        "wholesaler_store_name": resell.get("wholesellerStoreName"),
        "wholesaler_phone_number": resell.get("wholesellerPhoneNumber"),
        "selling_price": safe_get(dropshipping, ["sellingPrice", "source"]),
        "clout_price": safe_get(dropshipping, ["cloutPrice", "source"]),
        "margin": safe_get(dropshipping, ["margin", "source"]),
        "awb_status": resell.get("awbStatus"),
        "cancellation_stage": resell.get("cancellationStage"),
        "cancelled_by": resell.get("cancelledBy"),
        "cancellation_reason": resell.get("reasonOfCancellation"),
        "first_failed_delivery_date": resell.get("firstFailedDeliveryDate"),
        "rto_initiated": resell.get("rtoInitiated"),
        "ndr_reason": resell.get("ndrReason"),
        "ndr_timestamp": resell.get("ndrTimeStamp"),
        "ndr_attempt": resell.get("ndrAttempt"),
        "ndr_attempt_date": resell.get("nextAttemptDate"),
        "shopify_order_id": data.get("saasOrderId")
    }

    rows.append(row)

# Write to CSV
if rows:
    with open('orders_output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} rows written to orders_output.csv successfully.")
else:
    print("No data to write.")
