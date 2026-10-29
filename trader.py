import MetaTrader5 as mt5
import time
from config import MAGIC_NUMBER, LOT_SIZE, LIMIT_ORDER_EXPIRATION_HOURS

def has_open_or_pending_position(symbol, magic_number=MAGIC_NUMBER):
    """Ochiq bitimlar yoki kutayotgan limit buyurtmalar borligini tekshiradi."""
    # 1. Ochiq bitimlar
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for pos in positions:
            if pos.magic == magic_number:
                return True

    # 2. Kutib turgan Limit buyurtmalar
    orders = mt5.orders_get(symbol=symbol)
    if orders:
        for ord in orders:
            if ord.magic == magic_number:
                return True
                
    return False

def cancel_pending_orders(symbol, magic_number=MAGIC_NUMBER):
    """Eskirgan Limit buyurtmalarni tozalaydi."""
    orders = mt5.orders_get(symbol=symbol)
    if orders is None:
        return

    for ord in orders:
        if ord.magic == magic_number:
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": ord.ticket
            }
            mt5.order_send(request)

def place_limit_order(symbol, signal, entry_price, sl, tp, lot_size=LOT_SIZE, magic_number=MAGIC_NUMBER):
    """
    Bozor narxidan quvlab kirmay, qopqon (Limit Order) qo'yadi.
    2 soat ichida narx yetib kelmasa, avtomatik o'chib ketadi.
    """
    info = mt5.symbol_info(symbol)
    tick = mt5.symbol_info_tick(symbol)

    if info is None or tick is None:
        return False, f"Symbol ma'lumoti topilmadi: {symbol}"

    if not info.visible:
        mt5.symbol_select(symbol, True)

    if has_open_or_pending_position(symbol, magic_number):
        return False, f"Aktiv bitim yoki Limit order allaqachon mavjud."

    cancel_pending_orders(symbol, magic_number)

    if signal == "BUY":
        order_type = mt5.ORDER_TYPE_BUY_LIMIT
        if entry_price >= tick.ask:
            entry_price = round(tick.ask - 0.10, 2)
    elif signal == "SELL":
        order_type = mt5.ORDER_TYPE_SELL_LIMIT
        if entry_price <= tick.bid:
            entry_price = round(tick.bid + 0.10, 2)
    else:
        return False, f"Noto'g'ri signal: {signal}"

    expiration_time = int(time.time()) + (LIMIT_ORDER_EXPIRATION_HOURS * 3600)

    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": float(lot_size),
        "type": order_type,
        "price": float(entry_price),
        "sl": float(sl),
        "tp": float(tp),
        "deviation": 20,
        "magic": magic_number,
        "comment": "GoldSuperLimit",
        "type_time": mt5.ORDER_TIME_SPECIFIED,
        "expiration": expiration_time,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    result = mt5.order_send(request)
    if result is None:
        return False, "order_send None qaytardi"

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return False, f"Limit qo'yilmadi: {result.comment} (code {result.retcode})"

    return True, f"✅ LIMIT Order qo'yildi: #{result.order} | Kirish: {entry_price} | SL: {sl} | TP: {tp}"
