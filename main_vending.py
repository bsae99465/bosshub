import bosshub

client = bosshub.connect("API_KEY_HERExxxx")

def on_product_select(product_id):
    # 1. เช็คข้อมูลสินค้าและสต็อก Real-time
    info = client.get_product_info(product_id)
    
    if not info or info['stock'] <= 0:
        print("Out of Stock!")
        return

    print(f"Selected: {info['name']} Price: {info['price']}")
    
    # ... กระบวนการรับเงิน ...
    money_received = True 
    
    if money_received:
        # 2. จ่ายของ และ ตัดสต็อกบน Cloud ทันที
        dispense_item()
        client.report_sale(product_id, info['price'], "CASH")
        print("Thank you")

def dispense_item():
    # สั่ง Hardware มอเตอร์หมุน
    pass
