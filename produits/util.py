def calculate_payment_amount(order, partial=False):
    """
    Calcule le montant à payer pour une commande.
    :param order: Instance de la commande.
    :param partial: True pour paiement partiel (35 %).
    :return: Montant à payer.
    """
    total_amount = sum(item.total_price for item in order.items.all())
    return round(total_amount * 0.35, 2) if partial else total_amount