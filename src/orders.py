def calculate_order_total(order):
    total = 0

    for item in order["items"]:
        price = item["price"]
        quantity = item["qty"]

        if price > 0 and quantity > 0:
            total += price * quantity

    if order["member"]:
        if total > 100:
            discount = total * 0.2
        elif total > 50:
            discount = total * 0.1
        else:
            discount = 0
    else:
        discount = 0

    total -= discount

    if order["country"] == "PK":
        shipping = 5
    elif order["country"] == "US":
        shipping = 15
    else:
        shipping = 25

    total += shipping

    print("Total: " + str(total))

    return total

sample_order = {
    "items": [
        {"price": 25.0, "qty": 2},
        {"price": 40.0, "qty": 1},
        {"price": -5.0, "qty": 3},
    ],
    "member": True,
    "country": "PK",
}

calculate_order_total(sample_order)