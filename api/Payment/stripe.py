from flask import Blueprint, request, jsonify
import stripe
import os

stripe_payment_bp = Blueprint('stripe_payment', __name__)

# Configura la clau secreta de Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@stripe_payment_bp.route('/payment', methods=['POST'])
def create_payment_intent():
    try:
        data = request.json
        print(f"[DEBUG] Rebut pagament: {data}")
        amount = data.get('amount')
        if amount is None or float(amount) <= 0:
            return jsonify(error="L'import ha de ser superior a 0 per a processar un pagament amb Stripe"), 400

        currency = data.get('currency', 'eur')
        plan_id = data.get('planId')

        # Crea un PaymentIntent amb l'import i la moneda
        intent = stripe.PaymentIntent.create(
            amount=int(round(float(amount) * 100)), # Stripe usa cèntims. Round per evitar problemes decimals.
            currency=currency,
            automatic_payment_methods={
                'enabled': True,
            },
            metadata={
                'plan_id': plan_id
            }
        )

        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        print(f"[ERROR] Stripe: {str(e)}")
        return jsonify(error=str(e)), 403

@stripe_payment_bp.route('/api/payment/webhook', methods=['POST'])
def stripe_webhook():
    # Opcional: Implementar webhooks per a confirmar el pagament al backend de forma segura
    return jsonify(success=True)
